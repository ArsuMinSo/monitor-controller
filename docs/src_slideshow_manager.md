# Slideshow Manager

**Module:** `src.slideshow_manager`  
**File:** `src/slideshow_manager.py`

## Overview

Slideshow Management Module for Presentator

This module provides the SlideShowManager class which handles all slideshow
operations including discovery, loading, saving, conversion between formats,
and PowerPoint import functionality.

## Classes

### SlideShowManager

Manages slideshow operations for the Presentator system.

Handles discovery, loading, saving, and conversion of slideshows between
different formats (editor JSON, controller JSON, PowerPoint). Provides
a unified interface for slideshow management across the application.

Attributes:
    slideshows (list): Cached list of discovered slideshows

#### Methods

**`__init__(self)`**

Initialize the SlideShowManager.

Sets up empty slideshow cache that will be populated on first discovery.

**`convert_editor_to_controller_format(self, editor_slides)`**

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

**`convert_pptx_file(self, pptx_path, slideshow_name=None)`**

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

**`delete_slideshow(self, slideshow_id)`**

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

**`discover_slideshows(self)`**

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

**`load_slideshow_by_id(self, slideshow_id)`**

Find and return a slideshow by its ID.

Searches through the cached slideshows list to find a slideshow
with the specified ID.

Args:
    slideshow_id (str): Unique identifier of the slideshow
    
Returns:
    dict or None: Slideshow dictionary if found, None otherwise

**`save_editor_slideshow(self, slideshow_data, filename=None)`**

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


## Functions

### convert_editor_to_controller_format(editor_slides)

Legacy function wrapper.

### delete_slideshow(slideshow_id, slideshows)

Legacy function wrapper.

### discover_slideshows()

Legacy function wrapper.

### load_slideshow_by_id(slideshow_id, slideshows)

Legacy function wrapper.

### save_editor_slideshow(slideshow_data, filename=None)

Legacy function wrapper.

## Source File Statistics

- **Total Lines:** 358
- **Code Lines:** 272
- **Functions:** 12
- **Classes:** 1
- **File Size:** 14822 bytes


---
*Generated by Presentator documentation generator*
