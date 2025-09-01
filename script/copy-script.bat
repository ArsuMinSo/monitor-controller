
@echo off
REM ============================================================================
REM Presentator System - Complete Copy Script
REM ============================================================================
REM This script copies the entire Presentator system to a destination folder
REM including all necessary files, directories, and configurations
REM ============================================================================

setlocal enabledelayedexpansion

echo %BLUE%============================================================================%RESET%
echo %BLUE%                    Presentator System Copy Script                          %RESET%
echo %BLUE%============================================================================%RESET%
echo.

REM Get source directory (current directory)
set "SOURCE_DIR=%~dp0.."
echo %GREEN%Source Directory: %SOURCE_DIR%%RESET%

REM Get destination directory from user
if "%1"=="" (
    echo %YELLOW%Usage: %0 [destination_path]%RESET%
    echo %YELLOW%Example: %0 "C:\Backup\presentator-backup"%RESET%
    echo.
    set /p "DEST_DIR=Enter destination path: "
) else (
    set "DEST_DIR=%1"
)

echo %GREEN%Destination Directory: %DEST_DIR%%RESET%
echo.

REM Create destination directory
if not exist "%DEST_DIR%" (
    echo %BLUE%Creating destination directory...%RESET%
    mkdir "%DEST_DIR%" 2>nul
    if errorlevel 1 (
        echo %RED%Error: Could not create destination directory%RESET%
        pause
        exit /b 1
    )
)

echo %BLUE%Starting copy operation...%RESET%
echo.

REM Copy main application files
echo %YELLOW%[1/10] Copying main application files...%RESET%
copy "%SOURCE_DIR%\app.py" "%DEST_DIR%\" >nul 2>&1
copy "%SOURCE_DIR%\requirements.txt" "%DEST_DIR%\" >nul 2>&1
copy "%SOURCE_DIR%\README.md" "%DEST_DIR%\" >nul 2>&1
copy "%SOURCE_DIR%\LICENSE" "%DEST_DIR%\" >nul 2>&1
copy "%SOURCE_DIR%\.gitignore" "%DEST_DIR%\" >nul 2>&1
if exist "%SOURCE_DIR%\check_dependencies.py" copy "%SOURCE_DIR%\check_dependencies.py" "%DEST_DIR%\" >nul 2>&1
echo %GREEN%   ✓ Main files copied%RESET%

REM Copy source code directory
echo %YELLOW%[2/10] Copying source code directory (src/)...%RESET%
if exist "%SOURCE_DIR%\src" (
    xcopy "%SOURCE_DIR%\src" "%DEST_DIR%\src" /E /I /H /Y >nul 2>&1
    echo %GREEN%   ✓ Source code copied%RESET%
) else (
    echo %RED%   ✗ Source directory not found%RESET%
)

REM Copy web interface directory
echo %YELLOW%[3/10] Copying web interface directory (web/)...%RESET%
if exist "%SOURCE_DIR%\web" (
    xcopy "%SOURCE_DIR%\web" "%DEST_DIR%\web" /E /I /H /Y >nul 2>&1
    echo %GREEN%   ✓ Web interface copied%RESET%
) else (
    echo %RED%   ✗ Web directory not found%RESET%
)

REM Copy slideshows directory
echo %YELLOW%[4/10] Copying slideshows directory (slideshows/)...%RESET%
if exist "%SOURCE_DIR%\slideshows" (
    xcopy "%SOURCE_DIR%\slideshows" "%DEST_DIR%\slideshows" /E /I /H /Y >nul 2>&1
    echo %GREEN%   ✓ Slideshows copied%RESET%
) else (
    echo %BLUE%   ℹ Creating empty slideshows directory%RESET%
    mkdir "%DEST_DIR%\slideshows" 2>nul
)

REM Copy script directory
echo %YELLOW%[5/10] Copying script directory (script/)...%RESET%
if exist "%SOURCE_DIR%\script" (
    xcopy "%SOURCE_DIR%\script" "%DEST_DIR%\script" /E /I /H /Y >nul 2>&1
    echo %GREEN%   ✓ Scripts copied%RESET%
) else (
    echo %RED%   ✗ Script directory not found%RESET%
)

REM Copy documentation directory
echo %YELLOW%[6/10] Copying documentation directory (docs/)...%RESET%
if exist "%SOURCE_DIR%\docs" (
    xcopy "%SOURCE_DIR%\docs" "%DEST_DIR%\docs" /E /I /H /Y >nul 2>&1
    echo %GREEN%   ✓ Documentation copied%RESET%
) else (
    echo %RED%   ✗ Documentation directory not found%RESET%
)

REM Copy offline packages directory
echo %YELLOW%[7/10] Copying offline packages directory...%RESET%
if exist "%SOURCE_DIR%\offline_packages_linux" (
    xcopy "%SOURCE_DIR%\offline_packages_linux" "%DEST_DIR%\offline_packages_linux" /E /I /H /Y >nul 2>&1
    echo %GREEN%   ✓ Linux offline packages copied%RESET%
) else (
    echo %BLUE%   ℹ Linux offline packages not found (optional)%RESET%
)

if exist "%SOURCE_DIR%\offline_packages_windows" (
    xcopy "%SOURCE_DIR%\offline_packages_windows" "%DEST_DIR%\offline_packages_windows" /E /I /H /Y >nul 2>&1
    echo %GREEN%   ✓ Windows offline packages copied%RESET%
) else (
    echo %BLUE%   ℹ Windows offline packages not found (optional)%RESET%
)

REM Copy VS Code configuration
echo %YELLOW%[8/10] Copying VS Code configuration (.vscode/)...%RESET%
if exist "%SOURCE_DIR%\.vscode" (
    xcopy "%SOURCE_DIR%\.vscode" "%DEST_DIR%\.vscode" /E /I /H /Y >nul 2>&1
    echo %GREEN%   ✓ VS Code configuration copied%RESET%
) else (
    echo %BLUE%   ℹ VS Code configuration not found (optional)%RESET%
)

REM Copy GitHub configuration
echo %YELLOW%[9/10] Copying GitHub configuration (.github/)...%RESET%
if exist "%SOURCE_DIR%\.github" (
    xcopy "%SOURCE_DIR%\.github" "%DEST_DIR%\.github" /E /I /H /Y >nul 2>&1
    echo %GREEN%   ✓ GitHub configuration copied%RESET%
) else (
    echo %BLUE%   ℹ GitHub configuration not found (optional)%RESET%
)

REM Create necessary empty directories
echo %YELLOW%[10/10] Creating additional directories...%RESET%
mkdir "%DEST_DIR%\temp" 2>nul
mkdir "%DEST_DIR%\logs" 2>nul
echo %GREEN%   ✓ Empty directories created (temp, logs)%RESET%

echo.
echo %BLUE%============================================================================%RESET%

REM Verify copy operation
echo %BLUE%Verifying copy operation...%RESET%
set "ERRORS=0"

if not exist "%DEST_DIR%\app.py" (
    echo %RED%   ✗ app.py missing%RESET%
    set /a ERRORS+=1
)

if not exist "%DEST_DIR%\src" (
    echo %RED%   ✗ src directory missing%RESET%
    set /a ERRORS+=1
)

if not exist "%DEST_DIR%\web" (
    echo %RED%   ✗ web directory missing%RESET%
    set /a ERRORS+=1
)

if not exist "%DEST_DIR%\requirements.txt" (
    echo %RED%   ✗ requirements.txt missing%RESET%
    set /a ERRORS+=1
)

if %ERRORS% equ 0 (
    echo %GREEN%   ✓ All essential files verified%RESET%
) else (
    echo %RED%   ✗ %ERRORS% critical files missing%RESET%
)

echo.
echo %BLUE%============================================================================%RESET%

REM Calculate directory sizes
echo %BLUE%Copy Summary:%RESET%
for /f "tokens=3" %%a in ('dir "%DEST_DIR%" /s /-c 2^>nul ^| findstr /i "file(s)"') do set "FILE_COUNT=%%a"
for /f "tokens=3" %%a in ('dir "%DEST_DIR%" /s /-c 2^>nul ^| findstr /i "dir(s)"') do set "DIR_COUNT=%%a"

echo %GREEN%   Total Files Copied: %FILE_COUNT%%RESET%
echo %GREEN%   Total Directories: %DIR_COUNT%%RESET%
echo %GREEN%   Destination: %DEST_DIR%%RESET%

echo.
if %ERRORS% equ 0 (
    echo %GREEN%✓ Copy operation completed successfully!%RESET%
    echo %GREEN%✓ The Presentator system is ready to use in the destination folder%RESET%
    echo.
    echo %YELLOW%Next steps:%RESET%
    echo %YELLOW%1. Navigate to: cd "%DEST_DIR%"%RESET%
    echo %YELLOW%2. Install dependencies: py -m pip install -r requirements.txt%RESET%
    echo %YELLOW%3. Run the application: py app.py%RESET%
) else (
    echo %RED%✗ Copy operation completed with errors%RESET%
    echo %RED%✗ Please check the missing files and try again%RESET%
)

echo.
echo %BLUE%============================================================================%RESET%
pause