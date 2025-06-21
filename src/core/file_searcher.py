"""File searching functionality for media files."""

from pathlib import Path
from typing import Dict, List, Set
import fnmatch

from ..utils.logger import get_logger
from ..utils.config import Config

logger = get_logger(__name__)


class FileSearchResult:
    """Result of a file search operation."""
    
    def __init__(self, filename: str, full_path: Path):
        """
        Initialize search result.
        
        Args:
            filename: Name of the file
            full_path: Full path to the file
        """
        self.filename = filename
        self.full_path = full_path
        self.size = full_path.stat().st_size if full_path.exists() else 0
    
    def __str__(self) -> str:
        return f"{self.filename} -> {self.full_path}"
    
    def __repr__(self) -> str:
        return f"FileSearchResult(filename='{self.filename}', full_path='{self.full_path}')"


class FileSearcher:
    """Searches for media files in directory structures."""
    
    def __init__(self, config: Config):
        """
        Initialize the file searcher.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.found_files: Dict[str, List[FileSearchResult]] = {}
    
    def search_files(self, media_folder: Path, target_filenames: List[str]) -> Dict[str, List[FileSearchResult]]:
        """
        Search for target files in the media folder.
        
        Args:
            media_folder: Root directory to search in
            target_filenames: List of filenames to search for
            
        Returns:
            Dictionary mapping filenames to list of found file results
            
        Raises:
            FileNotFoundError: If media folder doesn't exist
        """
        if not media_folder.exists():
            raise FileNotFoundError(f"Media folder not found: {media_folder}")
        
        if not media_folder.is_dir():
            raise NotADirectoryError(f"Media folder is not a directory: {media_folder}")
        
        logger.info(f"Searching for {len(target_filenames)} files in: {media_folder}")
        
        # Initialize results dictionary
        self.found_files = {filename: [] for filename in target_filenames}
        
        # Create sets for efficient lookup
        target_set = set(target_filenames)
        if not self.config.case_sensitive:
            target_set_lower = {filename.lower() for filename in target_filenames}
        
        # Search files
        files_searched = 0
        for file_path in self._iterate_files(media_folder):
            files_searched += 1
            
            if files_searched % 1000 == 0:
                logger.debug(f"Searched {files_searched} files...")
            
            filename = file_path.name
            
            # Check for exact matches
            if self.config.case_sensitive:
                if filename in target_set:
                    result = FileSearchResult(filename, file_path)
                    self.found_files[filename].append(result)
            else:
                filename_lower = filename.lower()
                for target_filename in target_filenames:
                    if filename_lower == target_filename.lower():
                        result = FileSearchResult(target_filename, file_path)
                        self.found_files[target_filename].append(result)
                        break
        
        # Log results
        total_found = sum(len(results) for results in self.found_files.values())
        files_with_matches = sum(1 for results in self.found_files.values() if results)
        
        logger.info(f"Search completed: {files_searched} files searched")
        logger.info(f"Found {total_found} matches for {files_with_matches}/{len(target_filenames)} target files")
        
        return self.found_files
    
    def _iterate_files(self, directory: Path):
        """
        Iterate through files in directory.
        
        Args:
            directory: Directory to iterate through
            
        Yields:
            Path objects for each file found
        """
        try:
            if self.config.recursive_search:
                # Recursive search
                for item in directory.rglob('*'):
                    if item.is_file():
                        # Check if we should follow symlinks
                        if not self.config.follow_symlinks and item.is_symlink():
                            continue
                        
                        # Check if file has supported extension
                        if self._has_supported_extension(item.name):
                            yield item
            else:
                # Non-recursive search
                for item in directory.iterdir():
                    if item.is_file():
                        # Check if we should follow symlinks
                        if not self.config.follow_symlinks and item.is_symlink():
                            continue
                        
                        # Check if file has supported extension
                        if self._has_supported_extension(item.name):
                            yield item
        except PermissionError as e:
            logger.warning(f"Permission denied accessing directory: {directory} - {e}")
        except Exception as e:
            logger.error(f"Error iterating directory {directory}: {e}")
    
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
    
    def search_with_patterns(self, media_folder: Path, patterns: List[str]) -> Dict[str, List[FileSearchResult]]:
        """
        Search for files using wildcard patterns.
        
        Args:
            media_folder: Root directory to search in
            patterns: List of wildcard patterns to match (e.g., ['*.mp4', 'video_*.mkv'])
            
        Returns:
            Dictionary mapping patterns to list of found file results
        """
        if not media_folder.exists():
            raise FileNotFoundError(f"Media folder not found: {media_folder}")
        
        logger.info(f"Searching with {len(patterns)} patterns in: {media_folder}")
        
        results = {pattern: [] for pattern in patterns}
        files_searched = 0
        
        for file_path in self._iterate_files(media_folder):
            files_searched += 1
            filename = file_path.name
            
            for pattern in patterns:
                if self.config.case_sensitive:
                    if fnmatch.fnmatch(filename, pattern):
                        result = FileSearchResult(filename, file_path)
                        results[pattern].append(result)
                else:
                    if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                        result = FileSearchResult(filename, file_path)
                        results[pattern].append(result)
        
        total_found = sum(len(file_list) for file_list in results.values())
        logger.info(f"Pattern search completed: {total_found} matches found from {files_searched} files")
        
        return results
    
    def get_found_files(self) -> Dict[str, List[FileSearchResult]]:
        """
        Get the results of the last search operation.
        
        Returns:
            Dictionary of found files
        """
        return self.found_files.copy()
    
    def get_unique_matches(self) -> List[FileSearchResult]:
        """
        Get a list of unique file matches (removes duplicates by path).
        
        Returns:
            List of unique file search results
        """
        seen_paths: Set[Path] = set()
        unique_results = []
        
        for results_list in self.found_files.values():
            for result in results_list:
                if result.full_path not in seen_paths:
                    seen_paths.add(result.full_path)
                    unique_results.append(result)
        
        return unique_results
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get search statistics.
        
        Returns:
            Dictionary with search statistics
        """
        total_matches = sum(len(results) for results in self.found_files.values())
        files_with_matches = sum(1 for results in self.found_files.values() if results)
        unique_files = len(self.get_unique_matches())
        
        return {
            'total_matches': total_matches,
            'files_with_matches': files_with_matches,
            'target_files': len(self.found_files),
            'unique_files': unique_files
        }
