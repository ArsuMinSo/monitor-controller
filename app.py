"""
Presentator - Real-Time Slideshow System

Main application entry point for the Presentator system. This script initializes
and coordinates all system components including    # Initialize logging first (before creating any loggers)
    logger = setup_logging()
    
    try:
        logger.info("Slideshow System Starting...")
        print("Slideshow System Starting...")
        
        # Quick dependency check
        check_dependencies()erver, WebSocket server,
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

# Run dependency check first
def setup_logging():
    """
    Configure comprehensive logging for the Presentator system.
    
    Sets up multiple logging handlers with different levels:
    - Console: INFO level for user feedback
    - File: DEBUG level for detailed troubleshooting
    - Error File: ERROR level for critical issues only
    
    Creates logs directory and implements log rotation to prevent
    disk space issues from accumulating log files.
    """
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
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
        main_log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Error log file - ERROR level only
    error_log_file = os.path.join("logs", "errors.log")
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    # Log startup message
    logger.info("=" * 50)
    logger.info("Presentator System Starting - %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info("Logging initialized - Main: %s, Errors: %s", main_log_file, error_log_file)
    logger.info("=" * 50)
    
    return logger


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
        
        # Initialize logging first
        setup_logging()
        
        # Quick dependency check
        check_dependencies()
        
        # Create directories
        logger.debug("Creating required directories...")
        directories = ["slideshows", "web", "temp", "logs"]
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
        logger.debug("Managers initialized successfully")
        
        # Load initial slideshows
        logger.info("Discovering slideshows...")
        slideshows = slideshow_manager.discover_slideshows()
        websocket_manager.update_slideshows_list(slideshows)
        logger.info(f"Found {len(slideshows)} slideshows")
        print(f"Found {len(slideshows)} slideshows")
        
        # Get local IP address
        logger.debug("Getting local IP address...")
        local_ip = get_local_ip()
        logger.debug(f"Local IP: {local_ip}")
        
        # Start HTTP server with proper dependencies
        logger.info("Starting HTTP server on port 50000...")
        http_thread = threading.Thread(
            target=start_http_server, 
            args=(50000, slideshow_manager, websocket_manager),
            daemon=True,
            name="HTTPServer"
        )
        http_thread.start()
        logger.debug("HTTP server thread started")
        
        # Start WebSocket server
        logger.info("Starting WebSocket server on port 50001...")
        print("WebSocket server starting on ws://0.0.0.0:50001")
        websocket_server = await websocket_manager.start_websocket_server(50001)
        logger.info("WebSocket server started successfully")
        
        # Display success information
        success_messages = [
            "System ready!",
            "HTTP server running at http://0.0.0.0:50000",
            "Access URLs:",
            f"   Controller: http://{local_ip}:50000/web/controller.html",
            f"   Viewer:     http://{local_ip}:50000/web/viewer.html",
            f"   Editor:     http://{local_ip}:50000/web/editor.html",
            f"Network access: http://{local_ip}:50000"
        ]
        
        for msg in success_messages:
            logger.info(msg.replace('', '').replace('', '').replace('', '').replace('', '').replace('', '').replace('', '').replace('', ''))
            print(msg)
        
        logger.info("System fully operational - entering main loop")
        
        # Keep running
        await asyncio.Future()
        
    except Exception as e:
        logger.error(f"Fatal error in main(): {e}", exc_info=True)
        print(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
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
