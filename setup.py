"""
Setup script for Futuristic Google Calendar Display
Handles installation and configuration for Raspberry Pi
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_system():
    """Check system compatibility"""
    system = platform.system()
    machine = platform.machine()
    
    print(f"System: {system} {machine}")
    
    if system == "Linux":
        # Check if it's Raspberry Pi
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo:
                    print("✅ Raspberry Pi detected")
                    return True
                else:
                    print("⚠️  Not a Raspberry Pi, but Linux system detected")
                    return True
        except:
            print("⚠️  Could not detect Raspberry Pi, assuming compatible Linux")
            return True
    
    elif system == "Darwin":  # macOS
        print("✅ macOS detected - development mode")
        return True
    
    elif system == "Windows":
        print("✅ Windows detected - development mode")
        return True
    
    else:
        print(f"⚠️  Unknown system: {system}")
        return True


def install_system_dependencies():
    """Install system-level dependencies"""
    system = platform.system()
    
    if system == "Linux":
        print("Installing system dependencies...")
        
        # Update package list
        try:
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            print("✅ Package list updated")
        except subprocess.CalledProcessError:
            print("❌ Failed to update package list")
            return False
        
        # Install required packages
        packages = [
            'python3-pip',
            'python3-venv',
            'python3-pyqt5',
            'python3-pyqt5.qtcore',
            'python3-pyqt5.qtgui',
            'python3-pyqt5.qtwidgets',
            'libqt5gui5',
            'libqt5core5a',
            'libqt5widgets5',
            'qt5-default',
            'xorg',  # For X11 display
            'xinit'  # For starting X session
        ]
        
        for package in packages:
            try:
                print(f"Installing {package}...")
                subprocess.run(['sudo', 'apt', 'install', '-y', package], 
                             check=True, capture_output=True)
                print(f"✅ {package} installed")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Failed to install {package}: {e}")
    
    return True


def create_virtual_environment():
    """Create Python virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False


def install_python_dependencies():
    """Install Python dependencies"""
    # Determine pip path
    if platform.system() == "Windows":
        pip_path = "venv/Scripts/pip"
        python_path = "venv/Scripts/python"
    else:
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
    
    try:
        print("Upgrading pip...")
        subprocess.run([python_path, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True)
        print("✅ Pip upgraded")
        
        print("Installing Python dependencies...")
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ Python dependencies installed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False


def create_config_directory():
    """Create configuration directory"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    print("✅ Configuration directory created")
    
    # Create .gitignore for sensitive files
    gitignore_path = config_dir / ".gitignore"
    gitignore_content = """
# Ignore sensitive credential files
credentials.json
token.json
*.pickle
"""
    
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content.strip())
    
    print("✅ Configuration .gitignore created")
    return True


def create_startup_script():
    """Create startup script for Raspberry Pi"""
    startup_script = """#!/bin/bash
# Futuristic Calendar Display Startup Script

# Set display
export DISPLAY=:0

# Change to application directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the calendar display
python main.py

# If the app exits, restart after 5 seconds
sleep 5
exec "$0"
"""
    
    script_path = Path("start_calendar.sh")
    with open(script_path, 'w') as f:
        f.write(startup_script)
    
    # Make executable
    os.chmod(script_path, 0o755)
    print("✅ Startup script created: start_calendar.sh")
    
    return True


def create_systemd_service():
    """Create systemd service for auto-start"""
    service_content = f"""[Unit]
Description=Futuristic Calendar Display
After=graphical-session.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
WorkingDirectory={Path.cwd()}
ExecStart={Path.cwd()}/start_calendar.sh
Restart=always
RestartSec=5

[Install]
WantedBy=graphical-session.target
"""
    
    service_path = Path("calendar-display.service")
    with open(service_path, 'w') as f:
        f.write(service_content)
    
    print("✅ Systemd service file created: calendar-display.service")
    print()
    print("To enable auto-start on boot:")
    print(f"1. sudo cp {service_path} /etc/systemd/system/")
    print("2. sudo systemctl enable calendar-display.service")
    print("3. sudo systemctl start calendar-display.service")
    print()
    
    return True


def setup_display_config():
    """Setup display configuration for Raspberry Pi"""
    if platform.system() != "Linux":
        return True
    
    print("Setting up display configuration...")
    
    # Create X11 startup script
    x11_script = """#!/bin/bash
# Start X11 and calendar display

# Kill any existing X sessions
sudo pkill X

# Start X server
startx &

# Wait for X to start
sleep 3

# Start calendar display
cd "$(dirname "$0")"
source venv/bin/activate
python main.py
"""
    
    script_path = Path("start_x11_calendar.sh")
    with open(script_path, 'w') as f:
        f.write(x11_script)
    
    os.chmod(script_path, 0o755)
    print("✅ X11 startup script created: start_x11_calendar.sh")
    
    return True


def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 FUTURISTIC CALENDAR DISPLAY - SETUP")
    print("=" * 60)
    print()
    
    # Check system compatibility
    if not check_python_version():
        return False
    
    if not check_system():
        return False
    
    print()
    
    # Install system dependencies (Linux only)
    if platform.system() == "Linux":
        response = input("Install system dependencies? (y/n): ").lower()
        if response == 'y':
            if not install_system_dependencies():
                return False
    
    # Create virtual environment
    if not create_virtual_environment():
        return False
    
    # Install Python dependencies
    if not install_python_dependencies():
        return False
    
    # Create configuration
    if not create_config_directory():
        return False
    
    # Create startup scripts
    if not create_startup_script():
        return False
    
    if platform.system() == "Linux":
        if not create_systemd_service():
            return False
        
        if not setup_display_config():
            return False
    
    print()
    print("=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run: python main.py --setup")
    print("   (to configure Google Calendar authentication)")
    print()
    print("2. Run: python main.py --test")
    print("   (to test the configuration)")
    print()
    print("3. Run: python main.py")
    print("   (to start the calendar display)")
    print()
    
    if platform.system() == "Linux":
        print("For Raspberry Pi auto-start:")
        print("- Use start_calendar.sh for manual startup")
        print("- Install systemd service for boot startup")
        print("- Use start_x11_calendar.sh if no desktop environment")
    
    print()
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
