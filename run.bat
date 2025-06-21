@echo off
echo M3U8 to Folder - Media File Copier
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo Please run install.bat first to set up the environment.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if arguments were provided
if "%~1"=="" (
    echo Usage: %0 --playlist PLAYLIST --mediafolder MEDIAFOLDER --outputfolder OUTPUTFOLDER [OPTIONS]
    echo.
    echo Examples:
    echo   %0 --playlist my_playlist.m3u8 --mediafolder C:\Media --outputfolder C:\Output
    echo   %0 --playlist playlist.m3u8 --mediafolder C:\Media --outputfolder C:\Output --dry-run
    echo.
    echo For full help, run: %0 --help
    echo.
    pause
    exit /b 1
)

REM Run the application with all provided arguments
call python main.py %*

REM Check exit code
if errorlevel 1 (
    echo.
    echo Application finished with errors. Check the output above for details.
    pause
    exit /b 1
)

echo.
echo Application completed successfully!
pause
