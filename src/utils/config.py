"""Configuration management for the application."""

import configparser
from pathlib import Path
from typing import List, Optional

from .logger import get_logger

logger = get_logger(__name__)


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (defaults to settings.ini)
        """
        self.config = configparser.ConfigParser()
        
        if config_file is None:
            config_file = Path("settings.ini")
        
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                self.config.read(self.config_file)
                logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                self._load_defaults()
        else:
            logger.warning(f"Configuration file {self.config_file} not found, using defaults")
            self._load_defaults()
    
    def _load_defaults(self) -> None:
        """Load default configuration values."""
        self.config.read_dict({
            'DEFAULT': {
                'supported_extensions': '.mp4,.mkv,.avi,.mov,.wmv,.flv,.webm,.m4v,.mp3,.wav,.flac,.aac,.ogg,.m4a',
                'case_sensitive': 'false',
                'overwrite_existing': 'false',
                'maintain_structure': 'false',
                'log_level': 'INFO'
            },
            'PARSER': {
                'timeout': '5',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            'SEARCH': {
                'recursive_search': 'true',
                'follow_symlinks': 'false'
            }
        })
    
    @property
    def supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        extensions_str = self.config.get('DEFAULT', 'supported_extensions')
        return [ext.strip() for ext in extensions_str.split(',')]
    
    @property
    def case_sensitive(self) -> bool:
        """Get case sensitivity setting."""
        return self.config.getboolean('DEFAULT', 'case_sensitive')
    
    @property
    def overwrite_existing(self) -> bool:
        """Get overwrite existing files setting."""
        return self.config.getboolean('DEFAULT', 'overwrite_existing')
    
    @property
    def maintain_structure(self) -> bool:
        """Get maintain directory structure setting."""
        return self.config.getboolean('DEFAULT', 'maintain_structure')
    
    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self.config.get('DEFAULT', 'log_level')
    
    @property
    def parser_timeout(self) -> int:
        """Get parser timeout setting."""
        return self.config.getint('PARSER', 'timeout')
    
    @property
    def user_agent(self) -> str:
        """Get user agent string."""
        return self.config.get('PARSER', 'user_agent')
    
    @property
    def recursive_search(self) -> bool:
        """Get recursive search setting."""
        return self.config.getboolean('SEARCH', 'recursive_search')
    
    @property
    def follow_symlinks(self) -> bool:
        """Get follow symlinks setting."""
        return self.config.getboolean('SEARCH', 'follow_symlinks')
