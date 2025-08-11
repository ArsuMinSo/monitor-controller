# Controller Tutorial

## Overview

The Slideshow Controller is the central command interface for managing and presenting slideshows. It provides real-time control over presentations, slideshow management, PowerPoint import, and viewer synchronization across multiple devices on your network.

## Accessing the Controller

Open your web browser and navigate to controller

## Interface Overview

### Connection Status
- **Connected/Disconnected**: Shows WebSocket connection status to the server
- **Real-time Updates**: Automatically refreshes when connection is established

### Current Status Panel
- **Active Slideshow**: Name of currently loaded presentation
- **Current Slide**: Shows current slide number and total slides (e.g., "3 / 15")
- **Status**: Playing or Stopped state
- **Timer**: Countdown timer showing remaining time for current slide

## Main Control Functions

### Presentation Controls
- <img src="../../web/icons/play.svg" alt="Play" width="20" height="20" style="vertical-align:middle;"> **Play**: Start slideshow presentation
- <img src="../../web/icons/pause.svg" alt="Pause" width="20" height="20" style="vertical-align:middle;"> **Pause**: Pause current slideshow
- <img src="../../web/icons/previous.svg" alt="Previous" width="20" height="20" style="vertical-align:middle;"> **Previous**: Go to previous slide
- <img src="../../web/icons/next.svg" alt="Next" width="20" height="20" style="vertical-align:middle;"> **Next**: Go to next slide
- <img src="../../web/icons/refresh.svg" alt="Refresh" width="20" height="20" style="vertical-align:middle;"> **Refresh**: Reload slideshow list

### Slideshow Management (Appears when slideshow is loaded)
- <img src="../../web/icons/edit.svg" alt="Edit" width="20" height="20" style="vertical-align:middle;"> **Edit**: Open current slideshow in WYSIWYG editor
- <img src="../../web/icons/delete.svg" alt="Delete" width="20" height="20" style="vertical-align:middle;"> **Delete**: Remove current slideshow (with confirmation)

## PowerPoint Upload Section

### Upload Interface
- **File Selection**: Choose .pptx files from your computer
- **Slideshow Name**: Auto-filled from filename, or enter custom name
- <img src="../../web/icons/upload.svg" alt="Upload" width="20" height="20" style="vertical-align:middle;"> **Upload Button**: Convert and import PowerPoint file

### Upload Process
1. Select a .pptx file (only PowerPoint 2007+ format supported)
2. The slideshow name automatically fills from the filename
3. Click Upload to start conversion
4. Watch status messages for progress and results
5. Successfully imported slideshows appear in the Available Slideshows list

[PPTX import tutorial](./import_pptx.md)

## Available Slideshows Section

### Slideshow Cards
Each slideshow displays:
- **Title**: Slideshow name
- **Metadata**: Number of slides and theme information
- **Active Indicator**: Highlights currently loaded slideshow

### Per-Slideshow Controls
- <img src="../../web/icons/load.svg" alt="Load" width="20" height="20" style="vertical-align:middle;"> **Load**: Load slideshow without starting presentation
- <img src="../../web/icons/play.svg" alt="Play" width="20" height="20" style="vertical-align:middle;"> **Play**: Load and immediately start playing slideshow

## Step-by-Step Usage

### Loading and Playing a Slideshow

#### Method 1: Load then Play
1. Find your desired slideshow in the "Available Slideshows" section
2. Click the <img src="../../web/icons/load.svg" alt="Load" width="20" height="20" style="vertical-align:middle;"> **Load** button
3. The slideshow will appear as "Active Slideshow" in the status panel
4. Click the main <img src="../../web/icons/play.svg" alt="Play" width="20" height="20" style="vertical-align:middle;"> **Play** button to start presentation

#### Method 2: Load and Play Immediately
1. Find your desired slideshow
2. Click the <img src="../../web/icons/play.svg" alt="Play" width="20" height="20" style="vertical-align:middle;"> **Play** button directly on the slideshow card
3. The slideshow loads and starts playing automatically

### Managing Presentation Playback
1. **Play/Pause**: Use the main control buttons to start/stop presentation
2. **Manual Navigation**: Use Previous/Next buttons for manual slide control
3. **Timer Monitoring**: Watch the countdown timer to see remaining slide time
4. **Slide Tracking**: Monitor current slide position in the status panel

### Editing Slideshows
1. Load the slideshow you want to edit
2. Click the <img src="../../web/icons/edit.svg" alt="Edit" width="20" height="20" style="vertical-align:middle;"> **Edit** button (appears when slideshow is loaded)
3. The WYSIWYG editor opens in a new tab with the slideshow content
4. Make your changes in the editor and save
5. Return to the controller - changes are automatically reflected

[WYSIWYG editor tutorial](./wysiwyg.md)

### Deleting Slideshows
1. Load the slideshow you want to delete
2. Click the <img src="../../web/icons/delete.svg" alt="Delete" width="20" height="20" style="vertical-align:middle;"> **Delete** button
3. Confirm deletion in the popup dialog
4. The slideshow is permanently removed from the system


### Viewer Access
- **Open Viewer**: Launch presentation display in new tab
- **Fullscreen Ready**: Optimized for projection and display screens (enetering and exitting fullscreen is done via F11 key)
- **Keyboard Controls**: Support for presentation controls


---

*This tutorial covers the main controller interface. For slideshow creation, see the [WYSIWYG Editor Tutorial](./wysiwyg.md). For PowerPoint import, see the [PowerPoint Import Tutorial](./import_pptx.md).*
