"""
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
"""

import asyncio
import os
import threading
import sys
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
def setup_logging():
    """
    Configure comprehensive logging for the Presentator system.
    
    Sets up multiple logging handlers with different levels:
    - Console: INFO level for user feedback
    - File: DEBUG level for detailed troubleshooting
    - Error File: ERROR level for critical issues only
    
    Creates logs directory and implements log rotation to prevent
    disk space issues from accumulating log files.
    
    Log Rotation:
    - Forced rotation on every system startup (fresh logs each session)
    - Main log: presentator.log (10MB max, 5 backups: .log.1 to .log.5)
    - Error log: errors.log (5MB max, 5 backups: .log.1 to .log.5)
    
    Startup Process:
    1. Existing logs are rotated (.log -> .log.1, .log.1 -> .log.2, etc.)
    2. Fresh empty log files are created for the new session
    3. Old logs beyond 5 backups are automatically removed
    """
    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Rotate existing logs on startup before creating new handlers
    rotate_logs_on_startup()
    
    # Clean up old log files beyond rotation limit
    cleanup_old_log_files()
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler - INFO level for user feedback
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Main log file - DEBUG level with rotation
    main_log_file = os.path.join("logs", "presentator.log")
    file_handler = logging.handlers.RotatingFileHandler(
        main_log_file, 
        maxBytes=10*1024*1024,  # 10MB per file
        backupCount=5,          # Keep 5 old files (.log.1, .log.2, .log.3, .log.4, .log.5)
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Error log file - ERROR level only with rotation
    error_log_file = os.path.join("logs", "errors.log")
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5*1024*1024,   # 5MB per file
        backupCount=5,          # Keep 5 old files (.log.1, .log.2, .log.3, .log.4, .log.5)
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    # Log startup message
    logger.info("=" * 50)
    logger.info("Presentator System Starting - %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info("Logging initialized with startup rotation - Main: %s, Errors: %s", main_log_file, error_log_file)
    logger.info("Log rotation: Main (10MB, 5 backups), Errors (5MB, 5 backups)")
    logger.info("Logs rotated on every system startup")
    logger.info("=" * 50)
    
    return logger


def cleanup_old_log_files():
    """
    Clean up old log files that exceed the rotation limit.
    
    Removes log files beyond .log.5 for both presentator.log and errors.log
    to prevent unlimited accumulation of old log files.
    """
    if not os.path.exists("logs"):
        return
        
    try:
        # Clean up presentator log files
        cleanup_log_series("presentator.log", max_backups=5)
        
        # Clean up error log files  
        cleanup_log_series("errors.log", max_backups=5)
        
    except Exception as e:
        print(f"Warning: Could not clean up old log files: {e}")


def cleanup_log_series(base_name, max_backups=5):
    """
    Clean up a series of rotated log files.
    
    Args:
        base_name (str): Base name of the log file (e.g., "presentator.log")
        max_backups (int): Maximum number of backup files to keep
    """
    logs_dir = "logs"
    
    # Find all backup files for this log series
    backup_files = []
    for file in os.listdir(logs_dir):
        if file.startswith(base_name + ".") and file[len(base_name)+1:].isdigit():
            backup_num = int(file[len(base_name)+1:])
            backup_files.append((backup_num, file))
    
    # Sort by backup number (highest first)
    backup_files.sort(reverse=True)
    
    # Remove files beyond the limit
    for backup_num, filename in backup_files:
        if backup_num > max_backups:
            file_path = os.path.join(logs_dir, filename)
            try:
                os.remove(file_path)
                print(f"Removed old log file: {filename}")
            except Exception as e:
                print(f"Warning: Could not remove {filename}: {e}")


def rotate_logs_on_startup():
    """
    Force rotation of existing log files on system startup.
    
    This function manually rotates log files at each startup, ensuring
    a fresh start for each session. The rotation pattern:
    - presentator.log -> presentator.log.1
    - presentator.log.1 -> presentator.log.2
    - etc.
    """
    if not os.path.exists("logs"):
        return
        
    try:
        # Rotate presentator log files
        rotate_log_file_series("presentator.log", max_backups=5)
        
        # Rotate error log files  
        rotate_log_file_series("errors.log", max_backups=5)
        
        print("Log files rotated on startup")
        
    except Exception as e:
        print(f"Warning: Could not rotate log files on startup: {e}")


def rotate_log_file_series(base_name, max_backups=5):
    """
    Rotate a series of log files on startup.
    
    Args:
        base_name (str): Base name of the log file (e.g., "presentator.log")
        max_backups (int): Maximum number of backup files to keep
    """
    logs_dir = "logs"
    main_log_path = os.path.join(logs_dir, base_name)
    
    # Only rotate if the main log file exists and has content
    if not os.path.exists(main_log_path) or os.path.getsize(main_log_path) == 0:
        return
    
    # Find existing backup files
    backup_files = []
    for file in os.listdir(logs_dir):
        if file.startswith(base_name + ".") and file[len(base_name)+1:].isdigit():
            backup_num = int(file[len(base_name)+1:])
            if backup_num <= max_backups:
                backup_files.append(backup_num)
    
    # Sort backup numbers in descending order for safe renaming
    backup_files.sort(reverse=True)
    
    # Rename existing backup files (shift them up by 1)
    for backup_num in backup_files:
        old_path = os.path.join(logs_dir, f"{base_name}.{backup_num}")
        new_path = os.path.join(logs_dir, f"{base_name}.{backup_num + 1}")
        
        if backup_num >= max_backups:
            # Remove files that would exceed the limit
            try:
                os.remove(old_path)
                print(f"Removed old backup: {base_name}.{backup_num}")
            except Exception as e:
                print(f"Warning: Could not remove {old_path}: {e}")
        else:
            # Rename to next number
            try:
                os.rename(old_path, new_path)
                print(f"Rotated: {base_name}.{backup_num} -> {base_name}.{backup_num + 1}")
            except Exception as e:
                print(f"Warning: Could not rotate {old_path}: {e}")
    
    # Move main log file to .1
    try:
        backup_path = os.path.join(logs_dir, f"{base_name}.1")
        os.rename(main_log_path, backup_path)
        print(f"Rotated: {base_name} -> {base_name}.1")
    except Exception as e:
        print(f"Warning: Could not rotate main log {main_log_path}: {e}")


def check_dependencies():
    """
    Quick dependency check before starting the server.
    
    Verifies that all required Python packages are installed before
    attempting to start the Presentator system. Provides helpful
    error messages and installation instructions if dependencies are missing.
    
    Exits:
        System exit with code 1 if any required dependencies are missing
        
    Note:
        This is a lightweight check. For more comprehensive dependency
        verification, use the separate check_dependencies.py script.
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.debug("Checking dependencies...")
        import websockets
        logger.debug("websockets imported successfully")
        import pptx  # python-pptx
        logger.debug("python-pptx imported successfully")
        import PIL  # Pillow for image processing
        logger.debug("Pillow imported successfully")
        
        logger.info("All dependencies verified successfully")
        
    except ImportError as e:
        error_msg = f"Missing dependency: {e}"
        logger.error(error_msg)
        print(f"{error_msg}")
        print("Install dependencies with: py -m pip install -r requirements.txt")
        print("Or run full check: py check_dependencies.py")
        sys.exit(1)

# Import the modular components

try:
    from src.slideshow_manager import SlideShowManager
    from src.websocket_manager import WebSocketManager
    from src.http_server import start_http_server
    from src.utils import get_local_ip
    from src.presentation_queue import PresentationQueueManager
    logger = logging.getLogger(__name__)
    logger.debug("All core modules imported successfully")
except NotImplementedError as e:
    logger = logging.getLogger(__name__)
    error_msg = f"Implementation error: {e}"
    logger.error(error_msg)
    print(f"Error: {e}")
    print("Some features are not implemented yet. Please check the codebase for updates.")
    sys.exit(1)
except ImportError as e:
    logger = logging.getLogger(__name__)
    error_msg = f"Module import error: {e}"
    logger.error(error_msg)
    print(f"Import Error: {e}")
    print("Check that all source files exist in the 'src' directory")
    sys.exit(1)

async def main():
    """
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
    """
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Slideshow System Starting...")
        print("Slideshow System Starting...")
        
        # Quick dependency check
        check_dependencies()
        
        # Create directories
        logger.debug("Creating required directories...")
        directories = ["slideshows", "web", "logs"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"Directory ensured: {directory}")
        
        # Create empty favicon.ico to prevent 404 errors
        favicon_path = Path("web/favicon.ico")
        if not favicon_path.exists():
            favicon_path.write_bytes(b'')
            logger.debug("Created empty favicon.ico")
        
        # Initialize managers
        logger.info("Initializing system managers...")
        slideshow_manager = SlideShowManager()
        websocket_manager = WebSocketManager()
        queue_manager = PresentationQueueManager()
        logger.debug("Managers initialized successfully")
        
        # Load initial slideshows
        logger.info("Discovering slideshows...")
        slideshows = slideshow_manager.discover_slideshows()
        websocket_manager.update_slideshows_list(slideshows)
        logger.info(f"Found {len(slideshows)} slideshows")
        print(f"Found {len(slideshows)} slideshows")
        
        # Initialize queue state in websocket manager
        initial_queue_state = queue_manager.get_queue_state()
        websocket_manager.current_state["queue"] = initial_queue_state
        logger.info(f"Initialized queue state with {initial_queue_state.get('queue_length', 0)} items")
        
        # Get local IP address
        logger.debug("Getting local IP address...")
        local_ip = get_local_ip()
        logger.debug(f"Local IP: {local_ip}")
        
        # Start HTTP server with proper dependencies
        logger.info("Starting HTTP server on port 8080...")
        http_thread = threading.Thread(
            target=start_http_server, 
            args=(8080, slideshow_manager, websocket_manager, queue_manager),
            daemon=True,
            name="HTTPServer"
        )
        http_thread.start()
        logger.debug("HTTP server thread started")
        
        # Start WebSocket server
        logger.info("Starting WebSocket server on port 50002...")
        print("WebSocket server starting on ws://0.0.0.0:50002")
        websocket_server = await websocket_manager.start_websocket_server(50002)
        logger.info("WebSocket server started successfully")
        
        # Display success information
        success_messages = [
            "System ready!",
            "HTTP server running at http://0.0.0.0:8080",
            "Access URLs:",
            f"   Controller: http://{local_ip}:8080/web/controller.html",
            f"   Viewer:     http://{local_ip}:8080/web/viewer.html",
            f"   Editor:     http://{local_ip}:8080/web/editor.html",
            f"Network access: http://{local_ip}:8080"
        ]
        
        for msg in success_messages:
            logger.info(msg)
            print(msg)
        
        logger.info("System fully operational - entering main loop")
        
        # Keep running
        await asyncio.Future()
        
    except Exception as e:
        logger.error(f"Fatal error in main(): {e}", exc_info=True)
        print(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    # Initialize logging first (before creating any loggers)
    logger = setup_logging()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger = logging.getLogger(__name__)
        logger.info("Keyboard interrupt received")
        logger.info("Slideshow system stopped gracefully")
        print("\nSlideshow system stopped")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        print(f"\nUnexpected error: {e}")
        print("Check logs/errors.log for detailed error information")
        sys.exit(1)
