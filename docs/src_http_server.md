# HTTP Server

**Module:** `src.http_server`  
**File:** `src/http_server.py`

## Overview

HTTP Server Module for Presentator

This module provides HTTP server functionality with REST API endpoints
for slideshow management, file serving, and PowerPoint conversion.
Handles web interface serving and API communication between frontend and backend.

## Classes

### CustomHTTPRequestHandler

Custom HTTP request handler for Presentator API and web serving.

Extends SimpleHTTPRequestHandler to provide:
- REST API endpoints for slideshow management
- File serving for web interface and slideshow assets
- PowerPoint upload and conversion
- CORS support for cross-origin requests

Attributes:
    slideshow_manager: Instance of SlideShowManager for slideshow operations
    websocket_manager: Instance of WebSocketManager for real-time updates

#### Methods

**`__init__(self, *args, slideshow_manager=None, websocket_manager=None, **kwargs)`**

Initialize the HTTP request handler.

Args:
    slideshow_manager: SlideShowManager instance for slideshow operations
    websocket_manager: WebSocketManager instance for real-time communication
    *args: Positional arguments passed to parent class
    **kwargs: Keyword arguments passed to parent class

**`address_string(self)`**

Return the client address.

**`copyfile(self, source, outputfile)`**

Copy all data between two file objects.

The SOURCE argument is a file object open for reading
(or anything with a read() method) and the DESTINATION
argument is a file object open for writing (or
anything with a write() method).

The only reason for overriding this would be to change
the block size or perhaps to replace newlines by CRLF
-- note however that this the default server uses this
to copy binary data as well.

**`date_time_string(self, timestamp=None)`**

Return the current date and time formatted for a message header.

**`do_GET(self)`**

Handle HTTP GET requests.

Routes requests to appropriate handlers:
- /api/* -> API endpoints
- /slideshows/* -> Slideshow asset files
- /* -> Web interface files from /web directory

**`do_HEAD(self)`**

Serve a HEAD request.

**`do_POST(self)`**

Handle HTTP POST requests.

Routes POST requests to API endpoints for data modification operations
like saving slideshows, uploading files, etc.

**`end_headers(self)`**

Send the blank line ending the MIME headers.

**`finish(self)`**

No documentation available.

**`flush_headers(self)`**

No documentation available.

**`guess_type(self, path)`**

Guess the type of a file.

Argument is a PATH (a filename).

Return value is a string of the form type/subtype,
usable for a MIME Content-type header.

The default implementation looks the file's extension
up in the table self.extensions_map, using application/octet-stream
as a default; however it would be permissible (if
slow) to look inside the data to make a better guess.

**`handle(self)`**

Handle multiple requests if necessary.

**`handle_api_request(self)`**

Route API requests to appropriate handler methods.

Supported endpoints:
- /api/slideshows: Get list of available slideshows
- /api/save_slideshow: Save slideshow data
- /api/load_slideshow: Load specific slideshow
- /api/delete_slideshow: Delete slideshow
- /api/upload_pptx: Upload and convert PowerPoint files

Handles exceptions and returns appropriate HTTP error codes.

**`handle_delete_slideshow(self)`**

Handle POST /api/delete_slideshow endpoint.

Deletes a slideshow from the file system and updates all connected clients.

Request Body:
    JSON object with 'id' field containing slideshow identifier
    
Response:
    200: Success confirmation
    400: Bad request (missing ID or delete error)

**`handle_expect_100(self)`**

Decide what to do with an "Expect: 100-continue" header.

If the client is expecting a 100 Continue response, we must
respond with either a 100 Continue or a final response before
waiting for the request body. The default is to always respond
with a 100 Continue. You can behave differently (for example,
reject unauthorized requests) by overriding this method.

This method should either return True (possibly after sending
a 100 Continue response) or send an error response and return
False.

**`handle_get_slideshows(self)`**

Handle GET /api/slideshows endpoint.

Returns a JSON list of all available slideshows in the system.
Also updates connected WebSocket clients with the current slideshow list.

Response:
    200: JSON array of slideshow objects
    500: Internal server error

**`handle_load_slideshow(self)`**

Handle GET/POST /api/load_slideshow endpoint.

GET: Returns the most recently modified slideshow
POST: Loads specific slideshow by filename

For POST requests:
    Request Body: JSON with 'filename' field
    
Response:
    200: JSON slideshow data
    400: Bad request (missing filename for POST)
    404: Slideshow not found

**`handle_one_request(self)`**

Handle a single HTTP request.

You normally don't need to override this method; see the class
__doc__ string for information on how to handle specific HTTP
commands such as GET and POST.

**`handle_save_slideshow(self)`**

Handle POST /api/save_slideshow endpoint.

Saves slideshow data to file system. Expects JSON payload with
slideshow data and optional filename.

Request Body:
    JSON object containing slideshow data and optional filename
    
Response:
    200: Success with filepath
    400: Bad request (invalid JSON or save error)

**`handle_upload_pptx(self)`**

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

**`list_directory(self, path)`**

Helper to produce a directory listing (absent index.html).

Return value is either a file object, or None (indicating an
error).  In either case, the headers are sent, making the
interface the same as for send_head().

**`log_date_time_string(self)`**

Return the current time formatted for logging.

**`log_error(self, format, *args)`**

Log an error.

This is called when a request cannot be fulfilled.  By
default it passes the message on to log_message().

Arguments are the same as for log_message().

XXX This should go to the separate error log.

**`log_message(self, format, *args)`**

Log an arbitrary message.

This is used by all other logging functions.  Override
it if you have specific logging wishes.

The first argument, FORMAT, is a format string for the
message to be logged.  If the format string contains
any % escapes requiring parameters, they should be
specified as subsequent arguments (it's just like
printf!).

The client ip and current date/time are prefixed to
every message.

Unicode control characters are replaced with escaped hex
before writing the output to stderr.

**`log_request(self, code='-', size='-')`**

Log an accepted request.

This is called by send_response().

**`parse_request(self)`**

Parse a request (internal).

The request should be stored in self.raw_requestline; the results
are in self.command, self.path, self.request_version and
self.headers.

Return True for success, False for failure; on failure, any relevant
error response has already been sent back.

**`send_error(self, code, message=None, explain=None)`**

Send and log an error reply.

Arguments are
* code:    an HTTP error code
           3 digits
* message: a simple optional 1 line reason phrase.
           *( HTAB / SP / VCHAR / %x80-FF )
           defaults to short entry matching the response code
* explain: a detailed message defaults to the long entry
           matching the response code.

This sends an error response (so it must be called before any
output has been generated), logs the error, and finally sends
a piece of HTML explaining the error to the user.

**`send_head(self)`**

Common code for GET and HEAD commands.

This sends the response code and MIME headers.

Return value is either a file object (which has to be copied
to the outputfile by the caller unless the command was HEAD,
and must be closed by the caller under all circumstances), or
None, in which case the caller has nothing further to do.

**`send_header(self, keyword, value)`**

Send a MIME header to the headers buffer.

**`send_response(self, code, message=None)`**

Add the response header to the headers buffer and log the
response code.

Also send two standard headers with the server software
version and the current date.

**`send_response_only(self, code, message=None)`**

Send the response header only.

**`serve_slideshow_files(self)`**

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

**`setup(self)`**

No documentation available.

**`translate_path(self, path)`**

Translate a /-separated PATH to the local filename syntax.

Components that mean special things to the local file system
(e.g. drive or directory names) are ignored.  (XXX They should
probably be diagnosed.)

**`version_string(self)`**

Return the server software version string.


## Functions

### create_http_handler(slideshow_manager, websocket_manager)

Create HTTP handler factory with dependency injection.

Returns a handler class factory that creates CustomHTTPRequestHandler
instances with the provided slideshow and websocket managers injected.

Args:
    slideshow_manager: SlideShowManager instance for slideshow operations
    websocket_manager: WebSocketManager instance for real-time communication
    
Returns:
    Handler factory function that creates configured request handlers

### start_http_server(port=50000, slideshow_manager=None, websocket_manager=None)

Start the HTTP server on specified port.

Creates and starts a TCP server with the custom HTTP handler.
Blocks execution until server is stopped.

Args:
    port (int): Port number to listen on (default: 50000)
    slideshow_manager: SlideShowManager instance for slideshow operations
    websocket_manager: WebSocketManager instance for real-time communication
    
Note:
    This function blocks and runs the server indefinitely until interrupted.

## Source File Statistics

- **Total Lines:** 453
- **Code Lines:** 357
- **Functions:** 13
- **Classes:** 1
- **File Size:** 18662 bytes


---
*Generated by Presentator documentation generator*
