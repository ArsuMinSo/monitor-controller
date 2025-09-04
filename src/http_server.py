"""
HTTP Server Module for Presentator

This module provides HTTP server functionality with REST API endpoints
for slideshow management, file serving, and PowerPoint conversion.
Handles web interface serving and API communication between frontend and backend.
"""

import http.server
import socketserver
import json
import logging
import datetime
from pathlib import Path


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler for Presentator API and web serving.
    
    Extends SimpleHTTPRequestHandler to provide:
    - REST API endpoints for slideshow management
    - File serving for web interface and slideshow assets
    - PowerPoint upload and conversion
    - CORS support for cross-origin requests
    
    Attributes:
        slideshow_manager: Instance of SlideShowManager for slideshow operations
        websocket_manager: Instance of WebSocketManager for real-time updates
    """
    
    def __init__(self, *args, slideshow_manager=None, websocket_manager=None, **kwargs):
        """
        Initialize the HTTP request handler.
        
        Args:
            slideshow_manager: SlideShowManager instance for slideshow operations
            websocket_manager: WebSocketManager instance for real-time communication
            *args: Positional arguments passed to parent class
            **kwargs: Keyword arguments passed to parent class
        """
        self.slideshow_manager = slideshow_manager
        self.websocket_manager = websocket_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """
        Handle HTTP GET requests.
        
        Routes requests to appropriate handlers:
        - /api/* -> API endpoints
        - /slideshows/* -> Slideshow asset files
        - /* -> Web interface files from /web directory
        """
        self.logger.debug(f"GET request: {self.path} from {self.client_address[0]}")
        
        if self.path.startswith('/api/'):
            self.handle_api_request()
        elif self.path.startswith('/slideshows/'):
            # Serve slideshow images and files
            self.serve_slideshow_files()
        else:
            # Serve files from web directory
            if self.path == '/':
                self.path = '/web/controller.html'
                self.logger.debug("Redirecting root to controller.html")
            elif not self.path.startswith('/web/'):
                self.path = '/web' + self.path
                self.logger.debug(f"Adding /web prefix to path: {self.path}")
            super().do_GET()
    
    def do_POST(self):
        """
        Handle HTTP POST requests.
        
        Routes POST requests to API endpoints for data modification operations
        like saving slideshows, uploading files, etc.
        """
        self.logger.debug(f"POST request: {self.path} from {self.client_address[0]}")
        
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            self.logger.warning(f"Invalid POST request path: {self.path}")
            self.send_error(404, "Not Found")
    
    def handle_api_request(self):
        """
        Route API requests to appropriate handler methods.
        
        Supported endpoints:
        - /api/slideshows: Get list of available slideshows
        - /api/save_slideshow: Save slideshow data
        - /api/load_slideshow: Load specific slideshow
        - /api/delete_slideshow: Delete slideshow
        - /api/upload_pptx: Upload and convert PowerPoint files
        
        Handles exceptions and returns appropriate HTTP error codes.
        """
        try:
            if self.path == '/api/slideshows':
                self.handle_get_slideshows()
            elif self.path == '/api/clients':
                self.handle_get_clients()
            elif self.path == '/api/save_slideshow':
                self.handle_save_slideshow()
            elif self.path == '/api/load_slideshow':
                self.handle_load_slideshow()
            elif self.path == '/api/delete_slideshow':
                self.handle_delete_slideshow()
            elif self.path == '/api/upload_pptx':
                self.handle_upload_pptx()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            print(f"API error: {e}")
            self.send_error(500, f"Internal server error: {e}")
    
    def handle_get_slideshows(self):
        """
        Handle GET /api/slideshows endpoint.
        
        Returns a JSON list of all available slideshows in the system.
        Also updates connected WebSocket clients with the current slideshow list.
        
        Response:
            200: JSON array of slideshow objects
            500: Internal server error
        """
        slideshows = self.slideshow_manager.discover_slideshows()
        self.websocket_manager.update_slideshows_list(slideshows)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(slideshows).encode())
    
    def handle_get_clients(self):
        """
        Handle GET /api/clients endpoint.
        
        Returns information about currently connected WebSocket clients,
        including IP addresses, connection times, and activity.
        
        Response:
            200: JSON object with client statistics and details
            500: Internal server error
        """
        client_stats = self.websocket_manager.get_client_stats()
        unique_ips = self.websocket_manager.get_unique_ips()
        
        response_data = {
            "total_clients": client_stats["total_clients"],
            "unique_ips": len(unique_ips),
            "ip_addresses": unique_ips,
            "clients": client_stats["clients"],
            "server_time": datetime.datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())
    
    def handle_save_slideshow(self):
        """
        Handle POST /api/save_slideshow endpoint.
        
        Saves slideshow data to file system. Expects JSON payload with
        slideshow data and optional filename.
        
        Request Body:
            JSON object containing slideshow data and optional filename
            
        Response:
            200: Success with filepath
            400: Bad request (invalid JSON or save error)
        """
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            slideshow_data = json.loads(post_data)
            filename = slideshow_data.get('filename')
            filepath = self.slideshow_manager.save_editor_slideshow(slideshow_data, filename)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "filepath": filepath}).encode())
            
        except Exception as e:
            self.send_error(400, f"Save failed: {e}")
    
    def handle_load_slideshow(self):
        """
        Handle GET/POST /api/load_slideshow endpoint.
        
        GET: Returns the most recently modified slideshow
        POST: Loads specific slideshow by filename
        
        For POST requests:
            Request Body: JSON with 'filename' field
            
        Response:
            200: JSON slideshow data
            400: Bad request (missing filename for POST)
            404: Slideshow not found
        """
        if self.command == 'POST':
            # Handle specific slideshow loading
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                filename = data.get('filename')
                
                if filename:
                    # Load specific slideshow
                    slideshows_dir = Path("slideshows")
                    filepath = slideshows_dir / filename
                    
                    if filepath.exists():
                        with open(filepath, 'r', encoding='utf-8') as f:
                            slideshow_data = json.load(f)
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps(slideshow_data).encode())
                    else:
                        self.send_error(404, "Slideshow not found")
                else:
                    self.send_error(400, "Filename required")
                    
            except Exception as e:
                self.send_error(400, f"Load failed: {e}")
        else:
            # Handle general slideshow loading (GET)
            slideshows_dir = Path("slideshows")
            latest_file = None
            latest_time = 0
            
            if slideshows_dir.exists():
                for file in slideshows_dir.glob("*_editor.json"):
                    if file.stat().st_mtime > latest_time:
                        latest_time = file.stat().st_mtime
                        latest_file = file
            
            if latest_file:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    slideshow_data = json.load(f)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(slideshow_data).encode())
            else:
                self.send_error(404, "No slideshows found")
    
    def handle_delete_slideshow(self):
        """
        Handle POST /api/delete_slideshow endpoint.
        
        Deletes a slideshow from the file system and updates all connected clients.
        
        Request Body:
            JSON object with 'id' field containing slideshow identifier
            
        Response:
            200: Success confirmation
            400: Bad request (missing ID or delete error)
        """
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(post_data)
            slideshow_id = data.get('id')
            print(f"Deleting slideshow with ID: {slideshow_id}")
            print(f"data: {data}")
            
            if slideshow_id:
                updated_slideshows = self.slideshow_manager.delete_slideshow(slideshow_id)
                self.websocket_manager.update_slideshows_list(updated_slideshows)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode())
            else:
                self.send_error(400, "Slideshow ID required")
                
        except Exception as e:
            self.send_error(400, f"Delete failed: {e}")

    def handle_upload_pptx(self):
        """
        Handle POST /api/upload_pptx endpoint.
        
        Accepts PowerPoint (.pptx) file uploads and converts them to slideshow format.
        Supports multipart/form-data uploads with file and optional name fields.
        
        Request:
            Content-Type: multipart/form-data
            Fields:
                - file: PPTX file data
                - name: Optional slideshow name (defaults to "Uploaded Presentation")
                
        Response:
            200: Conversion result with success status and details
            400: Bad request (invalid file type or missing file)
            500: Internal server error during conversion
        """
        try:
            import tempfile
            import os
            from pathlib import Path

            content_length = int(self.headers['Content-Length'])
            content_type = self.headers.get('Content-Type')

            if not content_type or 'multipart/form-data' not in content_type:
                self.send_error(400, "Content-Type must be multipart/form-data")
                return

            # Parse multipart form data
            boundary = content_type.split("boundary=")[-1].encode()
            body = self.rfile.read(content_length)
            parts = body.split(b"--" + boundary)
            
            file_data = None
            filename = None
            slideshow_name = "Uploaded Presentation"

            for part in parts:
                if b'Content-Disposition' in part and b'\r\n\r\n' in part:
                    headers, _, value = part.partition(b'\r\n\r\n')
                    headers_str = headers.decode(errors='ignore')
                    
                    if 'name="file"' in headers_str:
                        filename_marker = 'filename="'
                        if filename_marker in headers_str:
                            filename_start = headers_str.index(filename_marker) + len(filename_marker)
                            filename_end = headers_str.index('"', filename_start)
                            filename = headers_str[filename_start:filename_end]
                            file_data = value.rstrip(b'\r\n')
                    elif 'name="name"' in headers_str:
                        slideshow_name = value.decode(errors='ignore').strip().rstrip('\r\n')

            if not file_data or not filename or not filename.lower().endswith('.pptx'):
                self.send_error(400, "Valid PPTX file required")
                return
            
            # Save and convert file
            temp_dir = tempfile.mkdtemp()
            temp_file = Path(temp_dir) / filename
            
            with open(temp_file, 'wb') as f:
                f.write(file_data)
            
            try:
                result = self.slideshow_manager.convert_pptx_file(temp_file, slideshow_name)
                
                # Clean up
                os.unlink(temp_file)
                os.rmdir(temp_dir)
                
                if result["success"]:
                    slideshows = self.slideshow_manager.discover_slideshows()
                    self.websocket_manager.update_slideshows_list(slideshows)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as conv_error:
                if temp_file.exists():
                    os.unlink(temp_file)
                if Path(temp_dir).exists():
                    os.rmdir(temp_dir)
                raise conv_error
                
        except Exception as e:
            self.send_error(500, f"Upload failed: {e}")

    def serve_slideshow_files(self):
        """
        Serve static slideshow assets (images, JSON files).
        
        Handles requests to /slideshows/* paths, serving files directly from
        the file system with appropriate MIME types and caching headers.
        
        Supported file types:
            - Images: .png, .jpg, .jpeg
            - Data: .json
            - Other: served as application/octet-stream
            
        Response:
            200: File content with appropriate headers
            404: File not found
            500: Server error accessing file
        """
        try:
            # Remove leading slash and convert to Path
            file_path = Path(self.path[1:])  # Remove leading '/'
            
            if file_path.exists() and file_path.is_file():
                # Determine content type
                if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    content_type = f'image/{file_path.suffix[1:].lower()}'
                    if content_type == 'image/jpg':
                        content_type = 'image/jpeg'
                elif file_path.suffix.lower() == '.json':
                    content_type = 'application/json'
                else:
                    content_type = 'application/octet-stream'
                
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'max-age=3600')  # Cache for 1 hour
                self.end_headers()
                
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
                
        except Exception as e:
            print(f"Error serving slideshow file {self.path}: {e}")
            self.send_error(500, f"Error serving file: {e}")

def create_http_handler(slideshow_manager, websocket_manager):
    """
    Create HTTP handler factory with dependency injection.
    
    Returns a handler class factory that creates CustomHTTPRequestHandler
    instances with the provided slideshow and websocket managers injected.
    
    Args:
        slideshow_manager: SlideShowManager instance for slideshow operations
        websocket_manager: WebSocketManager instance for real-time communication
        
    Returns:
        Handler factory function that creates configured request handlers
    """
    def handler(*args, **kwargs):
        return CustomHTTPRequestHandler(*args, slideshow_manager=slideshow_manager, 
                                      websocket_manager=websocket_manager, **kwargs)
    return handler


def start_http_server(port=50000, slideshow_manager=None, websocket_manager=None):
    """
    Start the HTTP server on specified port.
    
    Creates and starts a TCP server with the custom HTTP handler.
    Blocks execution until server is stopped.
    
    Args:
        port (int): Port number to listen on (default: 50000)
        slideshow_manager: SlideShowManager instance for slideshow operations
        websocket_manager: WebSocketManager instance for real-time communication
        
    Note:
        This function blocks and runs the server indefinitely until interrupted.
    """
    handler = create_http_handler(slideshow_manager, websocket_manager)
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"HTTP server running on port {port}")
        httpd.serve_forever()
