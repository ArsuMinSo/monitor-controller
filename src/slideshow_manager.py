"""
Slideshow Management Module for Presentator

This module provides the SlideShowManager class which handles all slideshow
operations including discovery, loading, saving, conversion between formats,
and PowerPoint import functionality.
"""

import json
import os
import logging
from pathlib import Path
from .pptx_parse import convert_pptx_file_free
from .utils import log


class SlideShowManager:
    """
    Manages slideshow operations for the Presentator system.
    
    Handles discovery, loading, saving, and conversion of slideshows between
    different formats (editor JSON, controller JSON, PowerPoint). Provides
    a unified interface for slideshow management across the application.
    
    Attributes:
        slideshows (list): Cached list of discovered slideshows
    """
    
    def __init__(self):
        """
        Initialize the SlideShowManager.
        
        Sets up empty slideshow cache that will be populated on first discovery.
        """
        self.slideshows = []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.debug("SlideShowManager initialized")
    
    def discover_slideshows(self):
        """
        Scan slideshows directory and discover available presentations.
        
        Searches the slideshows directory for JSON files containing slideshow data
        and converts them to a standardized format for the controller interface.
        
        Returns:
            list: List of slideshow dictionaries with standardized format containing:
                - id: Unique identifier for the slideshow
                - name: Display name of the slideshow
                - config: Configuration settings (theme, autoplay, loop)
                - slides: Array of slide data
                - path: File system path to slideshow file
                - type: Slideshow type ("editor", "controller", etc.)
                - original_data: Raw slideshow data from file
        
        Note:
            Creates slideshows directory if it doesn't exist.
        """
        slideshows_dir = Path("slideshows")
        slideshows = []
        
        if not slideshows_dir.exists():
            slideshows_dir.mkdir()
            return slideshows
          
        # Load editor-based slideshows (JSON format)
        for slideshow_file in slideshows_dir.glob("*_editor.json"):
            try:
                with open(slideshow_file, 'r', encoding='utf-8') as f:
                    editor_data = json.load(f)
                
                # Convert editor format to controller format
                converted_slides = self.convert_editor_to_controller_format(editor_data.get('slides', []))
                
                slideshow = {
                    "id": slideshow_file.stem,  # filename without extension
                    "name": editor_data.get('name', slideshow_file.stem.replace('_editor', '')),
                    "config": {
                        "theme": "default",
                        "autoplay": True,
                        "loop": True
                    },
                    "slides": converted_slides,
                    "path": str(slideshow_file),
                    "type": "editor",
                    "original_data": editor_data
                }
                slideshows.append(slideshow)
                
            except Exception as e:
                print(f"Error loading editor slideshow {slideshow_file}: {e}")
        
        for slideshow_dir in slideshows_dir.glob("*"):
            if slideshow_dir.is_dir() and (slideshow_dir / "slideshow.json").exists():
                try:
                    with open(slideshow_dir / "slideshow.json", 'r', encoding='utf-8') as f:
                        slideshow_data = json.load(f)
                    
                    slideshow = {
                        "id": slideshow_data.get("name", slideshow_dir.name),
                        "name": slideshow_data.get("name", slideshow_dir.name),
                        "slides": slideshow_data.get("slides", []),
                        "path": str(slideshow_dir),
                        "type": "markdown",
                        "config": {
                            "theme": "default",
                            "autoplay": True,
                            "loop": True
                        }
                    }
                    slideshows.append(slideshow)
                    
                except Exception as e:
                    print(f"Error loading markdown slideshow {slideshow_dir}: {e}")


        self.slideshows = slideshows
        return slideshows

    def convert_editor_to_controller_format(self, editor_slides):
        """
        Convert WYSIWYG editor slides to controller-compatible format.
        
        Transforms slide data from the editor format (used by the web editor)
        to the controller format (used by the viewer and controller interfaces).
        
        Args:
            editor_slides (list): List of slide dictionaries from editor format
            
        Returns:
            list: List of slide dictionaries in controller format with fields:
                - content: HTML content for display
                - html: HTML content (duplicate for compatibility)
                - duration: Display duration in seconds
                - background: Background color
                - bgColor: Background color (duplicate for compatibility)
                - slide_number: Sequential slide number
                - type: Slide type ("html")
        """
        converted_slides = []
        
        for i, slide in enumerate(editor_slides):
            # Extract text content from HTML
            html_content = slide.get('html', '')
            duration = slide.get('duration', 6)
            bg_color = slide.get('bgColor', '#f7ecd0')
            
            # If content is just plain text without HTML tags, wrap it in a paragraph
            if html_content and not '<' in html_content and html_content.strip():
                html_content = f'<p>{html_content}</p>'
            
            # Create a controller-compatible slide
            controller_slide = {
                "content": html_content,  # Keep original HTML
                "html": html_content,     # For direct HTML rendering
                "duration": duration,
                "background": bg_color,
                "bgColor": bg_color,      # Also keep bgColor for compatibility
                "slide_number": i + 1,
                "type": "html"  # Mark as HTML content
            }
            
            converted_slides.append(controller_slide)
        
        return converted_slides

    def load_slideshow_by_id(self, slideshow_id):
        """
        Find and return a slideshow by its ID.
        
        Searches through the cached slideshows list to find a slideshow
        with the specified ID.
        
        Args:
            slideshow_id (str): Unique identifier of the slideshow
            
        Returns:
            dict or None: Slideshow dictionary if found, None otherwise
        """
        for slideshow in self.slideshows:
            if slideshow["id"] == slideshow_id:
                return slideshow
        return None

    def save_editor_slideshow(self, slideshow_data, filename=None):
        """
        Save an editor slideshow to JSON format.
        
        Saves slideshow data from the editor interface to a JSON file in the
        slideshows directory with proper naming conventions.
        
        Args:
            slideshow_data (dict): Slideshow data from editor interface
            filename (str, optional): Custom filename. If not provided, generates
                filename from slideshow name with "_editor.json" suffix
                
        Returns:
            str: Full file path where the slideshow was saved
            
        Note:
            Automatically creates slideshows directory if it doesn't exist.
            Ensures filename ends with "_editor.json" for consistency.
        """
        slideshows_dir = Path("slideshows")
        slideshows_dir.mkdir(exist_ok=True)
        
        # Ensure filename has proper _editor.json suffix
        if filename and filename.endswith('_editor.json'):
            # Filename is already correct, use as-is
            pass
        elif filename:
            # Clean up existing extensions and add _editor.json
            if filename.endswith('.json'):
                filename = filename[:-5] + '_editor.json'
            elif filename.endswith('_editor'):
                filename = filename + '.json'
            else:
                filename = f"{filename}_editor.json"
        else:
            # No filename provided, generate from slideshow name
            name = slideshow_data.get('name', 'Untitled Slideshow')
            clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{clean_name}_editor.json"
        
        filepath = slideshows_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(slideshow_data, f, indent=2, ensure_ascii=False)
        
        try:
            self._compare_and_save(slideshows_dir / "00_loop_editor.json", slideshow_data)
        except Exception as e:
            print(f"Error updating 00_loop_editor.json: {e}")
        
        return str(filepath)

    def delete_slideshow(self, slideshow_id):
        """
        Delete a slideshow file and return updated slideshows list.
        
        Removes the slideshow file from the file system and cleans up any
        associated resources (image directories, etc.). Returns updated
        slideshow list after deletion.
        
        Args:
            slideshow_id (str): Unique identifier of slideshow to delete
            
        Returns:
            list: Updated list of slideshows after deletion
            
        Note:
            For editor slideshows, also removes associated image directories.
            For markdown slideshows, removes entire slideshow directory.
        """
        self.discover_slideshows()
        slideshow = self.load_slideshow_by_id(slideshow_id)
        if not slideshow:
            return self.slideshows
        
        try:
            # Delete the file
            slideshow_path = Path(slideshow['path'])
            if slideshow_path.exists():
                if slideshow['type'] == 'editor':
                    # Delete JSON file
                    self.logger.info(f"Deleting slideshow file: {slideshow_path}")  
                    os.remove(slideshow_path)               
                    
                    # Also delete associated image directory if it exists
                    slideshow_name = slideshow.get('name', slideshow_id)
                    # Clean name for file system (same as in pptx_parse.py)
                    clean_name = "".join(c for c in slideshow_name if c.isalnum() or c in (' ', '-', '_')).strip()
                    presentation_name = clean_name.replace(' ', '_')
                    
                    image_dir = slideshow_path.parent / f"{presentation_name}_images"
                    if image_dir.exists() and image_dir.is_dir():
                        import shutil
                        shutil.rmtree(image_dir)
                else:
                    # Delete markdown directory
                    import shutil
                    shutil.rmtree(slideshow_path)
            
            # Return updated list without the deleted slideshow
            self.slideshows = [s for s in self.slideshows if s['id'] != slideshow_id]
            return self.slideshows
            
        except Exception as e:
            print(f"Error deleting slideshow {slideshow_id}: {e}")
            return self.slideshows

    def convert_pptx_file(self, pptx_path, slideshow_name=None):
        """
        Convert PowerPoint file to slideshow format.
        
        Converts a PPTX file to the editor JSON format, extracts images,
        and makes the slideshow available in the system.
        
        Args:
            pptx_path (Path or str): Path to the PowerPoint file
            slideshow_name (str, optional): Name for the converted slideshow.
                If not provided, uses filename
                
        Returns:
            dict: Conversion result with fields:
                - success (bool): Whether conversion succeeded
                - message (str): Success/error message
                - slide_count (int): Number of slides converted (if successful)
                - output_path (str): Path to saved slideshow file (if successful)
        """
        try:
            output_path = convert_pptx_file_free(pptx_path, slideshow_name)
            
            # Refresh slideshows list
            self.discover_slideshows()
            
            # Count slides from the saved file
            with open(output_path, 'r', encoding='utf-8') as f:
                slideshow_data = json.load(f)
                slide_count = len(slideshow_data.get('slides', []))
            
            return {
                "success": True,
                "slideshow_name": slideshow_data.get('name', 'Converted Slideshow'),
                "slide_count": slide_count,
                "message": f"Converted {slide_count} slides successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _sterilize_input(self, input_str):
        """
        Create a filesystem-safe output from a given input.
        
        Args:
            input_str (str): Original input string
            
        Returns:
            str: Sanitized input
        """
        clean_input = "".join(c for c in input_str if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return clean_input.replace(' ', '_')
    
    def _compare_and_save(self, existing_file, new_data):
        """
        Compare new file with existing 00_loop_editor.json.
        Replace slides for the same presentation name, or append if not present.
        All slides get a div with presentation name.
        """
        # Load or initialize loop file
        if existing_file.exists():
            with open(existing_file, 'r', encoding='utf-8') as f:
                try:
                    old_data = json.load(f)
                except Exception:
                    old_data = {"presentations": [], "slides": []}
        else:
            old_data = {"presentations": [], "slides": []}

        presentations = old_data.get('presentations', [])
        slides = old_data.get('slides', [])
        new_name = new_data.get('name', 'N/A')
        # Remove old slides for this presentation
        slides = [s for s in slides if s.get('presentation') != new_name]
        # Add new slides with div tag and presentation name
        for slide in new_data.get('slides', []):
            content = slide.get('content', '')
            # Replace any div with new div
            import re
            content = re.sub(r'<div[^>]*>(.*?)</div>', r'\1', content, flags=re.DOTALL)
            content = f'<div name="{new_name}">{content}</div>'
            slide['content'] = content
            slide['presentation'] = new_name
            slides.append(slide)
        # Update presentations list
        if new_name not in presentations:
            presentations.append(new_name)
        # Save back
        with open(existing_file, 'w', encoding='utf-8') as f:
            json.dump({"name": "Loop presentations", "presentations": presentations, "slides": slides}, f, ensure_ascii=False, indent=4)
        return True

# Legacy function support for backwards compatibility
def discover_slideshows():
    """Legacy function wrapper."""
    manager = SlideShowManager()
    return manager.discover_slideshows()

def convert_editor_to_controller_format(editor_slides):
    """Legacy function wrapper."""
    manager = SlideShowManager()
    return manager.convert_editor_to_controller_format(editor_slides)

def load_slideshow_by_id(slideshow_id, slideshows):
    """Legacy function wrapper."""
    manager = SlideShowManager()
    manager.slideshows = slideshows
    return manager.load_slideshow_by_id(slideshow_id)

def save_editor_slideshow(slideshow_data, filename=None):
    """Legacy function wrapper."""
    manager = SlideShowManager()
    return manager.save_editor_slideshow(slideshow_data, filename)

def delete_slideshow(slideshow_id, slideshows):
    """Legacy function wrapper."""
    manager = SlideShowManager()
    manager.slideshows = slideshows
    return manager.delete_slideshow(slideshow_id)