"""
Configuration settings for the Calendar Display Application
"""

# Application Settings
APP_NAME = "Futuristic Calendar Display"
VERSION = "1.0.0"

# Display Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FULLSCREEN = True
HIDE_CURSOR = True

# Calendar Settings
REFRESH_INTERVAL = 900  # 15 minutes in seconds
MAX_EVENTS_DISPLAY = 5
TIMEZONE = "America/New_York"  # Change to your timezone

# Notification Settings
WARNING_MINUTES = 10  # Minutes before event to show warning
NOTIFICATION_TIMEOUT = 30  # Seconds to auto-dismiss notifications
NOTIFICATION_SOUND = False  # Set to True if you want sound alerts

# Google Calendar API Settings
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly'
]
CREDENTIALS_FILE = 'config/credentials.json'
TOKEN_FILE = 'config/token.json'

# UI Theme Settings
THEME = {
    'background': '#0a0a0a',
    'primary': '#00ffff',      # Cyan
    'secondary': '#8a2be2',    # Blue Violet
    'accent': '#ff1493',       # Deep Pink
    'text_primary': '#ffffff',
    'text_secondary': '#b0b0b0',
    'success': '#00ff00',
    'warning': '#ffa500',
    'error': '#ff4444',
    'current_event': '#00ffff',
    'past_event': '#666666',
    'upcoming_event': '#ffffff'
}

# Font Settings
FONTS = {
    'time_display': ('Helvetica Neue', 48, 'bold'),  # Fallback to clean system font
    'date_display': ('Helvetica Neue', 24, 'normal'),
    'event_title': ('Arial', 20, 'bold'),
    'event_time': ('Arial', 18, 'bold'),
    'notification_title': ('Helvetica Neue', 28, 'bold'),
    'notification_text': ('Arial', 22, 'normal')
}

# Animation Settings
ANIMATIONS = {
    'notification_fade_duration': 500,  # milliseconds
    'event_highlight_duration': 1000,
    'time_update_smooth': True
}

# Auto-scroll re-enable timeout (seconds)
# After a user manually scrolls, auto-centering will be disabled for this many seconds.
AUTO_SCROLL_REENABLE_SECONDS = 5
