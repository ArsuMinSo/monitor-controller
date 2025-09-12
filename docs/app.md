# Main Application

**Module:** `app`  
**File:** `app.py`

## Overview

Presentator - Real-Time Slideshow System

Main application entry point for the Presentator system. This script initializes
and coordinates all system components including HTTP server, WebSocket server,
and slideshow management services.

The Presentator system provides:

- Web-based slideshow creation and editing
- Real-time synchronized slideshow display across multiple devices
- PowerPoint import and conversion
- RESTful API for slideshow management
- WebSocket-based real-time communication

Requirements:
    - Python 3.7 or higher
    - see requirements.txt for Python dependencies

The system runs two servers:
    - HTTP Server: Web interface and REST API
    - WebSocket Server: Real-time communication

## Functions

### check_dependencies()

Quick dependency check before starting the server.

Verifies that all required Python packages are installed before
attempting to start the Presentator system. Provides helpful
error messages and installation instructions if dependencies are missing.

Exits:
    System exit with code 1 if any required dependencies are missing

Note:
    This is a lightweight check. For more comprehensive dependency
    verification, use the separate check_dependencies.py script.

### main()

Main application entry point and server coordinator.

Initializes and starts all Presentator system components:

1. Performs dependency checks
2. Creates slideshow and WebSocket managers
3. Discovers available slideshows
4. Starts WebSocket server for real-time communication
5. Starts HTTP server for web interface and API
6. Displays connection information

The function runs indefinitely, coordinating both servers until
the application is terminated.

Note:
    This function should be run with asyncio.run() to handle
    the asynchronous WebSocket server properly.

### setup_logging()

Configure comprehensive logging for the Presentator system.

Sets up multiple logging handlers with different levels:

- Console: INFO level for user feedback
- File: DEBUG level for detailed troubleshooting
- Error File: ERROR level for critical issues only

Creates logs directory and implements log rotation to prevent
disk space issues from accumulating log files.

## Source File Statistics

- **Total Lines:** 277
- **Code Lines:** 209
- **Functions:** 2
- **Classes:** 0
- **File Size:** 10202 bytes
