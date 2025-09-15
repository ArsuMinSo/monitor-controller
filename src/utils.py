"""
Utility Functions Module for Presentator

This module provides common utility functions for network operations,
file handling, and system-level tasks used throughout the Presentator
application. Contains helper functions for IP detection, port management,
and other system utilities.
"""

import socket


def get_local_ip():
    """
    Get the local IP address of this machine.
    
    Determines the local IP address by connecting to a remote server
    and checking the local socket address. Falls back to localhost
    if unable to determine the actual IP.
    
    Returns:
        str: Local IP address (e.g., "192.168.1.100") or "127.0.0.1" as fallback
        
    Note:
        Uses Google's DNS server (8.8.8.8) as a reference point for
        determining the outbound network interface.
    """
    try:
        # Connect to a remote server to get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "127.0.0.1"


def get_available_port(start_port=50000, max_attempts=100):
    """
    Find an available port starting from the specified port number.
    
    Searches for an available TCP port by attempting to bind to sequential
    port numbers starting from the given port. Useful for dynamic port
    allocation when default ports might be in use.
    
    Args:
        start_port (int): Starting port number to check (default: 50000)
        max_attempts (int): Maximum number of ports to try (default: 100)
        
    Returns:
        int: First available port number found
        
    Raises:
        RuntimeError: If no available ports are found in the specified range
        
    Example:
        >>> port = get_available_port(8000, 50)
        >>> print(f"Using port: {port}")
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts}")


def validate_slideshow_data(data):
    """Validate slideshow data structure."""
    required_fields = ['name', 'slides']
    
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(data['slides'], list):
        raise ValueError("Slides must be a list")
    
    for i, slide in enumerate(data['slides']):
        if not isinstance(slide, dict):
            raise ValueError(f"Slide {i} must be a dictionary")
        
        if 'html' not in slide:
            raise ValueError(f"Slide {i} missing 'html' field")
    
    return True

def log(message, level='INFO'):
    """
    Simple logging function to print messages with a level prefix.
    
    Args:
        message (str): The message to log
        level (str): Log level (e.g., 'INFO', 'ERROR', 'DEBUG')
        
    Example:
        >>> log("Application started", "INFO")
        INFO: Application started
    """
    print(f"\n\t{level}: {message}\n")

def sterile_filename(filename):
    """
    Sanitize a filename by removing potentially unsafe characters.
    
    Args:
        filename (str): The original filename
        
    Returns:
        str: Sanitized filename safe for filesystem use
        
    Example:
        >>> sterile_filename("my*file?.txt")
        'myfile.txt'
    """
    import re
    return re.sub(r'[^a-zA-Z0-9_.-]', '', filename)

def sterile_string(s):
    """
    Sanitize a string by removing potentially unsafe characters.
    
    Args:
        s (str): The original string
        
    Returns:
        str: Sanitized string safe for general use
        
    Example:
        >>> sterile_string("Hello, World!")
        'Hello World'
    """
    import re
    return re.sub(r'[^a-zA-Z0-9\s]', '', s)