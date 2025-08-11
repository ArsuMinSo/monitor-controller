"""
Presentator - Real-Time Slideshow System

Main application entry point for the Presentator system. This script initializes
and coordinates all system components including the HTTP server, WebSocket server,
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
from pathlib import Path

# Run dependency check first
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
    try:
        import websockets
        import pptx  # python-pptx
        import PIL  # Pillow for image processing
    except ImportError as e:
        print(f" Missing dependency: {e}")
        print(" Install dependencies with: py -m pip install -r requirements.txt")
        print(" Or run full check: py check_dependencies.py")
        sys.exit(1)

# Import the modular components

try:
    from src.slideshow_manager import SlideShowManager
    from src.websocket_manager import WebSocketManager
    from src.http_server import start_http_server
    from src.utils import get_local_ip
except NotImplementedError as e:
    print(f"Error: {e}")
    print("Some features are not implemented yet. Please check the codebase for updates.")
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
    print("Slideshow System Starting...")
    
    # Quick dependency check
    check_dependencies()
    
    # Create directories
    os.makedirs("slideshows", exist_ok=True)
    os.makedirs("web", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    # Create empty favicon.ico to prevent 404 errors
    favicon_path = Path("web/favicon.ico")
    if not favicon_path.exists():
        favicon_path.write_bytes(b'')
    
    # Initialize managers
    slideshow_manager = SlideShowManager()
    websocket_manager = WebSocketManager()
    
    # Load initial slideshows
    slideshows = slideshow_manager.discover_slideshows()
    websocket_manager.update_slideshows_list(slideshows)
    print(f"Found {len(slideshows)} slideshows")
    
    # Get local IP address
    local_ip = get_local_ip()
    
    # Start HTTP server with proper dependencies
    http_thread = threading.Thread(
        target=start_http_server, 
        args=(50000, slideshow_manager, websocket_manager),
        daemon=True
    )
    http_thread.start()
    
    # Start WebSocket server
    print("WebSocket server starting on ws://0.0.0.0:50001")
    websocket_server = await websocket_manager.start_websocket_server(50001)
    
    print("HTTP server running at http://0.0.0.0:50000")
    print("System ready!")
    print("Access URLs:")
    print(f"   Network:  http://{local_ip}:50000/web/controller.html")
    print(f"   Viewer:   http://{local_ip}:50000/web/viewer.html")
    print(f"Other devices can connect using: http://{local_ip}:50000")
    
    # Keep running
    await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Slideshow system stopped")
