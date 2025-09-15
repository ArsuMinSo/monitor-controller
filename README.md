# Monitor Controller

A real-time slideshow presentation system designed for ability to display synchronized presentations across multiple network devices.

## What This Project Does

Monitor Controller is a slideshow management system that enables you to create, manage, and display synchronized presentations or banners across multiple devices on your network. It is ideal for professional digital signage, allowing you to display synchronized banners or slideshows throughout a facility using your own infrastructure.

### Core Functionality

#### **Centralized Slideshow Management**

- Manage multiple presentations from a single interface [_tutorial_](./docs/tuto/con2.md)
- Import PowerPoint presentations (.pptx files) [_tutorial_](./docs/tuto/import_pptx.md)
- Create slideshows using a built-in WYSIWYG editor. [_tutorial_](./docs/tuto/wysiwyg.md)
- Or take html from professional WYSIWYG editor [_editor_](https://wysiwyghtml.com/)

#### **Multi-Device Synchronization**

- Display the same slideshow simultaneously on multiple screens
- Real-time synchronization - when you change slides on one device, all devices update instantly
- Centralized control from any device on the network

#### **Professional Display Features**

- Automatic slideshow advancement with configurable timing
- Manual control with keyboard navigation
- Full-screen presentation mode
- Custom themes and background colors
- Support for images, text formatting, and layouts

### Use Cases

#### **Digital Signage**

- Restaurant menus and specials
- Store promotions and advertisements  
- Office information displays
- Event announcements and schedules

#### **Professional Presentations**

- Conference rooms with multiple displays
- Trade show booths
- Training sessions
- Product demonstrations

## Getting Started

### Quick Installation

1. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install System Dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt install poppler-utils libreoffice
   ```

3. **Run the Application:**
   ```bash
   python3 app.py
   ```

4. **Open in Browser:**
   ```
   http://localhost:8080
   ```

### Detailed Setup

For complete installation instructions, troubleshooting, and platform-specific setup, see:
- **[INSTALLATION.md](./INSTALLATION.md)** - Comprehensive installation guide
- **[script/README.md](./script/README.md)** - Alternative installation methods

### PowerPoint Conversion

The system supports two PowerPoint conversion modes:

- **Text/HTML Mode**: Extracts and preserves editable text content
- **Image Mode**: Converts slides to images preserving exact visual appearance

Requirements for image conversion:
- LibreOffice (for PPTX PDF conversion)
- poppler-utils (for PDF image conversion)
