# 🚀 Installation Guide - Futuristic Google Calendar Display

## Quick Installation Summary

This guide provides step-by-step instructions for installing the Futuristic Google Calendar Display on your Raspberry Pi.

## 📋 Prerequisites

- **Raspberry Pi 4** (recommended) or Raspberry Pi 3B+
- **5-inch touchscreen display** (800x480 resolution)
- **Raspberry Pi OS** (Bullseye or newer)
- **Internet connection**
- **Google account** with calendar access

## 🛠️ Installation Steps

### 1. System Preparation

```bash
# Update your Raspberry Pi
sudo apt update && sudo apt upgrade -y

# Install Git if not already installed
sudo apt install git -y
```

### 2. Download the Application

```bash
# Navigate to your home directory
cd /home/pi

# Clone the repository (replace with actual repository URL)
git clone <repository-url> calendar_app
cd calendar_app
```

### 3. Run Automated Setup

```bash
# Run the setup script
python setup.py
```

This will:
- Check system compatibility
- Install system dependencies (PyQt5, X11, etc.)
- Create a Python virtual environment
- Install Python packages
- Create startup scripts

### 4. Google Calendar API Setup

#### 4.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your project ID

#### 4.2 Enable Google Calendar API

1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click "Enable"

#### 4.3 Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - Choose "External" user type
   - Fill in required fields (app name, user support email)
   - Add your email to test users
4. Choose "Desktop application" as application type
5. Name it "Calendar Display" or similar
6. Download the JSON credentials file

#### 4.4 Configure Application

```bash
# Copy credentials to config directory
cp ~/Downloads/credentials.json config/

# Run setup wizard
source venv/bin/activate
python main.py --setup
```

Follow the prompts to complete authentication.

### 5. Test Installation

```bash
# Test all components
source venv/bin/activate
python test_app.py

# Test Google Calendar connection
python main.py --test
```

### 6. Run the Application

```bash
# Start the calendar display
source venv/bin/activate
python main.py
```

## 🔧 Configuration

### Display Settings

Edit `config/settings.py` to customize:

```python
# Screen resolution (adjust for your display)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# Fullscreen mode
FULLSCREEN = True

# Hide cursor for kiosk mode
HIDE_CURSOR = True

# Your timezone
TIMEZONE = "America/New_York"  # Change this!

# Refresh interval (seconds)
REFRESH_INTERVAL = 900  # 15 minutes
```

### Theme Customization

Modify colors in `config/settings.py`:

```python
THEME = {
    'background': '#0a0a0a',      # Dark background
    'primary': '#00ffff',         # Cyan highlights
    'secondary': '#8a2be2',       # Purple accents
    'accent': '#ff1493',          # Pink alerts
    # ... more colors
}
```

## 🚀 Auto-Start Setup

### Method 1: Systemd Service (Recommended)

```bash
# Copy service file
sudo cp calendar-display.service /etc/systemd/system/

# Enable auto-start
sudo systemctl enable calendar-display.service

# Start service
sudo systemctl start calendar-display.service

# Check status
sudo systemctl status calendar-display.service
```

### Method 2: Desktop Autostart

```bash
# Create autostart directory
mkdir -p ~/.config/autostart

# Create desktop entry
cat > ~/.config/autostart/calendar-display.desktop << EOF
[Desktop Entry]
Type=Application
Name=Calendar Display
Exec=/home/pi/calendar_app/start_calendar.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

### Method 3: Manual Script

```bash
# Make startup script executable
chmod +x start_calendar.sh

# Run manually
./start_calendar.sh
```

## 🐛 Troubleshooting

### Common Issues

#### "No module named PyQt5"
```bash
# Install system PyQt5
sudo apt install python3-pyqt5

# Or in virtual environment
source venv/bin/activate
pip install PyQt5
```

#### "Display not found"
```bash
# Set display environment
export DISPLAY=:0

# Start X11 if needed
startx
```

#### "Authentication failed"
- Verify `config/credentials.json` exists
- Check Google Calendar API is enabled
- Re-run setup: `python main.py --setup`

#### "No events showing"
- Check internet connection
- Verify timezone in `config/settings.py`
- Run debug: `python main.py --test`

### Debug Mode

```bash
# Run with verbose output
source venv/bin/activate
python -v main.py
```

### Log Files

```bash
# Check service logs
journalctl -u calendar-display.service -f

# Check system logs
tail -f /var/log/syslog | grep calendar
```

## 📱 Usage

### Keyboard Shortcuts
- **F5**: Force refresh
- **F11**: Toggle fullscreen
- **Escape**: Exit fullscreen/close
- **Ctrl+Q**: Quit application

### Touch Controls
- **Tap notification**: Dismiss
- **Tap outside notification**: Dismiss

## 🔄 Updates

To update the application:

```bash
cd /home/pi/calendar_app
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

## 📞 Support

- Check the main [README.md](README.md) for detailed documentation
- Run `python test_app.py` to diagnose issues
- Use `python main.py --test` for Google Calendar debugging

## 🎯 Performance Tips

### For Raspberry Pi 3B+
- Reduce refresh interval: `REFRESH_INTERVAL = 1800` (30 minutes)
- Limit events: `MAX_EVENTS_DISPLAY = 6`
- Disable animations: `ANIMATIONS['enabled'] = False`

### For Better Performance
- Use wired Ethernet instead of Wi-Fi
- Use a high-quality SD card (Class 10 or better)
- Ensure adequate power supply (official Raspberry Pi adapter)

---

**🎉 Congratulations! Your futuristic calendar display is ready!**

Transform your Raspberry Pi into a stunning, always-on calendar display that will impress everyone who sees it.
