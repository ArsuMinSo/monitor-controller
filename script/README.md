# Scripts Directory

This directory contains utility scripts for Presentator system deployment, installation, and maintenance.

## Script Overview

### Installation & Deployment Scripts

#### `install.py`

**Purpose**: Main installation script for setting up Presentator dependencies
**Usage**: `py install.py`  
**Description**:

- Automatically installs required Python packages
- Checks system compatibility
- Sets up virtual environment if needed
- Handles both online and offline installation modes

#### `copy-script.bat`

**Purpose**: Deploy Presentator to remote Linux/Raspberry Pi systems  
**Usage**: `copy-script.bat`  
**Description**:

- Copies all Presentator files to remote server via SCP
- Updates web files, source code, and configurations
- Includes offline packages for systems without internet
- Requires SSH access to target system
- **FILL PARAMETERS BEFORE RUN**: REMOTE_USER, REMOTE_HOST parameters needs to be filled with target rpi/linux device

#### `download_packages_linux.bat`

**Purpose**: Download Python packages for offline Rpi/Linux installation  
**Usage**: `download_packages_linux.bat`  
**Description**:

- Downloads packages for ARM64 (Raspberry Pi) and x86_64 architectures
- Creates `offline_packages_linux/` directory with all dependencies
- Includes source packages as fallback options
- Must be run on Windows system with internet access

#### `install_offline_linux.sh`

**Purpose**: Install Presentator dependencies on offline Linux systems  
**Usage**: `chmod +x install_offline_linux.sh && ./install_offline_linux.sh`  
**Description**:

- Installs packages from local `offline_packages_linux/` directory
- Works without internet connection
- Handles ARM and x86_64 architectures automatically
- Creates virtual environment and installs dependencies

### Maintenance Scripts

#### `generate_docs.py`

**Purpose**: Generate comprehensive HTML documentation using pydoc  

## Usage Examples

### Fresh Installation

```bash
# On Windows (with internet)
py install.py

# On Linux (with internet)
python3 install.py
```

### Offline Installation for Linux

```bash
# Step 1: On Windows machine (with internet)
download_packages_linux.bat

# Step 2: Copy offline_packages_linux/* to Linux machine
copy-script.bat

# Step 3: On Linux machine (without internet)
chmod +x install_offline_linux.sh
./install_offline_linux.sh
```

### Remote Deployment

```bash
# Edit copy-script.bat with your server details first
copy-script.bat
```

## Configuration Requirements

### For `copy-script.bat`

Before running, edit the script to set:

- `REMOTE_USER` - SSH username
- `REMOTE_HOST` - Server IP or hostname
- Ensure SSH key authentication is set up - if its not, do it manually. Tutorials, how to do it, are surely on internet.

### For offline installation

- Run `download_packages_linux.bat` on a Windows machine with internet
- Copy the generated `offline_packages_linux/` folder to your target Linux system
- Ensure Python 3.7+ is installed on the target system

## Dependencies

### System Requirements

- **Windows**: Python 3.7+, internet access for downloads
- **Linux**: Python 3.7+, pip, virtual environment support
- **SSH/SCP/SFTP**: For remote deployment (OpenSSH or PuTTY)

### Python Packages Handled

- `websockets>=10.0` - WebSocket communication
- `python-pptx>=0.6.21` - PowerPoint file processing  
- `Pillow>=8.0.0` - Image processing

## File Structure After Installation

```text
Presentator/
 scripts/
    README.md              # This file
    install.py             # Main installer
    copy-script.bat        # Remote deployment
    download_packages_linux.bat  # Package downloader
    install_offline_linux.sh     # Offline installer
    rename_project.bat     # Project renamer
    OFFLINE_INSTALL.md     # Offline installation guide
 offline_packages_linux/    # Downloaded packages (after download)
 app.py                     # Main application
 ...
```

## Security Notes

- SSH keys are recommended over password authentication
- Verify server fingerprints when connecting to new systems
