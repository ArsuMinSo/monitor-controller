"""
Presentation Queue Management Module for Presentator

This module provides the PresentationQueueManager class which handles
queuing multiple slideshows for automatic sequential playback.
Supports adding, removing, reordering, and looping through presentations.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional


class PresentationQueueManager:
    """
    Manages presentation queue for automatic slideshow playback.
    
    Handles queue operations including adding/removing slideshows,
    controlling playback order, loop functionality, and queue persistence.
    
    Attributes:
        queue (list): List of slideshow IDs in playback order
        current_index (int): Index of currently playing slideshow in queue
        is_playing (bool): Whether queue is currently playing
        loop_enabled (bool): Whether to loop back to start when queue ends
        queue_file (Path): Path to queue persistence file
    """
    
    def __init__(self, queue_file="queue.json"):
        """
        Initialize the PresentationQueueManager.
        
        Args:
            queue_file (str): Filename for queue persistence
        """
        self.queue = []
        self.current_index = 0
        self.is_playing = False
        self.loop_enabled = False
        self.queue_file = Path(queue_file)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Load saved queue if it exists
        self.load_queue()
        self.logger.debug("PresentationQueueManager initialized")
    
    def add_to_queue(self, slideshow_id: str) -> bool:
        """
        Add a slideshow to the end of the queue.
        
        Args:
            slideshow_id (str): ID of slideshow to add
            
        Returns:
            bool: True if added successfully, False if already in queue
        """
        if slideshow_id not in self.queue:
            self.queue.append(slideshow_id)
            self.save_queue()
            self.logger.info(f"Added slideshow '{slideshow_id}' to queue at position {len(self.queue)}")
            return True
        else:
            self.logger.warning(f"Slideshow '{slideshow_id}' already in queue")
            return False
    
    def remove_from_queue(self, slideshow_id: str) -> bool:
        """
        Remove a slideshow from the queue.
        
        Args:
            slideshow_id (str): ID of slideshow to remove
            
        Returns:
            bool: True if removed successfully, False if not in queue
        """
        try:
            removed_index = self.queue.index(slideshow_id)
            self.queue.remove(slideshow_id)
            
            # Adjust current_index if needed
            if removed_index < self.current_index:
                self.current_index -= 1
            elif removed_index == self.current_index and self.current_index >= len(self.queue):
                self.current_index = max(0, len(self.queue) - 1)
            
            self.save_queue()
            self.logger.info(f"Removed slideshow '{slideshow_id}' from queue")
            return True
        except ValueError:
            self.logger.warning(f"Slideshow '{slideshow_id}' not found in queue")
            return False
    
    def reorder_queue(self, new_order: List[str]) -> bool:
        """
        Reorder the queue with a new sequence.
        
        Args:
            new_order (List[str]): New queue order as list of slideshow IDs
            
        Returns:
            bool: True if reordered successfully
        """
        # Validate that new_order contains same items as current queue
        if set(new_order) == set(self.queue):
            current_slideshow = self.get_current_slideshow()
            self.queue = new_order
            
            # Update current_index to maintain current slideshow
            if current_slideshow and current_slideshow in self.queue:
                self.current_index = self.queue.index(current_slideshow)
            
            self.save_queue()
            self.logger.info("Queue reordered successfully")
            return True
        else:
            self.logger.error("Invalid reorder: new order doesn't match current queue items")
            return False
    
    def move_in_queue(self, slideshow_id: str, new_position: int) -> bool:
        """
        Move a slideshow to a specific position in the queue.
        
        Args:
            slideshow_id (str): ID of slideshow to move
            new_position (int): New position (0-based index)
            
        Returns:
            bool: True if moved successfully
        """
        try:
            if slideshow_id not in self.queue:
                return False
            
            # Remove from current position
            old_index = self.queue.index(slideshow_id)
            self.queue.pop(old_index)
            
            # Insert at new position
            new_position = max(0, min(new_position, len(self.queue)))
            self.queue.insert(new_position, slideshow_id)
            
            # Adjust current_index
            if old_index == self.current_index:
                self.current_index = new_position
            elif old_index < self.current_index <= new_position:
                self.current_index -= 1
            elif new_position <= self.current_index < old_index:
                self.current_index += 1
            
            self.save_queue()
            self.logger.info(f"Moved '{slideshow_id}' from position {old_index} to {new_position}")
            return True
        except Exception as e:
            self.logger.error(f"Error moving slideshow in queue: {e}")
            return False
    
    def clear_queue(self) -> None:
        """Clear all items from the queue."""
        self.queue.clear()
        self.current_index = 0
        self.is_playing = False
        self.save_queue()
        self.logger.info("Queue cleared")
    
    def get_current_slideshow(self) -> Optional[str]:
        """
        Get the currently selected slideshow in the queue.
        
        Returns:
            Optional[str]: Current slideshow ID or None if queue is empty
        """
        if 0 <= self.current_index < len(self.queue):
            return self.queue[self.current_index]
        return None
    
    def next_slideshow(self) -> Optional[str]:
        """
        Advance to the next slideshow in the queue.
        
        Returns:
            Optional[str]: Next slideshow ID or None if at end
        """
        if not self.queue:
            return None
        
        if self.current_index < len(self.queue) - 1:
            self.current_index += 1
        elif self.loop_enabled:
            self.current_index = 0
        else:
            # At end of queue without loop
            self.is_playing = False
            self.save_queue()
            self.logger.info("Reached end of queue, stopping playback")
            return None
        
        current = self.get_current_slideshow()
        self.save_queue()
        self.logger.info(f"Advanced to next slideshow: {current}")
        return current
    
    def previous_slideshow(self) -> Optional[str]:
        """
        Go back to the previous slideshow in the queue.
        
        Returns:
            Optional[str]: Previous slideshow ID or None if at start
        """
        if not self.queue:
            return None
        
        if self.current_index > 0:
            self.current_index -= 1
        elif self.loop_enabled:
            self.current_index = len(self.queue) - 1
        else:
            # At start of queue
            return None
        
        current = self.get_current_slideshow()
        self.save_queue()
        self.logger.info(f"Went back to previous slideshow: {current}")
        return current
    
    def start_queue(self) -> Optional[str]:
        """
        Start playing the queue from the beginning.
        
        Returns:
            Optional[str]: First slideshow ID or None if queue is empty
        """
        if not self.queue:
            self.logger.warning("Cannot start queue: queue is empty")
            return None
        
        self.current_index = 0
        self.is_playing = True
        self.save_queue()
        
        current = self.get_current_slideshow()
        self.logger.info(f"Started queue playback with: {current}")
        return current
    
    def stop_queue(self) -> None:
        """Stop queue playback."""
        self.is_playing = False
        self.save_queue()
        self.logger.info("Queue playback stopped")
    
    def toggle_loop(self) -> bool:
        """
        Toggle loop mode for the queue.
        
        Returns:
            bool: New loop state
        """
        self.loop_enabled = not self.loop_enabled
        self.save_queue()
        self.logger.info(f"Queue loop {'enabled' if self.loop_enabled else 'disabled'}")
        return self.loop_enabled
    
    def get_queue_state(self) -> Dict:
        """
        Get complete queue state for broadcasting.
        
        Returns:
            Dict: Complete queue state including items, current position, and settings
        """
        return {
            "queue": self.queue.copy(),
            "current_index": self.current_index,
            "current_slideshow": self.get_current_slideshow(),
            "is_playing": self.is_playing,
            "loop_enabled": self.loop_enabled,
            "queue_length": len(self.queue)
        }
    
    def save_queue(self) -> None:
        """Save current queue state to file for persistence."""
        try:
            queue_data = {
                "queue": self.queue,
                "current_index": self.current_index,
                "is_playing": self.is_playing,
                "loop_enabled": self.loop_enabled
            }
            
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue_data, f, indent=2, ensure_ascii=False)
                
            self.logger.debug("Queue state saved to file")
            self.load_queue()  # Reload to ensure consistency
        except Exception as e:
            self.logger.error(f"Error saving queue: {e}")
    
    def load_queue(self) -> None:
        """Load queue state from file if it exists."""
        try:
            if self.queue_file.exists():
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    queue_data = json.load(f)
                
                self.queue = queue_data.get("queue", [])
                self.current_index = queue_data.get("current_index", 0)
                self.is_playing = queue_data.get("is_playing", False)
                self.loop_enabled = queue_data.get("loop_enabled", False)
                
                # Validate current_index
                if self.current_index >= len(self.queue):
                    self.current_index = max(0, len(self.queue) - 1)
                
                self.logger.info(f"Loaded queue with {len(self.queue)} items")
            else:
                self.logger.debug("No saved queue found, starting with empty queue")
        except Exception as e:
            self.logger.error(f"Error loading queue: {e}")
            # Reset to defaults on error
            self.queue = []
            self.current_index = 0
            self.is_playing = False
            self.loop_enabled = False
