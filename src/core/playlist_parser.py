"""M3U8 playlist parsing functionality."""

from pathlib import Path
from typing import List, Optional
import m3u8

from ..utils.logger import get_logger
from ..utils.config import Config

logger = get_logger(__name__)


class PlaylistParser:
    """Parser for M3U8 playlist files."""
    
    def __init__(self, config: Config):
        """
        Initialize the playlist parser.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.media_files: List[str] = []
    
    def parse_playlist(self, playlist_path: Path) -> List[str]:
        """
        Parse M3U8 playlist and extract media file names.
        
        Args:
            playlist_path: Path to the M3U8 playlist file
            
        Returns:
            List of media file names found in the playlist
            
        Raises:
            FileNotFoundError: If playlist file doesn't exist
            Exception: If parsing fails
        """
        if not playlist_path.exists():
            raise FileNotFoundError(f"Playlist file not found: {playlist_path}")
        
        logger.info(f"Parsing playlist: {playlist_path}")
        
        try:
            # Parse the M3U8 file using m3u8 library
            # Read file content and parse with loads() to avoid URL interpretation issues
            with open(playlist_path, 'r', encoding='utf-8') as f:
                content = f.read()
            playlist = m3u8.loads(content)
            
            logger.info(f"Found {len(playlist.segments)} segments in playlist")
            
            # Extract media file names from segments
            self.media_files = []
            for segment in playlist.segments:
                if segment.uri:
                    filename = self._extract_filename(segment.uri)
                    if filename:
                        self.media_files.append(filename)
            
            # Remove duplicates while preserving order
            self.media_files = list(dict.fromkeys(self.media_files))
            
            logger.info(f"Extracted {len(self.media_files)} unique media file names")
            
            return self.media_files
            
        except Exception as e:
            logger.error(f"Failed to parse playlist {playlist_path}: {e}")
            raise
    
    def _extract_filename(self, text: str) -> Optional[str]:
        """
        Extract filename from text (URL, path, or title).
        
        Args:
            text: Text to extract filename from
            
        Returns:
            Extracted filename or None if not found
        """
        if not text:
            return None
        
        # Handle URLs - extract filename from path
        if text.startswith(('http://', 'https://', 'ftp://')):
            try:
                from urllib.parse import urlparse
                parsed = urlparse(text)
                filename = Path(parsed.path).name
                if filename and self._has_supported_extension(filename):
                    return filename
            except Exception:
                pass
        
        # Handle file paths
        try:
            path = Path(text)
            filename = path.name
            if filename and self._has_supported_extension(filename):
                return filename
        except Exception:
            pass
        
        # Handle plain filenames
        if self._has_supported_extension(text):
            return text
        
        return None
    
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
    
    def get_media_files(self) -> List[str]:
        """
        Get the list of extracted media files.
        
        Returns:
            List of media file names
        """
        return self.media_files.copy()
    
    def filter_by_extension(self, extensions: List[str]) -> List[str]:
        """
        Filter media files by specific extensions.
        
        Args:
            extensions: List of extensions to filter by (e.g., ['.mp4', '.mkv'])
            
        Returns:
            Filtered list of media files
        """
        filtered_files = []
        extensions_lower = [ext.lower() for ext in extensions]
        
        for filename in self.media_files:
            filename_lower = filename.lower()
            for ext in extensions_lower:
                if filename_lower.endswith(ext):
                    filtered_files.append(filename)
                    break
        
        logger.info(f"Filtered to {len(filtered_files)} files with extensions: {extensions}")
        return filtered_files
