#!/bin/bash
# Install packages from offline downloads on Linux
# Run this script on your Linux machine after copying the offline_packages_linux folder

echo "Installing Presentator dependencies from offline packages..."

# Check if offline packages directory exists
if [ ! -d "offline_packages_linux" ]; then
    echo "Error: offline_packages_linux directory not found!"
    echo "Please copy the offline_packages_linux folder from your Windows machine first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install packages from offline directory
echo "Installing packages from offline downloads..."
python3 -m pip install --find-links offline_packages_linux --no-index --prefer-binary websockets python-pptx Pillow

# Check installation
echo ""
echo "Checking installed packages..."
python3 -c "
try:
    import websockets
    import pptx
    from PIL import Image
    print('All packages installed successfully!')
    print('websockets:', websockets.__version__) 
    print('python-pptx: Available') 
    print('Pillow: Available')
except ImportError as e:
    print('Import error:', e)
"

echo ""
echo "Installation completed!"
echo "To activate the environment later, run: source venv/bin/activate"
