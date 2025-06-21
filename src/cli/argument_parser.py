"""Command line argument parsing and main application logic."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from ..utils.logger import setup_logger, get_logger
from ..utils.config import Config
from ..core.playlist_parser import PlaylistParser
from ..core.file_searcher import FileSearcher
from ..core.file_copier import FileCopier


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Extract media files from M3U8 playlists and copy them from a media folder to an output folder.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --playlist my_playlist.m3u8 --mediafolder /path/to/media --outputfolder /path/to/output
  %(prog)s --playlist playlist.m3u8 --mediafolder C:\\Media --outputfolder C:\\Output --config custom_settings.ini
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--playlist",
        type=str,
        required=True,
        help="Path to the M3U8 playlist file"
    )
    
    parser.add_argument(
        "--mediafolder",
        type=str,
        required=True,
        help="Path to the folder containing media files (will search recursively)"
    )
    
    parser.add_argument(
        "--outputfolder",
        type=str,
        required=True,
        help="Path to the output folder where matched files will be copied"
    )
    
    # Optional arguments
    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom configuration file (default: settings.ini)"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (overrides config file setting)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file (optional)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be copied without actually copying files"
    )
    
    parser.add_argument(
        "--report",
        type=str,
        help="Path to save a detailed report of the operation"
    )
    
    parser.add_argument(
        "--clean-output",
        action="store_true",
        help="Remove files from output folder that are not in the current playlist"
    )
    
    return parser


def validate_arguments(args: argparse.Namespace) -> bool:
    """
    Validate command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        True if arguments are valid, False otherwise
    """
    errors = []
    
    # Check playlist file
    playlist_path = Path(args.playlist)
    if not playlist_path.exists():
        errors.append(f"Playlist file does not exist: {playlist_path}")
    elif not playlist_path.is_file():
        errors.append(f"Playlist path is not a file: {playlist_path}")
    
    # Check media folder
    media_folder = Path(args.mediafolder)
    if not media_folder.exists():
        errors.append(f"Media folder does not exist: {media_folder}")
    elif not media_folder.is_dir():
        errors.append(f"Media folder path is not a directory: {media_folder}")
    
    # Check output folder parent (output folder itself will be created if needed)
    output_folder = Path(args.outputfolder)
    if output_folder.exists() and not output_folder.is_dir():
        errors.append(f"Output folder path exists but is not a directory: {output_folder}")
    elif not output_folder.parent.exists():
        errors.append(f"Output folder parent directory does not exist: {output_folder.parent}")
    
    # Check config file if provided
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            errors.append(f"Configuration file does not exist: {config_path}")
        elif not config_path.is_file():
            errors.append(f"Configuration path is not a file: {config_path}")
    
    # Print errors if any
    if errors:
        print("Validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return False
    
    return True


def run_application(args: argparse.Namespace) -> int:
    """
    Run the main application logic.
    
    Args:
        args: Parsed and validated command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Load configuration
        config_file = Path(args.config) if args.config else None
        config = Config(config_file)
        
        # Set up logging
        log_level = args.log_level if args.log_level else config.log_level
        log_file = Path(args.log_file) if args.log_file else None
        logger = setup_logger(level=log_level, log_file=log_file)
        
        logger.info("=== M3U8 to Folder - Starting ===")
        logger.info(f"Playlist: {args.playlist}")
        logger.info(f"Media folder: {args.mediafolder}")
        logger.info(f"Output folder: {args.outputfolder}")
        
        if args.dry_run:
            logger.info("DRY RUN MODE - No files will be copied")
        
        if args.clean_output:
            logger.info("CLEAN OUTPUT MODE - Files not in playlist will be removed")
        
        # Convert paths
        playlist_path = Path(args.playlist)
        media_folder = Path(args.mediafolder)
        output_folder = Path(args.outputfolder)
        
        # Step 1: Parse playlist
        logger.info("Step 1: Parsing M3U8 playlist")
        playlist_parser = PlaylistParser(config)
        media_files = playlist_parser.parse_playlist(playlist_path)
        
        if not media_files:
            logger.warning("No media files found in playlist")
            return 1
        
        logger.info(f"Found {len(media_files)} media files in playlist")
        
        # Step 2: Search for files
        logger.info("Step 2: Searching for files in media folder")
        file_searcher = FileSearcher(config)
        search_results = file_searcher.search_files(media_folder, media_files)
        
        # Get statistics
        search_stats = file_searcher.get_statistics()
        logger.info(f"Search results: {search_stats['total_matches']} matches for {search_stats['files_with_matches']}/{search_stats['target_files']} files")
        
        if search_stats['total_matches'] == 0:
            logger.warning("No matching files found in media folder")
            return 1
        
        # Step 3: Copy files (or dry run)
        if args.dry_run:
            logger.info("Step 3: DRY RUN - Files that would be copied:")
            unique_files = file_searcher.get_unique_matches()
            for file_result in unique_files:
                logger.info(f"  WOULD COPY: {file_result.full_path}")
            logger.info(f"Total files that would be copied: {len(unique_files)}")
            
            # Step 4: Show cleanup preview if requested
            if args.clean_output:
                logger.info("Step 4: DRY RUN - Files that would be removed from output folder:")
                file_copier = FileCopier(config)
                expected_filenames = [file_result.filename for file_result in unique_files]
                
                if output_folder.exists():
                    # Preview cleanup without actually removing files
                    existing_files = []
                    for file_path in output_folder.iterdir():
                        if file_path.is_file() and file_copier._has_supported_extension(file_path.name):
                            existing_files.append(file_path)
                    
                    expected_set = set(expected_filenames)
                    files_to_remove = [f for f in existing_files if f.name not in expected_set]
                    
                    if files_to_remove:
                        for file_path in files_to_remove:
                            logger.info(f"  WOULD REMOVE: {file_path}")
                        logger.info(f"Total files that would be removed: {len(files_to_remove)}")
                    else:
                        logger.info("  No files would be removed")
                else:
                    logger.info("  Output folder doesn't exist, nothing to clean")
        else:
            logger.info("Step 3: Copying files to output folder")
            file_copier = FileCopier(config)
            # Use unique files to avoid copying the same file multiple times
            unique_files = file_searcher.get_unique_matches()
            copy_results = file_copier.copy_unique_files(unique_files, output_folder)
            
            # Get copy statistics
            copy_stats = file_copier.get_statistics()
            logger.info(f"Copy results: {copy_stats['successful']} successful, {copy_stats['skipped']} skipped, {copy_stats['errors']} errors")
            
            # Step 4: Clean output folder if requested
            if args.clean_output:
                logger.info("Step 4: Cleaning output folder")
                # Get the filenames that should be in the output folder
                expected_filenames = [file_result.filename for file_result in unique_files]
                removed_files = file_copier.clean_output_folder(output_folder, expected_filenames)
                logger.info(f"Cleanup completed: {len(removed_files)} files removed")
            
            # Generate and save report if requested
            if args.report:
                report_content = file_copier.generate_report()
                report_path = Path(args.report)
                report_path.write_text(report_content, encoding='utf-8')
                logger.info(f"Report saved to: {report_path}")
            
            # Return error code if there were copy errors
            if copy_stats['errors'] > 0:
                logger.error(f"Operation completed with {copy_stats['errors']} errors")
                return 2
        
        logger.info("=== M3U8 to Folder - Completed Successfully ===")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


def main() -> None:
    """Main entry point for the application."""
    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Validate arguments
    if not validate_arguments(args):
        sys.exit(1)
    
    # Run application
    exit_code = run_application(args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
