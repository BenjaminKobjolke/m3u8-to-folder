# M3U8 to Folder

A Python tool that extracts media file names from M3U8 playlists and copies matching files from a media directory to an output folder.

## Features

-   **M3U8 Playlist Parsing**: Extracts media file references from M3U8 playlist files
-   **Recursive File Search**: Searches through media folders and subfolders for matching files
-   **Flexible File Matching**: Supports various audio and video formats
-   **Safe File Operations**: Configurable overwrite protection and error handling
-   **Detailed Logging**: Comprehensive logging with configurable levels
-   **Dry Run Mode**: Preview what files would be copied without actually copying them
-   **Progress Reporting**: Generate detailed reports of copy operations
-   **Windows Batch Scripts**: Easy setup and execution on Windows

## Supported File Formats

**Video**: `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v`  
**Audio**: `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.m4a`

## Installation

### Prerequisites

-   Python 3.7 or higher
-   Windows (batch scripts provided) or any OS with Python support

### Quick Setup (Windows)

1. Clone or download this repository
2. Run `install.bat` to set up the virtual environment and install dependencies
3. Use `run.bat` to execute the application

### Manual Setup

1. Create a virtual environment:

    ```bash
    python -m venv venv
    ```

2. Activate the virtual environment:

    - Windows: `venv\Scripts\activate`
    - Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Basic Usage

```bash
python main.py --playlist playlist.m3u8 --mediafolder /path/to/media --outputfolder /path/to/output
```

### Windows Batch Script Usage

```cmd
run.bat --playlist playlist.m3u8 --mediafolder C:\Media --outputfolder C:\Output
```

### Command Line Arguments

#### Required Arguments

-   `--playlist`: Path to the M3U8 playlist file
-   `--mediafolder`: Path to the folder containing media files (searches recursively)
-   `--outputfolder`: Path to the output folder where matched files will be copied

#### Optional Arguments

-   `--config`: Path to custom configuration file (default: `settings.ini`)
-   `--log-level`: Set logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
-   `--log-file`: Path to save log output to a file
-   `--dry-run`: Show what would be copied without actually copying files
-   `--report`: Path to save a detailed operation report
-   `--clean-output`: Remove files from output folder that are not in the current playlist
-   `--help`: Show help message and exit

### Examples

#### Basic file copying:

```bash
python main.py --playlist my_music.m3u8 --mediafolder C:\Music --outputfolder C:\Playlist_Output
```

#### Dry run to preview operations:

```bash
python main.py --playlist videos.m3u8 --mediafolder /media/videos --outputfolder /output --dry-run
```

#### With detailed logging and report:

```bash
python main.py --playlist playlist.m3u8 --mediafolder C:\Media --outputfolder C:\Output --log-level DEBUG --log-file operation.log --report report.txt
```

#### Clean output folder (remove files not in playlist):

```bash
python main.py --playlist playlist.m3u8 --mediafolder C:\Media --outputfolder C:\Output --clean-output
```

#### Preview cleanup with dry run:

```bash
python main.py --playlist playlist.m3u8 --mediafolder C:\Media --outputfolder C:\Output --clean-output --dry-run
```

## Configuration

The application uses a `settings.ini` file for configuration. You can customize various settings:

```ini
[DEFAULT]
# Supported file extensions
supported_extensions = .mp4,.mkv,.avi,.mov,.wmv,.flv,.webm,.m4v,.mp3,.wav,.flac,.aac,.ogg,.m4a
# Case sensitive filename matching
case_sensitive = false
# Overwrite existing files in output folder
overwrite_existing = false
# Maintain directory structure (not fully implemented)
maintain_structure = false
# Default logging level
log_level = INFO

[PARSER]
# Timeout for remote M3U8 URLs (seconds)
timeout = 5
# User agent for HTTP requests
user_agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

[SEARCH]
# Search recursively through subdirectories
recursive_search = true
# Follow symbolic links during search
follow_symlinks = false
```

## Project Structure

```
m3u8-to-folder/
├── main.py                     # Entry point
├── src/
│   ├── cli/
│   │   └── argument_parser.py  # Command line interface
│   ├── core/
│   │   ├── playlist_parser.py  # M3U8 parsing logic
│   │   ├── file_searcher.py    # File searching functionality
│   │   └── file_copier.py      # File copying operations
│   └── utils/
│       ├── logger.py           # Logging configuration
│       └── config.py           # Configuration management
├── settings.ini                # Configuration file
├── requirements.txt            # Python dependencies
├── install.bat                 # Windows installation script
├── run.bat                     # Windows run script
└── activate_environment.bat    # Windows environment activation
```

## How It Works

1. **Parse M3U8 Playlist**: The application reads the M3U8 file and extracts media file references
2. **Search Media Folder**: Recursively searches the specified media folder for files matching the playlist entries
3. **Copy Files**: Copies found files to the output folder with configurable options for handling duplicates and errors

## Error Handling

The application includes comprehensive error handling:

-   **File Validation**: Checks that input files and directories exist
-   **Permission Handling**: Gracefully handles permission errors
-   **Duplicate Management**: Configurable behavior for existing files
-   **Detailed Logging**: All operations are logged with appropriate levels
-   **Exit Codes**: Returns appropriate exit codes for scripting integration

## Exit Codes

-   `0`: Success
-   `1`: General error (file not found, parsing error, etc.)
-   `2`: Copy operation completed with errors
-   `130`: Operation cancelled by user (Ctrl+C)

## Troubleshooting

### Common Issues

1. **"Virtual environment not found"**: Run `install.bat` first
2. **"Python not found"**: Install Python 3.7+ and ensure it's in your PATH
3. **"No files found in playlist"**: Check that your M3U8 file contains valid media references
4. **"No matching files found"**: Verify that your media folder contains files with names matching the playlist entries

### Debug Mode

For detailed troubleshooting, run with debug logging:

```bash
python main.py --playlist playlist.m3u8 --mediafolder C:\Media --outputfolder C:\Output --log-level DEBUG
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Dependencies

-   `m3u-parser`: For parsing M3U8 playlist files
-   Python standard library modules for file operations, logging, and configuration management
