"""File copying functionality for media files."""

import shutil
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from ..utils.logger import get_logger
from ..utils.config import Config
from .file_searcher import FileSearchResult

logger = get_logger(__name__)


@dataclass
class CopyResult:
    """Result of a file copy operation."""
    source_path: Path
    destination_path: Path
    success: bool
    error_message: Optional[str] = None
    bytes_copied: int = 0
    skipped: bool = False
    skip_reason: Optional[str] = None


class FileCopier:
    """Handles copying of media files to output directory."""
    
    def __init__(self, config: Config):
        """
        Initialize the file copier.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.copy_results: List[CopyResult] = []
    
    def copy_files(
        self, 
        search_results: Dict[str, List[FileSearchResult]], 
        output_folder: Path
    ) -> List[CopyResult]:
        """
        Copy found files to the output folder.
        
        Args:
            search_results: Dictionary of search results from FileSearcher
            output_folder: Destination directory for copied files
            
        Returns:
            List of copy results
        """
        # Create output folder if it doesn't exist
        output_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"Copying files to: {output_folder}")
        
        self.copy_results = []
        total_files = sum(len(results) for results in search_results.values())
        
        if total_files == 0:
            logger.warning("No files to copy")
            return self.copy_results
        
        logger.info(f"Starting copy operation for {total_files} files")
        
        copied_count = 0
        skipped_count = 0
        error_count = 0
        
        for target_filename, file_results in search_results.items():
            if not file_results:
                logger.debug(f"No matches found for: {target_filename}")
                continue
            
            # Handle multiple matches for the same target filename
            for i, file_result in enumerate(file_results):
                destination_path = self._get_destination_path(
                    file_result, output_folder, target_filename, i
                )
                
                copy_result = self._copy_single_file(file_result.full_path, destination_path)
                self.copy_results.append(copy_result)
                
                if copy_result.success:
                    copied_count += 1
                elif copy_result.skipped:
                    skipped_count += 1
                else:
                    error_count += 1
        
        logger.info(f"Copy operation completed: {copied_count} copied, {skipped_count} skipped, {error_count} errors")
        return self.copy_results
    
    def copy_unique_files(
        self, 
        file_results: List[FileSearchResult], 
        output_folder: Path
    ) -> List[CopyResult]:
        """
        Copy a list of unique files to the output folder.
        
        Args:
            file_results: List of file search results
            output_folder: Destination directory for copied files
            
        Returns:
            List of copy results
        """
        # Create output folder if it doesn't exist
        output_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"Copying {len(file_results)} unique files to: {output_folder}")
        
        self.copy_results = []
        copied_count = 0
        skipped_count = 0
        error_count = 0
        
        for file_result in file_results:
            destination_path = self._get_destination_path(file_result, output_folder)
            
            copy_result = self._copy_single_file(file_result.full_path, destination_path)
            self.copy_results.append(copy_result)
            
            if copy_result.success:
                copied_count += 1
            elif copy_result.skipped:
                skipped_count += 1
            else:
                error_count += 1
        
        logger.info(f"Unique copy operation completed: {copied_count} copied, {skipped_count} skipped, {error_count} errors")
        return self.copy_results
    
    def _get_destination_path(
        self, 
        file_result: FileSearchResult, 
        output_folder: Path, 
        target_filename: Optional[str] = None,
        duplicate_index: int = 0
    ) -> Path:
        """
        Get the destination path for a file.
        
        Args:
            file_result: File search result
            output_folder: Output directory
            target_filename: Target filename (for renaming)
            duplicate_index: Index for handling duplicates
            
        Returns:
            Destination path for the file
        """
        if self.config.maintain_structure:
            # Maintain relative directory structure
            # This would require knowing the original search root, so for now use filename only
            destination_path = output_folder / file_result.filename
        else:
            # Use original filename or target filename
            filename = target_filename if target_filename else file_result.filename
            
            # Handle duplicates by adding index
            if duplicate_index > 0:
                stem = Path(filename).stem
                suffix = Path(filename).suffix
                filename = f"{stem}_{duplicate_index}{suffix}"
            
            destination_path = output_folder / filename
        
        return destination_path
    
    def _copy_single_file(self, source_path: Path, destination_path: Path) -> CopyResult:
        """
        Copy a single file from source to destination.
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            Copy result
        """
        try:
            # Check if source file exists
            if not source_path.exists():
                return CopyResult(
                    source_path=source_path,
                    destination_path=destination_path,
                    success=False,
                    error_message="Source file does not exist"
                )
            
            # Check if destination already exists
            if destination_path.exists():
                if not self.config.overwrite_existing:
                    return CopyResult(
                        source_path=source_path,
                        destination_path=destination_path,
                        success=False,
                        skipped=True,
                        skip_reason="Destination file already exists and overwrite is disabled"
                    )
                else:
                    logger.debug(f"Overwriting existing file: {destination_path}")
            
            # Create destination directory if needed
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Get file size for progress tracking
            file_size = source_path.stat().st_size
            
            # Copy the file
            shutil.copy2(source_path, destination_path)
            
            logger.debug(f"Copied: {source_path} -> {destination_path}")
            
            return CopyResult(
                source_path=source_path,
                destination_path=destination_path,
                success=True,
                bytes_copied=file_size
            )
            
        except PermissionError as e:
            error_msg = f"Permission denied: {e}"
            logger.error(f"Failed to copy {source_path}: {error_msg}")
            return CopyResult(
                source_path=source_path,
                destination_path=destination_path,
                success=False,
                error_message=error_msg
            )
        
        except OSError as e:
            error_msg = f"OS error: {e}"
            logger.error(f"Failed to copy {source_path}: {error_msg}")
            return CopyResult(
                source_path=source_path,
                destination_path=destination_path,
                success=False,
                error_message=error_msg
            )
        
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(f"Failed to copy {source_path}: {error_msg}")
            return CopyResult(
                source_path=source_path,
                destination_path=destination_path,
                success=False,
                error_message=error_msg
            )
    
    def get_copy_results(self) -> List[CopyResult]:
        """
        Get the results of the last copy operation.
        
        Returns:
            List of copy results
        """
        return self.copy_results.copy()
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get copy operation statistics.
        
        Returns:
            Dictionary with copy statistics
        """
        successful = sum(1 for result in self.copy_results if result.success)
        skipped = sum(1 for result in self.copy_results if result.skipped)
        errors = sum(1 for result in self.copy_results if not result.success and not result.skipped)
        total_bytes = sum(result.bytes_copied for result in self.copy_results if result.success)
        
        return {
            'total_files': len(self.copy_results),
            'successful': successful,
            'skipped': skipped,
            'errors': errors,
            'total_bytes_copied': total_bytes
        }
    
    def clean_output_folder(self, output_folder: Path, expected_filenames: List[str]) -> List[Path]:
        """
        Remove files from output folder that are not in the expected filenames list.
        
        Args:
            output_folder: Output directory to clean
            expected_filenames: List of filenames that should remain in the folder
            
        Returns:
            List of files that were removed
        """
        if not output_folder.exists():
            logger.info("Output folder doesn't exist, nothing to clean")
            return []
        
        logger.info(f"Cleaning output folder: {output_folder}")
        
        # Get all media files currently in the output folder
        existing_files = []
        for file_path in output_folder.iterdir():
            if file_path.is_file() and self._has_supported_extension(file_path.name):
                existing_files.append(file_path)
        
        # Determine which files should be removed
        expected_set = set(expected_filenames)
        files_to_remove = []
        
        for file_path in existing_files:
            if file_path.name not in expected_set:
                files_to_remove.append(file_path)
        
        logger.info(f"Found {len(existing_files)} media files in output folder")
        logger.info(f"Expected {len(expected_filenames)} files from playlist")
        logger.info(f"Will remove {len(files_to_remove)} files not in playlist")
        
        # Remove the files
        removed_files = []
        for file_path in files_to_remove:
            try:
                file_path.unlink()
                removed_files.append(file_path)
                logger.info(f"Removed: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to remove {file_path}: {e}")
        
        logger.info(f"Successfully removed {len(removed_files)} files")
        return removed_files
    
    def _has_supported_extension(self, filename: str) -> bool:
        """
        Check if filename has a supported extension.
        
        Args:
            filename: Filename to check
            
        Returns:
            True if filename has supported extension
        """
        if not filename:
            return False
        
        filename_lower = filename.lower()
        for ext in self.config.supported_extensions:
            if filename_lower.endswith(ext.lower()):
                return True
        
        return False

    def generate_report(self) -> str:
        """
        Generate a text report of the copy operation.
        
        Returns:
            Formatted report string
        """
        stats = self.get_statistics()
        
        report_lines = [
            "=== File Copy Report ===",
            f"Total files processed: {stats['total_files']}",
            f"Successfully copied: {stats['successful']}",
            f"Skipped: {stats['skipped']}",
            f"Errors: {stats['errors']}",
            f"Total bytes copied: {stats['total_bytes_copied']:,} bytes",
            ""
        ]
        
        if stats['errors'] > 0:
            report_lines.append("=== Errors ===")
            for result in self.copy_results:
                if not result.success and not result.skipped:
                    report_lines.append(f"ERROR: {result.source_path} - {result.error_message}")
            report_lines.append("")
        
        if stats['skipped'] > 0:
            report_lines.append("=== Skipped Files ===")
            for result in self.copy_results:
                if result.skipped:
                    report_lines.append(f"SKIPPED: {result.source_path} - {result.skip_reason}")
            report_lines.append("")
        
        return "\n".join(report_lines)
