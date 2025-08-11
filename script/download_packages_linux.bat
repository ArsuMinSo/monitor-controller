@echo off
REM Download packages for offline installation on Linux/Raspberry Pi
REM This script downloads packages on Windows for later installation on Linux

echo Downloading packages for offline Linux installation...

REM Create directory for downloaded packages
if not exist "offline_packages_linux" mkdir offline_packages_linux
cd offline_packages_linux

echo.
echo Downloading packages for Linux (ARM64/x86_64)...

REM Download for Linux ARM64 (Raspberry Pi 4/5)
echo Downloading for ARM64 (Raspberry Pi 4/5)...
py -m pip download --platform linux_aarch64 --only-binary=:all: websockets>=12.0
py -m pip download --platform linux_aarch64 --only-binary=:all: python-pptx>=1.0.0
py -m pip download --platform linux_aarch64 --only-binary=:all: Pillow>=10.0.0

REM Download for Linux ARM32 (older Raspberry Pi models)
echo Downloading for ARM32 (older Raspberry Pi)...
py -m pip download --platform linux_armv7l --only-binary=:all: websockets>=12.0
py -m pip download --platform linux_armv7l --only-binary=:all: python-pptx>=1.0.0
py -m pip download --platform linux_armv7l --only-binary=:all: Pillow>=10.0.0

REM Download for Linux x86_64 (standard Linux)
echo Downloading for x86_64 (standard Linux)...
py -m pip download --platform linux_x86_64 --only-binary=:all: websockets>=12.0
py -m pip download --platform linux_x86_64 --only-binary=:all: python-pptx>=1.0.0
py -m pip download --platform linux_x86_64 --only-binary=:all: Pillow>=10.0.0

REM Download universal/source packages as fallback
echo Downloading universal packages as fallback...
py -m pip download --no-binary=:all: websockets>=12.0
py -m pip download --no-binary=:all: python-pptx>=1.0.0
py -m pip download --no-binary=:all: Pillow>=10.0.0

REM Download all dependencies
echo Downloading all dependencies...
py -m pip download websockets>=12.0 python-pptx>=1.0.0 Pillow>=10.0.0

cd ..

echo.
echo ========================================
echo Package download completed!
echo.
echo Files are in: offline_packages_linux/
echo.
echo To install on Linux machine:
echo 1. Copy the offline_packages_linux folder to your Linux machine
echo 2. Run: python3 -m pip install --find-links offline_packages_linux --no-index websockets python-pptx Pillow
echo.
echo For Raspberry Pi specifically:
echo python3 -m pip install --find-links offline_packages_linux --no-index --prefer-binary websockets python-pptx Pillow
echo ========================================

pause
