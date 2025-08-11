import subprocess
import os
import shutil
import argparse
import re


def generate_docs(output_dir="docs", file_name = None):
    os.makedirs(output_dir, exist_ok=True)

    files = [
        ("app", "Main Application"),
        ("src.http_server", "HTTP Server"),
        ("src.slideshow_manager", "Slideshow Manager"),
        ("src.websocket_manager", "WebSocket Manager"),
        ("src.pptx_parse", "PowerPoint Parser"),
        ("src.utils", "Utilities")
    ]

    for module, display_name in files:
        print(f"Generating documentation for {module}...")
        
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
    print(f"\nDocumentation generated in '{output_dir}/' directory")
    print(f"Open '{output_dir}/index.html' to view the documentation")


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
        <a href="https://github.com/ArsuMinSo/Monitor_vyroba" style="color: #667eea;">View on GitHub</a></p>
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
            <a href="https://github.com/ArsuMinSo/Monitor_vyroba" style="color: rgba(255,255,255,0.8);">View on GitHub</a></p>
        </div>
    </div>
</body>
</html>"""
    
    with open(f"{output_dir}/index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)


if __name__ == "__main__":
    generate_docs(output_dir="docs") 
