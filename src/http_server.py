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
    
    def __init__(self, *args, slideshow_manager=None, websocket_manager=None, queue_manager=None, **kwargs):
        """
        Initialize the HTTP request handler.
        
        Args:
            slideshow_manager: SlideShowManager instance for slideshow operations
            websocket_manager: WebSocketManager instance for real-time communication
            queue_manager: PresentationQueueManager instance for queue operations
            *args: Positional arguments passed to parent class
            **kwargs: Keyword arguments passed to parent class
        """
        self.slideshow_manager = slideshow_manager
        self.websocket_manager = websocket_manager
        self.queue_manager = queue_manager
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
        - /api/queue: Queue management operations
        - /api/queue/add: Add slideshow to queue
        - /api/queue/remove: Remove slideshow from queue
        - /api/queue/start: Start queue playback
        - /api/queue/stop: Stop queue playback
        - /api/queue/next: Advance to next slideshow
        - /api/queue/previous: Go to previous slideshow
        - /api/queue/toggle_loop: Toggle loop mode
        - /api/queue/reorder: Reorder queue items
        
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
            elif self.path == '/api/queue':
                self.handle_queue_request()
            elif self.path.startswith('/api/queue/'):
                self.handle_queue_action()
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
            if slideshow_id:
                updated_slideshows = self.slideshow_manager.delete_slideshow(slideshow_id)
                # Update all connected clients
                self.websocket_manager.update_slideshows_list(updated_slideshows)
                self.logger.info("WebSocket clients updated with new slideshow list")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode())
                self.logger.info("Delete response sent successfully")
            else:
                self.logger.error("Delete request missing slideshow ID")
                self.send_error(400, "Slideshow ID required")
                
        except Exception as e:
            self.logger.error(f"Delete operation failed: {e}")
            self.logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
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

    def handle_queue_request(self):
        """
        Handle GET /api/queue endpoint.
        
        Returns current queue state including queue items, current position,
        playback status, and loop settings.
        
        Response:
            200: JSON object with complete queue state
            500: Internal server error
        """
        try:
            queue_state = self.queue_manager.get_queue_state()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(queue_state).encode())
            
        except Exception as e:
            self.logger.error(f"Error getting queue state: {e}")
            self.send_error(500, f"Queue error: {e}")

    def handle_queue_action(self):
        """
        Handle queue action endpoints like /api/queue/add, /api/queue/remove, etc.
        
        Routes specific queue actions to appropriate methods based on URL path.
        Supports both GET and POST methods depending on the action.
        
        Endpoints:
            - POST /api/queue/add: Add slideshow to queue
            - POST /api/queue/remove: Remove slideshow from queue
            - POST /api/queue/start: Start queue playback
            - POST /api/queue/stop: Stop queue playback
            - POST /api/queue/next: Advance to next slideshow
            - POST /api/queue/previous: Go to previous slideshow
            - POST /api/queue/toggle_loop: Toggle loop mode
            - POST /api/queue/reorder: Reorder queue items
        """
        try:
            action = self.path.split('/')[-1]  # Get last part of path
            
            if action == 'add':
                self.handle_queue_add()
            elif action == 'remove':
                self.handle_queue_remove()
            elif action == 'start':
                self.handle_queue_start()
            elif action == 'stop':
                self.handle_queue_stop()
            elif action == 'next':
                self.handle_queue_next()
            elif action == 'previous':
                self.handle_queue_previous()
            elif action == 'toggle_loop':
                self.handle_queue_toggle_loop()
            elif action == 'reorder':
                self.handle_queue_reorder()
            else:
                self.send_error(404, f"Queue action '{action}' not found")
                
        except Exception as e:
            self.logger.error(f"Error handling queue action: {e}")
            self.send_error(500, f"Queue action error: {e}")

    def handle_queue_add(self):
        """Add slideshow to queue via POST /api/queue/add"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            slideshow_id = data.get('slideshow_id')
            if not slideshow_id:
                self.send_error(400, "Missing slideshow_id")
                return
            
            success = self.queue_manager.add_to_queue(slideshow_id)
            result = {"success": success, "message": f"Slideshow {'added to' if success else 'already in'} queue"}
            
            # Broadcast updated queue state
            if success:
                self.websocket_manager.broadcast_queue_state_sync(self.queue_manager.get_queue_state())
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.logger.error(f"Error adding to queue: {e}")
            self.send_error(500, f"Add to queue failed: {e}")

    def handle_queue_remove(self):
        """Remove slideshow from queue via POST /api/queue/remove"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            slideshow_id = data.get('slideshow_id')
            if not slideshow_id:
                self.send_error(400, "Missing slideshow_id")
                return
            
            success = self.queue_manager.remove_from_queue(slideshow_id)
            result = {"success": success, "message": f"Slideshow {'removed from' if success else 'not found in'} queue"}
            
            # Broadcast updated queue state
            if success:
                self.websocket_manager.broadcast_queue_state_sync(self.queue_manager.get_queue_state())
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.logger.error(f"Error removing from queue: {e}")
            self.send_error(500, f"Remove from queue failed: {e}")

    def handle_queue_start(self):
        """Start queue playback via POST /api/queue/start"""
        try:
            current_slideshow = self.queue_manager.start_queue()
            result = {
                "success": current_slideshow is not None,
                "current_slideshow": current_slideshow,
                "message": "Queue started" if current_slideshow else "Queue is empty"
            }
            
            # Broadcast updated queue state and switch to slideshow if available
            self.websocket_manager.broadcast_queue_state_sync(self.queue_manager.get_queue_state())
            if current_slideshow:
                # Load and switch to the first slideshow in queue
                slideshow_data = self.slideshow_manager.load_slideshow_by_id(current_slideshow)
                if slideshow_data:
                    self.websocket_manager.current_slideshow = slideshow_data
                    self.websocket_manager.current_slide_index = 0
                    self.websocket_manager.broadcast_state()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.logger.error(f"Error starting queue: {e}")
            self.send_error(500, f"Start queue failed: {e}")

    def handle_queue_stop(self):
        """Stop queue playback via POST /api/queue/stop"""
        try:
            self.queue_manager.stop_queue()
            result = {"success": True, "message": "Queue stopped"}
            
            # Broadcast updated queue state
            self.websocket_manager.broadcast_queue_state_sync(self.queue_manager.get_queue_state())
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.logger.error(f"Error stopping queue: {e}")
            self.send_error(500, f"Stop queue failed: {e}")

    def handle_queue_next(self):
        """Advance to next slideshow via POST /api/queue/next"""
        try:
            next_slideshow = self.queue_manager.next_slideshow()
            result = {
                "success": next_slideshow is not None,
                "current_slideshow": next_slideshow,
                "message": "Advanced to next slideshow" if next_slideshow else "End of queue reached"
            }
            
            # Broadcast updated queue state and switch to slideshow if available
            self.websocket_manager.broadcast_queue_state_sync(self.queue_manager.get_queue_state())
            if next_slideshow:
                slideshow_data = self.slideshow_manager.load_slideshow_by_id(next_slideshow)
                if slideshow_data:
                    self.websocket_manager.current_slideshow = slideshow_data
                    self.websocket_manager.current_slide_index = 0
                    self.websocket_manager.broadcast_state()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.logger.error(f"Error advancing queue: {e}")
            self.send_error(500, f"Queue next failed: {e}")

    def handle_queue_previous(self):
        """Go to previous slideshow via POST /api/queue/previous"""
        try:
            previous_slideshow = self.queue_manager.previous_slideshow()
            result = {
                "success": previous_slideshow is not None,
                "current_slideshow": previous_slideshow,
                "message": "Went to previous slideshow" if previous_slideshow else "At start of queue"
            }
            
            # Broadcast updated queue state and switch to slideshow if available
            self.websocket_manager.broadcast_queue_state_sync(self.queue_manager.get_queue_state())
            if previous_slideshow:
                slideshow_data = self.slideshow_manager.load_slideshow_by_id(previous_slideshow)
                if slideshow_data:
                    self.websocket_manager.current_slideshow = slideshow_data
                    self.websocket_manager.current_slide_index = 0
                    self.websocket_manager.broadcast_state()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.logger.error(f"Error going to previous: {e}")
            self.send_error(500, f"Queue previous failed: {e}")

    def handle_queue_toggle_loop(self):
        """Toggle queue loop mode via POST /api/queue/toggle_loop"""
        try:
            loop_enabled = self.queue_manager.toggle_loop()
            result = {
                "success": True,
                "loop_enabled": loop_enabled,
                "message": f"Loop {'enabled' if loop_enabled else 'disabled'}"
            }
            
            # Broadcast updated queue state
            self.websocket_manager.broadcast_queue_state_sync(self.queue_manager.get_queue_state())
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.logger.error(f"Error toggling loop: {e}")
            self.send_error(500, f"Toggle loop failed: {e}")

    def handle_queue_reorder(self):
        """Reorder queue via POST /api/queue/reorder"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            new_order = data.get('queue_order')
            if not new_order or not isinstance(new_order, list):
                self.send_error(400, "Missing or invalid queue_order (must be array)")
                return
            
            success = self.queue_manager.reorder_queue(new_order)
            result = {
                "success": success,
                "message": "Queue reordered successfully" if success else "Invalid reorder request"
            }
            
            # Broadcast updated queue state
            if success:
                self.websocket_manager.broadcast_queue_state_sync(self.queue_manager.get_queue_state())
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.logger.error(f"Error reordering queue: {e}")
            self.send_error(500, f"Reorder queue failed: {e}")

def create_http_handler(slideshow_manager, websocket_manager, queue_manager):
    """
    Create HTTP handler factory with dependency injection.
    
    Returns a handler class factory that creates CustomHTTPRequestHandler
    instances with the provided slideshow and websocket managers injected.
    
    Args:
        slideshow_manager: SlideShowManager instance for slideshow operations
        websocket_manager: WebSocketManager instance for real-time communication
        queue_manager: PresentationQueueManager instance for queue operations
        
    Returns:
        Handler factory function that creates configured request handlers
    """
    def handler(*args, **kwargs):
        return CustomHTTPRequestHandler(*args, slideshow_manager=slideshow_manager, 
                                      websocket_manager=websocket_manager, queue_manager=queue_manager, **kwargs)
    return handler


def start_http_server(port=50000, slideshow_manager=None, websocket_manager=None, queue_manager=None):
    """
    Start the HTTP server on specified port.
    
    Creates and starts a TCP server with the custom HTTP handler.
    Blocks execution until server is stopped.
    
    Args:
        port (int): Port number to listen on (default: 50000)
        slideshow_manager: SlideShowManager instance for slideshow operations
        websocket_manager: WebSocketManager instance for real-time communication
        queue_manager: PresentationQueueManager instance for queue operations
        
    Note:
        This function blocks and runs the server indefinitely until interrupted.
    """
    handler = create_http_handler(slideshow_manager, websocket_manager, queue_manager)
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"HTTP server running on port {port}")
        httpd.serve_forever()
