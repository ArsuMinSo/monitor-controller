"""
WebSocket Management Module for Presentator

This module provides the WebSocketManager class which handles real-time
communication between the server and connected clients (viewers and controllers).
Manages connection state, broadcasting, and message handling for synchronized
slideshow control across multiple devices.
"""

import asyncio
import websockets
import json
import logging
import datetime
import socket


class WebSocketManager:
    """
    Manages WebSocket connections and real-time state broadcasting.
    
    Handles all WebSocket communication for the Presentator system, including
    client connection management, state synchronization, and message broadcasting
    to all connected viewers and controllers.
    
    Attributes:
        clients (set): Set of active WebSocket connections
        current_state (dict): Current system state including:
            - current_slideshow: Active slideshow data
            - current_slide: Current slide index
            - slideshows: List of available slideshows
            - playing: Playback status
    """
    
    def __init__(self):
        """
        Initialize the WebSocketManager.
        
        Sets up empty client set and initial state with no active slideshow.
        Also initializes client information tracking for monitoring connected clients.
        """
        self.clients = set()
        self.client_info = {}  # Store client information with IP, connect time, etc.
        self.current_state = {
            "current_slideshow": None,
            "current_slide": 0,
            "slideshows": [],
            "playing": False
        }
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug("WebSocketManager initialized")

    
    async def broadcast_state(self):
        """
        Broadcast current state to all connected clients.
        
        Sends the current system state (slideshow, slide index, playback status)
        to all connected WebSocket clients. Automatically removes disconnected
        clients from the client set.
        
        Note:
            Creates a copy of clients set to avoid modification during iteration.
            Handles connection errors gracefully by removing failed connections.
        """
        if not self.clients:
            return
        
        message = json.dumps({
            "type": "state_update",
            "current_slideshow": self.current_state["current_slideshow"],
            "current_slide": self.current_state["current_slide"],
            "playing": self.current_state["playing"]
        })
        
        # Create a copy of clients to avoid issues if set changes during iteration
        clients_copy = self.clients.copy()
        
        for client in clients_copy:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                self.clients.discard(client)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                self.clients.discard(client)


    async def broadcast_slideshows_list(self):
        """
        Broadcast updated slideshows list to all connected clients.
        
        Sends the current list of available slideshows to all connected clients.
        Used when slideshows are added, removed, or modified to keep all
        interfaces synchronized.
        
        Note:
            Only broadcasts if there are connected clients.
            Handles connection errors by removing failed connections.
        """
        if not self.clients:
            return
        
        message = json.dumps({
            "type": "slideshows_update",
            "slideshows": self.current_state["slideshows"]
        })
        
        # Create a copy of clients to avoid issues if set changes during iteration
        clients_copy = self.clients.copy()
        
        for client in clients_copy:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                self.clients.discard(client)
            except Exception as e:
                print(f"Error broadcasting slideshows to client: {e}")
                self.clients.discard(client)


    async def handle_client(self, websocket):
        """
        Handle new WebSocket client connections.
        
        Manages the lifecycle of a WebSocket client connection, including:
        - Adding client to active connections set
        - Tracking client information (IP address, connection time)
        - Sending initial state to new client
        - Processing incoming messages and commands
        - Cleaning up on disconnection
        
        Args:
            websocket: WebSocket connection object
            
        Note:
            This method runs for the duration of the client connection.
            Automatically removes client from set when connection closes.
        """
        # Get client IP address and connection info
        try:
            client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
            client_port = websocket.remote_address[1] if websocket.remote_address else "unknown"
        except Exception:
            client_ip = "unknown"
            client_port = "unknown"
        
        connect_time = datetime.datetime.now()
        
        # Store client information
        client_id = id(websocket)
        self.client_info[client_id] = {
            "ip": client_ip,
            "port": client_port,
            "connect_time": connect_time,
            "websocket": websocket,
            "last_activity": connect_time
        }
        
        self.clients.add(websocket)
        
        self.logger.info(f"Client connected from {client_ip}:{client_port}. Total clients: {len(self.clients)}")
        print(f"Client connected from {client_ip}:{client_port}. Total clients: {len(self.clients)}")
        
        # Display current client list
        self.display_client_info()
        
        try:
            # Send current state to new client
            await websocket.send(json.dumps({
                "type": "state_update",
                "current_slideshow": self.current_state["current_slideshow"],
                "current_slide": self.current_state["current_slide"],
                "playing": self.current_state["playing"]
            }))
            
            async for message in websocket:
                try:
                    # Update last activity time
                    if client_id in self.client_info:
                        self.client_info[client_id]["last_activity"] = datetime.datetime.now()
                    
                    data = json.loads(message)
                    command = data.get("command")
                    params = data.get("params", {})
                    
                    self.logger.debug(f"Command '{command}' received from {client_ip}:{client_port}")
                    await self.handle_command(command, params)
                    
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid JSON received from {client_ip}:{client_port}: {message}")
                    print(f"Invalid JSON received from {client_ip}:{client_port}: {message}")
                except Exception as e:
                    self.logger.error(f"Error handling message from {client_ip}:{client_port}: {e}")
                    print(f"Error handling message from {client_ip}:{client_port}: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Clean up client info
            if client_id in self.client_info:
                del self.client_info[client_id]
            
            self.clients.discard(websocket)
            
            self.logger.info(f"Client {client_ip}:{client_port} disconnected. Total clients: {len(self.clients)}")
            print(f"Client {client_ip}:{client_port} disconnected. Total clients: {len(self.clients)}")
            
            # Display updated client list
            if self.clients:
                self.display_client_info()


    async def handle_command(self, command, params):
        """
        Handle WebSocket commands from clients.
        
        Processes commands received from connected clients and updates system
        state accordingly. Broadcasts state changes to all connected clients.
        
        Supported commands:
            - refresh_slideshows: Reload slideshow list
            - load_slideshow: Load specific slideshow by ID
            - set_slide: Navigate to specific slide
            - play: Start slideshow playback
            - pause: Pause slideshow playback
            - stop: Stop slideshow and reset
            
        Args:
            command (str): Command name
            params (dict): Command parameters
        """
        from .slideshow_manager import load_slideshow_by_id, discover_slideshows
        
        if command == "refresh_slideshows":
            # Refresh the slideshows list
            slideshows = discover_slideshows()
            self.current_state["slideshows"] = slideshows
            # Broadcast the updated slideshows list to all clients
            await self.broadcast_slideshows_list()
            
        elif command == "load_slideshow":
            slideshow_id = params.get("slideshow_id") or params.get("id")
            slideshow = load_slideshow_by_id(slideshow_id, self.current_state["slideshows"])
            if slideshow:
                self.current_state["current_slideshow"] = slideshow
                self.current_state["current_slide"] = 0
                self.current_state["playing"] = False
                await self.broadcast_state()
        
        elif command == "set_slide":
            slide_index = params.get("slide")
            if (self.current_state["current_slideshow"] and 
                0 <= slide_index < len(self.current_state["current_slideshow"]["slides"])):
                self.current_state["current_slide"] = slide_index
                await self.broadcast_state()
        
        elif command == "play":
            self.current_state["playing"] = True
            await self.broadcast_state()
        
        elif command == "pause":
            self.current_state["playing"] = False
            await self.broadcast_state()
        
        elif command == "next_slide":
            if self.current_state["current_slideshow"]:
                total_slides = len(self.current_state["current_slideshow"]["slides"])
                self.current_state["current_slide"] = (self.current_state["current_slide"] + 1) % total_slides
                await self.broadcast_state()
        
        elif command == "prev_slide":
            if self.current_state["current_slideshow"]:
                total_slides = len(self.current_state["current_slideshow"]["slides"])
                self.current_state["current_slide"] = (self.current_state["current_slide"] - 1) % total_slides
                await self.broadcast_state()
        
        elif command == "get_client_info":
            # Return client information (useful for management interfaces)
            stats = self.get_client_stats()
            self.logger.info(f"Client info requested. Current stats: {stats}")
        
        elif command == "show_clients":
            # Display client info in console
            self.display_client_info()


    def display_client_info(self):
        """
        Display information about currently connected clients.
        
        Prints a formatted table showing client details including IP addresses,
        connection times, and activity status.
        """
        if not self.client_info:
            print("No clients currently connected.")
            return
        
        print("\n" + "=" * 80)
        print(f"CONNECTED CLIENTS ({len(self.client_info)})")
        print("=" * 80)
        print(f"{'IP Address':<15} {'Port':<6} {'Connected':<20} {'Last Activity':<20} {'Duration':<10}")
        print("-" * 80)
        
        now = datetime.datetime.now()
        
        for client_id, info in self.client_info.items():
            ip = info['ip']
            port = info['port']
            connect_time = info['connect_time']
            last_activity = info['last_activity']
            
            # Calculate connection duration
            duration = now - connect_time
            duration_str = self._format_duration(duration)
            
            # Format timestamps
            connect_str = connect_time.strftime('%Y-%m-%d %H:%M:%S')
            activity_str = last_activity.strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"{ip:<15} {port:<6} {connect_str:<20} {activity_str:<20} {duration_str:<10}")
        
        print("=" * 80)
    
    def _format_duration(self, duration):
        """Format timedelta as human-readable string"""
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_client_stats(self):
        """
        Get statistics about connected clients.
        
        Returns:
            dict: Client statistics including count, IP addresses, and connection info
        """
        stats = {
            "total_clients": len(self.client_info),
            "clients": []
        }
        
        now = datetime.datetime.now()
        
        for client_id, info in self.client_info.items():
            duration = now - info['connect_time']
            client_stats = {
                "ip": info['ip'],
                "port": info['port'],
                "connected_since": info['connect_time'].isoformat(),
                "last_activity": info['last_activity'].isoformat(),
                "duration_seconds": int(duration.total_seconds()),
                "duration_formatted": self._format_duration(duration)
            }
            stats["clients"].append(client_stats)
        
        return stats
    
    def get_unique_ips(self):
        """
        Get list of unique IP addresses of connected clients.
        
        Returns:
            list: List of unique IP addresses
        """
        return list(set(info['ip'] for info in self.client_info.values()))


    def update_slideshows_list(self, slideshows):
        """
        Update the global slideshows list.
        
        Updates the internal state with a new list of available slideshows.
        This method is called when slideshows are discovered, added, or removed.
        
        Args:
            slideshows (list): List of slideshow dictionaries
        """
        self.current_state["slideshows"] = slideshows

    def get_current_state(self):
        """
        Get the current application state.
        
        Returns a copy of the current system state to prevent external
        modification of internal state.
        
        Returns:
            dict: Copy of current state containing slideshow and playback information
        """
        return self.current_state.copy()

    async def start_websocket_server(self, port=50001):
        """
        Start the WebSocket server.
        
        Creates and starts the WebSocket server on the specified port,
        listening on all network interfaces.
        
        Args:
            port (int): Port number to listen on (default: 50001)
            
        Returns:
            Server object from websockets.serve()
            
        Note:
            This method starts the server but doesn't block. Use with asyncio.run()
            or similar to run the server.
        """
        print(f"Starting WebSocket server on port {port}")
        return await websockets.serve(self.handle_client, "0.0.0.0", port)


# Legacy support for backwards compatibility
clients = set()
current_state = {
    "current_slideshow": None,
    "current_slide": 0,
    "slideshows": [],
    "playing": False
}

_default_manager = None

def get_default_manager():
    global _default_manager
    if _default_manager is None:
        _default_manager = WebSocketManager()
    return _default_manager

async def broadcast_state():
    manager = get_default_manager()
    await manager.broadcast_state()

async def broadcast_slideshows_list():
    manager = get_default_manager()
    await manager.broadcast_slideshows_list()

async def handle_client(websocket):
    manager = get_default_manager()
    await manager.handle_client(websocket)

async def handle_command(command, params):
    manager = get_default_manager()
    await manager.handle_command(command, params)

def update_slideshows_list(slideshows):
    manager = get_default_manager()
    manager.update_slideshows_list(slideshows)
    global current_state
    current_state["slideshows"] = slideshows

def get_current_state():
    manager = get_default_manager()
    return manager.get_current_state()

async def start_websocket_server(port=50001):
    manager = get_default_manager()
    return await manager.start_websocket_server(port)
