import subprocess
import os
import shutil
import argparse
import re
import ast
import inspect


def generate_docs(output_dir="docs", output_format="html", file_name=None):
    os.makedirs(output_dir, exist_ok=True)

    files = [
        ("app", "Main Application"),
        ("src.http_server", "HTTP Server"),
        ("src.slideshow_manager", "Slideshow Manager"),
        ("src.websocket_manager", "WebSocket Manager"),
        ("src.pptx_parse", "PowerPoint Parser"),
        ("src.utils", "Utilities")
    ]

    if output_format.lower() == "md" or output_format.lower() == "markdown":
        generate_markdown_docs(output_dir, files)
    else:
        generate_html_docs(output_dir, files)


def generate_html_docs(output_dir, files):
    """Generate HTML documentation using pydoc"""
    for module, display_name in files:
        print(f"Generating HTML documentation for {module}...")
        
        # Generate HTML documentation for each module
        subprocess.run(["py", "-m", "pydoc", "-w", module], check=True)
        
        # Move and style the generated HTML files
        html_file = f"{module}.html"
        target_file = f"{output_dir}/{html_file}"
        
        if os.path.exists(target_file):
            os.remove(target_file)
        
        # Read the generated HTML and add styling
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add custom styling and navigation
        styled_content = add_styling_and_nav(content, module, display_name, files)
        
        # Write the styled content
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(styled_content)
        
        # Remove the original file
        os.remove(html_file)
        
        print(f"  -> Generated: {target_file}")
    
    # Generate index page
    generate_index_page(output_dir, files)
    print(f"\nHTML documentation generated in '{output_dir}/' directory")
    print(f"Open '{output_dir}/index.html' to view the documentation")


def generate_markdown_docs(output_dir, files):
    """Generate Markdown documentation by parsing Python source code"""
    print("Generating Markdown documentation...")
    
    # Generate individual module docs
    for module, display_name in files:
        print(f"Generating Markdown documentation for {module}...")
        
        try:
            # Convert module path to file path
            if module == "app":
                file_path = "app.py"
            else:
                file_path = module.replace(".", "/") + ".py"
            
            # Generate markdown content
            markdown_content = generate_module_markdown(module, display_name, file_path)
            
            # Write to file
            md_filename = f"{module.replace('.', '_')}.md"
            target_file = f"{output_dir}/{md_filename}"
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"  -> Generated: {target_file}")
            
        except Exception as e:
            print(f"  -> Error generating {module}: {e}")
    
    # Generate index markdown
    generate_markdown_index(output_dir, files)
    print(f"\nMarkdown documentation generated in '{output_dir}/' directory")
    print(f"Open '{output_dir}/README.md' to view the documentation")


def generate_module_markdown(module_name, display_name, file_path):
    """Generate Markdown documentation for a single module"""
    
    try:
        # Try to import the module to get docstrings
        if module_name == "app":
            import sys
            sys.path.insert(0, ".")
            import app as module_obj
        else:
            exec(f"from {module_name} import *")
            module_obj = __import__(module_name, fromlist=[''])
        
        # Get module docstring
        module_doc = inspect.getdoc(module_obj) or "No module documentation available."
        
    except Exception as e:
        module_doc = f"Could not load module documentation: {e}"
        module_obj = None
    
    # Start building markdown
    markdown = f"""# {display_name}

**Module:** `{module_name}`  
**File:** `{file_path}`

## Overview

{module_doc}

"""
    
    if module_obj:
        try:
            # Get classes
            classes = []
            functions = []
            
            for name, obj in inspect.getmembers(module_obj):
                if not name.startswith('_'):
                    if inspect.isclass(obj) and obj.__module__ == module_obj.__name__:
                        classes.append((name, obj))
                    elif inspect.isfunction(obj) and obj.__module__ == module_obj.__name__:
                        functions.append((name, obj))
            
            # Document classes
            if classes:
                markdown += "## Classes\n\n"
                for class_name, class_obj in classes:
                    class_doc = inspect.getdoc(class_obj) or "No documentation available."
                    markdown += f"### {class_name}\n\n{class_doc}\n\n"
                    
                    # Document methods
                    methods = [method for method in inspect.getmembers(class_obj, predicate=inspect.isfunction) 
                              if not method[0].startswith('_') or method[0] in ['__init__']]
                    
                    if methods:
                        markdown += "#### Methods\n\n"
                        for method_name, method_obj in methods:
                            method_doc = inspect.getdoc(method_obj) or "No documentation available."
                            try:
                                signature = inspect.signature(method_obj)
                                markdown += f"**`{method_name}{signature}`**\n\n{method_doc}\n\n"
                            except:
                                markdown += f"**`{method_name}()`**\n\n{method_doc}\n\n"
                        markdown += "\n"
            
            # Document functions
            if functions:
                markdown += "## Functions\n\n"
                for func_name, func_obj in functions:
                    func_doc = inspect.getdoc(func_obj) or "No documentation available."
                    try:
                        signature = inspect.signature(func_obj)
                        markdown += f"### {func_name}{signature}\n\n{func_doc}\n\n"
                    except:
                        markdown += f"### {func_name}()\n\n{func_doc}\n\n"
        
        except Exception as e:
            markdown += f"## Error\n\nCould not extract detailed module information: {e}\n\n"
    
    # Add source file analysis if possible
    try:
        if os.path.exists(file_path):
            markdown += generate_source_analysis(file_path)
    except Exception as e:
        markdown += f"## Source Analysis\n\nCould not analyze source file: {e}\n\n"
    
    # Add footer
    markdown += f"""
---
*Generated by Presentator documentation generator*
"""
    
    return markdown


def generate_source_analysis(file_path):
    """Generate source code analysis for markdown docs"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count lines, functions, classes
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        # Parse AST to count functions and classes
        tree = ast.parse(content)
        functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        classes = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
        
        analysis = f"""## Source File Statistics

- **Total Lines:** {total_lines}
- **Code Lines:** {code_lines}
- **Functions:** {functions}
- **Classes:** {classes}
- **File Size:** {os.path.getsize(file_path)} bytes

"""
        return analysis
        
    except Exception as e:
        return f"## Source Analysis\n\nCould not analyze source file: {e}\n\n"


def generate_markdown_index(output_dir, modules):
    """Generate a README.md index file for Markdown documentation"""
    
    readme_content = f"""# Presentator - API Documentation

![Presentator](https://img.shields.io/badge/Presentator-Real--time%20Slideshow%20System-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-green)
![WebSocket](https://img.shields.io/badge/WebSocket-Real--time-orange)

## Overview

Presentator is a powerful real-time slideshow system designed for digital signage and presentations. 
The system enables synchronized slideshow control across multiple network devices using modern WebSocket technology.

## Features

- **Web-based Editor** - Create and edit slideshows directly in your browser
- **Real-time Sync** - Synchronized display across multiple devices  
- **PowerPoint Import** - Import and convert PowerPoint presentations
- **REST API** - Full RESTful API for slideshow management
- **Network Access** - Access from any device on your network
- **Responsive Design** - Works on desktop, tablet, and mobile devices

## System Architecture

The Presentator system consists of several key components:

| Component | Purpose |
|-----------|---------|
| **HTTP Server** | Web interface and REST API endpoints |
| **WebSocket Server** | Real-time communication and state sync |
| **Slideshow Manager** | CRUD operations and format conversion |
| **PowerPoint Parser** | Import and convert PowerPoint files |
| **Web Interface** | Controller, viewer, and editor interfaces |

## Module Documentation

"""
    
    # Add module links
    for module, name in modules:
        md_filename = f"{module.replace('.', '_')}.md"
        module_descriptions = {
            "app": "Main application entry point and server coordinator",
            "src.http_server": "HTTP server with REST API endpoints",
            "src.slideshow_manager": "Core slideshow CRUD operations",
            "src.websocket_manager": "Real-time WebSocket communication",
            "src.pptx_parse": "PowerPoint import functionality",
            "src.utils": "Network utilities and helpers"
        }
        
        description = module_descriptions.get(module, "System module")
        readme_content += f"- **[{name}]({md_filename})** - {description}\n"
    
    readme_content += f"""

## Quick Start

1. **Install Dependencies**
   ```bash
   py -m pip install -r requirements.txt
   ```

2. **Start the System**
   ```bash
   py app.py
   ```

3. **Access the Interface**
   - Controller: http://localhost:8080/web/controller.html
   - Viewer: http://localhost:8080/web/viewer.html
   - Editor: http://localhost:8080/web/editor.html

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/slideshows` | GET | List all slideshows |
| `/api/slideshow/<id>` | GET | Get slideshow details |
| `/api/load_slideshow` | POST | Load a slideshow |
| `/api/upload_pptx` | POST | Upload PowerPoint file |
| `/api/delete_slideshow` | POST | Delete a slideshow |

## WebSocket Events

The system uses WebSocket communication on port 50002 for real-time updates:

- **play** - Start slideshow playback
- **pause** - Pause slideshow
- **next_slide** - Advance to next slide
- **prev_slide** - Go to previous slide
- **set_slide** - Jump to specific slide

## Development

### File Structure
```
monitor-controller/
app.py                 # Main application
src/                   # Core modules
http_server.py     # HTTP server
websocket_manager.py # WebSocket server  
slideshow_manager.py # Slideshow operations
pptx_parse.py      # PowerPoint parser
utils.py           # Utilities
web/                   # Web interface
controller.html    # Control interface
viewer.html        # Display interface
editor.html        # Slideshow editor
style.css          # Styles
slideshows/            # Slideshow storage
```

### Requirements

- Python 3.7 or higher
- websockets - WebSocket server implementation
- python-pptx - PowerPoint file processing
- Pillow - Image processing support

## License

This project is open source. See the repository for license details.

---
*Documentation generated by Presentator documentation generator*
*Last updated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # Write the README
    with open(f"{output_dir}/README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)


def add_styling_and_nav(html_content, current_module, display_name, all_modules):
    """Add custom styling and navigation to pydoc-generated HTML."""
    
    # Custom CSS styles
    custom_styles = """
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 0; 
            background: #f8f9fa;
            line-height: 1.6;
        }
        
        .nav-bar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .nav-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
        }
        
        .nav-title {
            font-size: 24px;
            font-weight: bold;
            margin: 0;
        }
        
        .nav-links {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .nav-links a {
            color: white;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 20px;
            background: rgba(255,255,255,0.1);
            transition: all 0.3s ease;
            font-size: 14px;
        }
        
        .nav-links a:hover {
            background: rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }
        
        .nav-links a.active {
            background: rgba(255,255,255,0.3);
            font-weight: bold;
        }
        
        .content-wrapper {
            max-width: 1200px;
            margin: 20px auto;
            padding: 0 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .module-header {
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            margin: 0 -20px 20px -20px;
        }
        
        .module-title {
            font-size: 32px;
            margin: 0 0 10px 0;
            font-weight: 300;
        }
        
        .module-path {
            font-size: 16px;
            opacity: 0.9;
            font-family: 'Courier New', monospace;
        }
        
        .content {
            padding: 20px;
        }
        
        /* Style existing pydoc elements */
        tt, code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            border: 1px solid #e9ecef;
        }
        
        pre {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            overflow-x: auto;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        
        th, td {
            border: 1px solid #dee2e6;
            padding: 12px;
            text-align: left;
        }
        
        th {
            background: #f8f9fa;
            font-weight: 600;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            margin-top: 40px;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .nav-container {
                flex-direction: column;
                gap: 15px;
            }
            
            .nav-links {
                justify-content: center;
            }
            
            .content-wrapper {
                margin: 10px;
                padding: 0 15px;
            }
            
            .module-title {
                font-size: 24px;
            }
        }
    </style>
    """
    
    # Create navigation HTML
    nav_html = f"""
    <div class="nav-bar">
        <div class="nav-container">
            <h1 class="nav-title">Presentator Docs</h1>
            <div class="nav-links">
                <a href="index.html"> Home</a>
    """
    
    for module, name in all_modules:
        active_class = " active" if module == current_module else ""
        nav_html += f'                <a href="{module}.html" class="{active_class}">{name}</a>\n'
    
    nav_html += """            </div>
        </div>
    </div>
    """
    
    # Create module header
    header_html = f"""
    <div class="content-wrapper">
        <div class="module-header">
            <h1 class="module-title">{display_name}</h1>
            <div class="module-path">{current_module.replace('.', '/')}.py</div>
        </div>
        <div class="content">
    """
    
    # Footer HTML
    footer_html = """
        </div>
    </div>
    <div class="footer">
        <p>Generated with pydoc for Presentator System | 
        <a href="https://github.com/ArsuMinSo/monitor-controller" style="color: #667eea;">View on GitHub</a></p>
    </div>
    """
    
    # Insert custom styles in head
    if '<head>' in html_content:
        html_content = html_content.replace('<head>', f'<head>{custom_styles}')
    
    # Insert navigation after body tag
    if '<body' in html_content:
        body_start = html_content.find('>', html_content.find('<body')) + 1
        html_content = html_content[:body_start] + nav_html + header_html + html_content[body_start:] + footer_html
    
    return html_content


def generate_index_page(output_dir, modules):
    """Generate a styled index page for the documentation."""
    
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Presentator - API Documentation</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 50px;
        }}
        
        .main-title {{
            font-size: 48px;
            font-weight: 300;
            margin: 0 0 20px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .subtitle {{
            font-size: 20px;
            opacity: 0.9;
            margin: 0;
        }}
        
        .content-card {{
            background: white;
            border-radius: 15px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}
        
        .description {{
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 40px;
        }}
        
        .description h2 {{
            margin-top: 0;
            font-size: 28px;
            font-weight: 300;
        }}
        
        .features {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .feature {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }}
        
        .feature h3 {{
            margin: 0 0 10px 0;
            font-size: 18px;
        }}
        
        .modules-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }}
        
        .module-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-decoration: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .module-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
            text-decoration: none;
            color: white;
        }}
        
        .module-name {{
            font-size: 22px;
            font-weight: 600;
            margin: 0 0 10px 0;
        }}
        
        .module-description {{
            opacity: 0.9;
            line-height: 1.5;
        }}
        
        .architecture {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 30px;
            margin: 30px 0;
        }}
        
        .architecture h2 {{
            color: #333;
            margin-top: 0;
            font-size: 24px;
        }}
        
        .arch-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .arch-item {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .arch-item strong {{
            color: #667eea;
            display: block;
            margin-bottom: 8px;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 50px;
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .main-title {{
                font-size: 36px;
            }}
            
            .content-card {{
                padding: 25px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="main-title">Presentator</h1>
            <p class="subtitle">Real-time Slideshow System Documentation</p>
        </div>
        
        <div class="content-card">
            <div class="description">
                <h2>About Presentator</h2>
                <p>Presentator is a powerful real-time slideshow system designed for digital signage and presentations. 
                The system enables synchronized slideshow control across multiple network devices using modern WebSocket technology.</p>
                
                <div class="features">
                    <div class="feature">
                        <h3> Web-based Editor</h3>
                        <p>Create and edit slideshows directly in your browser</p>
                    </div>
                    <div class="feature">
                        <h3> Real-time Sync</h3>
                        <p>Synchronized display across multiple devices</p>
                    </div>
                    <div class="feature">
                        <h3> PowerPoint Import</h3>
                        <p>Import and convert PowerPoint presentations</p>
                    </div>
                    <div class="feature">
                        <h3> REST API</h3>
                        <p>Full RESTful API for slideshow management</p>
                    </div>
                </div>
            </div>
            
            <h2 style="color: #333; margin-bottom: 30px;">Module Documentation</h2>
            
            <div class="modules-grid">
    """
    
    # Add module cards
    module_descriptions = {
        "app": "Main application entry point and server coordinator. Handles startup, dependency checking, and orchestrates all system components.",
        "src.http_server": "HTTP server providing REST API endpoints for slideshow management, file serving, and PowerPoint upload handling.",
        "src.slideshow_manager": "Core slideshow CRUD operations, format conversion, and PowerPoint import integration.",
        "src.websocket_manager": "Real-time WebSocket communication server for state synchronization and client management.", 
        "src.pptx_parse": "PowerPoint file parsing and conversion functionality for importing presentations.",
        "src.utils": "Network utilities and helper functions used throughout the system."
    }
    
    for module, name in modules:
        description = module_descriptions.get(module, "System module documentation")
        index_html += f"""
                <a href="{module}.html" class="module-card">
                    <div class="module-name">{name}</div>
                    <div class="module-description">{description}</div>
                </a>
        """
    
    index_html += """
            </div>
            
            <div class="architecture">
                <h2>System Architecture</h2>
                <div class="arch-grid">
                    <div class="arch-item">
                        <strong>app.py</strong>
                        Main application entry point and server coordinator
                    </div>
                    <div class="arch-item">
                        <strong>http_server</strong>
                        HTTP server with REST API endpoints
                    </div>
                    <div class="arch-item">
                        <strong>websocket_manager</strong>
                        WebSocket server for real-time communication
                    </div>
                    <div class="arch-item">
                        <strong>slideshow_manager</strong>
                        Slideshow CRUD operations and format conversion
                    </div>
                    <div class="arch-item">
                        <strong>pptx_parse</strong>
                        PowerPoint import and conversion functionality
                    </div>
                    <div class="arch-item">
                        <strong>utils</strong>
                        Network utilities and helper functions
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated with pydoc for Presentator System | 
            <a href="https://github.com/ArsuMinSo/monitor-controller" style="color: rgba(255,255,255,0.8);">View on GitHub</a></p>
        </div>
    </div>
</body>
</html>"""
    
    with open(f"{output_dir}/index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate documentation for Presentator system')
    parser.add_argument('--format', '-f', 
                       choices=['html', 'md', 'markdown'], 
                       default='html',
                       help='Output format (html or md/markdown)')
    parser.add_argument('--output', '-o', 
                       default='docs',
                       help='Output directory (default: docs)')
    parser.add_argument('--file', 
                       help='Generate docs for specific file (not implemented yet)')
    
    args = parser.parse_args()
    
    print(f"Generating {args.format.upper()} documentation...")
    print(f"Output directory: {args.output}")
    print("=" * 50)
    
    generate_docs(output_dir=args.output, output_format=args.format, file_name=args.file) 
