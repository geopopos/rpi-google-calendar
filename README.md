# 🚀 Futuristic Google Calendar Display

A stunning, futuristic Google Calendar display application designed specifically for Raspberry Pi with a 5-inch touchscreen. Features a cyberpunk-inspired interface with real-time event updates, notifications, and a sleek dark theme perfect for always-on displays.

![Calendar Display Preview](https://via.placeholder.com/800x480/0a0a0a/00ffff?text=Futuristic+Calendar+Display)

## ✨ Features

- **🎨 Futuristic UI Design**: Cyberpunk-inspired interface with neon colors and smooth animations
- **📅 Real-time Calendar Sync**: Automatic synchronization with Google Calendar
- **🔔 Smart Notifications**: 10-minute warnings and event start alerts
- **📱 Touch-Friendly**: Optimized for 5-inch touchscreen displays
- **🖥️ Full-Screen Mode**: Kiosk-style display perfect for wall mounting
- **⚡ Auto-Refresh**: Configurable refresh intervals (default: 15 minutes)
- **🌙 Always-On Display**: Designed for 24/7 operation
- **🔄 Status Indicators**: Visual indicators for past, current, and upcoming events
- **📍 Location Display**: Shows event locations when available
- **🎯 Multi-Calendar Support**: Displays events from all your Google calendars

## 🛠️ Hardware Requirements

- **Raspberry Pi 4** (recommended) or Raspberry Pi 3B+
- **5-inch touchscreen display** (800x480 resolution)
- **MicroSD card** (16GB or larger)
- **Power supply** (official Raspberry Pi power adapter recommended)
- **Internet connection** (Wi-Fi or Ethernet)

## 📋 Software Requirements

- **Raspberry Pi OS** (Bullseye or newer)
- **Python 3.7+**
- **PyQt5** (for GUI)
- **Google Calendar API access**

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd calendar_app

# Run the setup script
python setup.py
```

### 2. Configure Google Calendar

```bash
# Run the setup wizard
python main.py --setup
```

Follow the instructions to:
1. Create a Google Cloud Project
2. Enable the Google Calendar API
3. Create OAuth 2.0 credentials
4. Download and save the credentials file

### 3. Test Configuration

```bash
# Test your setup
python main.py --test
```

### 4. Run the Calendar Display

```bash
# Start the application
python main.py
```

## 📖 Detailed Installation Guide

### Step 1: Prepare Your Raspberry Pi

1. **Install Raspberry Pi OS**
   - Use Raspberry Pi Imager to flash the latest Raspberry Pi OS
   - Enable SSH and Wi-Fi during setup (optional)

2. **Update the system**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Install Git**
   ```bash
   sudo apt install git -y
   ```

### Step 2: Download and Setup the Application

1. **Clone the repository**
   ```bash
   cd /home/pi
   git clone <repository-url>
   cd calendar_app
   ```

2. **Run the automated setup**
   ```bash
   python setup.py
   ```
   
   This will:
   - Check system compatibility
   - Install system dependencies
   - Create a Python virtual environment
   - Install Python packages
   - Create startup scripts

### Step 3: Google Calendar API Setup

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable the Google Calendar API**
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the JSON file

4. **Configure the application**
   ```bash
   # Copy your credentials file to the config directory
   cp ~/Downloads/credentials.json config/
   
   # Run the setup wizard
   python main.py --setup
   ```

5. **Test the configuration**
   ```bash
   python main.py --test
   ```

### Step 4: Configure Display Settings

Edit `config/settings.py` to customize your display:

```python
# Display Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FULLSCREEN = True
HIDE_CURSOR = True

# Calendar Settings
REFRESH_INTERVAL = 900  # 15 minutes
MAX_EVENTS_DISPLAY = 8
TIMEZONE = "America/New_York"  # Change to your timezone

# Notification Settings
WARNING_MINUTES = 10
NOTIFICATION_TIMEOUT = 30
```

## 🎮 Usage

### Running the Application

```bash
# Normal mode
python main.py

# Setup mode (first time)
python main.py --setup

# Test mode
python main.py --test
```

### Keyboard Shortcuts

- **F5**: Force refresh calendar data
- **F11**: Toggle fullscreen mode
- **Escape**: Exit fullscreen or close application
- **Ctrl+Q**: Quit application

### Touch Controls

- **Tap notification**: Dismiss notification
- **Tap outside notification**: Dismiss notification
- **Tap event**: View event details (future feature)

## 🔧 Configuration

### Display Settings

The application is pre-configured for a 5-inch display (800x480), but you can customize it in `config/settings.py`:

```python
# For different screen sizes
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600

# Disable fullscreen for development
FULLSCREEN = False

# Show cursor for debugging
HIDE_CURSOR = False
```

### Theme Customization

Customize colors and fonts in `config/settings.py`:

```python
THEME = {
    'background': '#0a0a0a',
    'primary': '#00ffff',      # Cyan
    'secondary': '#8a2be2',    # Blue Violet
    'accent': '#ff1493',       # Deep Pink
    'text_primary': '#ffffff',
    'text_secondary': '#b0b0b0',
    # ... more colors
}
```

### Notification Settings

```python
# Notification timing
WARNING_MINUTES = 10        # Warning before event
NOTIFICATION_TIMEOUT = 30   # Auto-dismiss time
NOTIFICATION_SOUND = False  # Enable sound alerts
```

## 🚀 Auto-Start Setup

### Method 1: Systemd Service (Recommended)

```bash
# Copy the service file
sudo cp calendar-display.service /etc/systemd/system/

# Enable auto-start
sudo systemctl enable calendar-display.service

# Start the service
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

### Method 3: Manual Startup Script

```bash
# Make the startup script executable
chmod +x start_calendar.sh

# Run manually
./start_calendar.sh
```

## 🐛 Troubleshooting

### Common Issues

1. **"No module named PyQt5"**
   ```bash
   # Install PyQt5 system package
   sudo apt install python3-pyqt5
   
   # Or install in virtual environment
   source venv/bin/activate
   pip install PyQt5
   ```

2. **"Display not found"**
   ```bash
   # Set display environment
   export DISPLAY=:0
   
   # Or start X11
   startx
   ```

3. **"Authentication failed"**
   - Check that `config/credentials.json` exists
   - Verify Google Calendar API is enabled
   - Run `python main.py --setup` again

4. **"No events showing"**
   - Check internet connection
   - Verify timezone settings in `config/settings.py`
   - Run `python main.py --test` to debug

### Debug Mode

Run with verbose output:

```bash
# Enable debug logging
export PYTHONPATH=/home/pi/calendar_app
python -v main.py
```

### Log Files

Check system logs:

```bash
# Application logs
journalctl -u calendar-display.service -f

# System logs
tail -f /var/log/syslog | grep calendar
```

## 🔧 Development

### Project Structure

```
calendar_app/
├── main.py                 # Application entry point
├── main_window.py          # Main GUI window
├── setup.py               # Installation script
├── requirements.txt       # Python dependencies
├── config/
│   └── settings.py        # Configuration settings
├── services/
│   ├── google_auth.py     # Google Calendar authentication
│   ├── calendar_service.py # Calendar data management
│   └── notification_manager.py # Notification handling
├── ui/
│   ├── styles.py          # UI themes and styling
│   ├── event_widget.py    # Event display components
│   └── notification_widget.py # Notification overlays
└── README.md              # This file
```

### Adding Features

1. **Custom Themes**: Modify `ui/styles.py`
2. **New Notifications**: Extend `services/notification_manager.py`
3. **Additional Calendars**: Update `services/calendar_service.py`
4. **UI Components**: Add to `ui/` directory

### Testing

```bash
# Test individual components
python services/google_auth.py
python services/calendar_service.py
python ui/event_widget.py
python ui/notification_widget.py
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

- **Issues**: Report bugs and request features on GitHub
- **Documentation**: Check this README and inline code comments
- **Community**: Join discussions in the project repository

## 🙏 Acknowledgments

- **Google Calendar API** for calendar integration
- **PyQt5** for the GUI framework
- **Raspberry Pi Foundation** for the amazing hardware
- **Open Source Community** for inspiration and tools

---

**Made with ❤️ for the Raspberry Pi community**

*Transform your Raspberry Pi into a stunning calendar display!*
