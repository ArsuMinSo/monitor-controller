"""
Simple installation script for Monitor_vyroba dependencies
"""

import subprocess
import sys


def install_dependencies():
    """Install dependencies from requirements.txt"""
    print("Monitor_vyroba - Installing Dependencies")
    print("=" * 40)
    
    try:
        print("Installing Python packages...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True)
        
        print("\n Dependencies installed successfully!")
        print(" You can now run: py app.py")
        
    except subprocess.CalledProcessError as e:
        print(f"\n Installation failed: {e}")
        print(" Please check your internet connection and try again")
        return False
    except FileNotFoundError:
        print("\n requirements.txt not found")
        print(" Please run this script from the project directory")
        return False
    
    return True


if __name__ == "__main__":
    install_dependencies()
