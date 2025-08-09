"""
Main Application Window
Futuristic Google Calendar Display for Raspberry Pi
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QScrollArea, QFrame, QApplication, QScroller)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent
from PyQt5.QtGui import QFont, QCursor
from datetime import datetime
import pytz

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import (SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN, HIDE_CURSOR,
                             REFRESH_INTERVAL, TIMEZONE, THEME, FONTS, APP_NAME,
                             AUTO_SCROLL_REENABLE_SECONDS, TIME_FORMAT_12_HOUR)
from services.calendar_service import CalendarService
from services.notification_manager import NotificationManager
from ui.styles import get_combined_stylesheet, load_custom_fonts
from ui.event_widget import EventListWidget
from ui.notification_widget import NotificationManager as UINotificationManager


class HeaderWidget(QWidget):
    """Header widget displaying time, date, and status"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timezone = pytz.timezone(TIMEZONE)
        self.setObjectName("header")
        self.setup_ui()
        
        # Timer for updating time display
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)  # Update every second
        
        # Initial time update
        self.update_time()
    
    def setup_ui(self):
        """Setup header UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignCenter)
        
        # Time display
        self.time_label = QLabel()
        self.time_label.setObjectName("time_display")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        # Date display
        self.date_label = QLabel()
        self.date_label.setObjectName("date_display")
        self.date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.date_label)
        
        # Status display
        self.status_label = QLabel()
        self.status_label.setObjectName("status_display")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.hide()  # Hidden by default
        layout.addWidget(self.status_label)
    
    def update_time(self):
        """Update time and date display"""
        now = datetime.now(self.timezone)
        
        # Format time based on configuration
        if TIME_FORMAT_12_HOUR:
            time_str = now.strftime("%I:%M:%S %p")
        else:
            time_str = now.strftime("%H:%M:%S")
        self.time_label.setText(time_str)
        
        # Format date with separators and remove leading zero
        day = now.day
        date_str = now.strftime(f"%A • %B {day} • %Y")
        self.date_label.setText(date_str)
    
    def show_status(self, message, duration=3000):
        """Show a temporary status message"""
        self.status_label.setText(message)
        self.status_label.show()
        
        # Hide after duration
        QTimer.singleShot(duration, self.status_label.hide)


class CalendarDisplayWindow(QMainWindow):
    """Main calendar display window"""
    
    # Signals
    events_updated = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.timezone = pytz.timezone(TIMEZONE)
        
        # Services
        self.calendar_service = CalendarService()
        self.notification_manager = NotificationManager(self.calendar_service)
        
        # UI Components
        self.header_widget = None
        self.event_list_widget = None
        self.ui_notification_manager = None
        self.no_events_label = None
        self.scroll_area = None
        # Track whether the user has manually scrolled to avoid auto-scrolling
        self.user_scrolled = False
        # Timer to re-enable auto-scroll after user interaction
        self._auto_scroll_timer = QTimer()
        self._auto_scroll_timer.setSingleShot(True)
        self._auto_scroll_timer.timeout.connect(lambda: setattr(self, 'user_scrolled', False))
        
        # State
        self.current_events = []
        self.last_refresh = None
        
        # Setup
        self.setup_window()
        self.setup_ui()
        self.setup_timers()
        self.setup_connections()
        
        # Load custom fonts
        load_custom_fonts()
        
        # Apply styling
        self.setStyleSheet(get_combined_stylesheet())
        
        # Initial data load
        self.refresh_calendar_data()
        
        print(f"Calendar Display initialized for {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    
    def setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle(APP_NAME)
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Set window flags for fullscreen kiosk mode
        if FULLSCREEN:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            self.showFullScreen()
        
        # Hide cursor if specified
        if HIDE_CURSOR:
            self.setCursor(QCursor(Qt.BlankCursor))
        
        # Set background
        self.setStyleSheet(f"background-color: {THEME['background']};")
    
    def setup_ui(self):
        """Setup the main UI layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.header_widget = HeaderWidget()
        main_layout.addWidget(self.header_widget)
        
        # Events section
        self.setup_events_section(main_layout)
        
        # Notification overlay
        self.ui_notification_manager = UINotificationManager(central_widget)
        
        # Ensure notification overlay covers the entire window
        self.ui_notification_manager.resize(self.size())
    
    def setup_events_section(self, parent_layout):
        """Setup the events display section"""
        # Scroll area for events
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Event list widget
        self.event_list_widget = EventListWidget()
        self.scroll_area.setWidget(self.event_list_widget)
        
        # Enable touch events on the viewport for touchscreen support
        viewport = self.scroll_area.viewport()
        viewport.setAttribute(Qt.WA_AcceptTouchEvents, True)
        # Install event filter to detect manual user interaction (touch/mouse)
        viewport.installEventFilter(self)
        
        # Enable kinetic (momentum) scrolling via QScroller where available
        try:
            # Prefer touch gesture; fall back to left-mouse-button gesture
            try:
                QScroller.grabGesture(viewport, QScroller.TouchGesture)
            except Exception:
                QScroller.grabGesture(viewport, QScroller.LeftMouseButtonGesture)
        except Exception:
            # If QScroller isn't supported in this environment, ignore and fall back to synthesized events
            pass

        # Track manual user scrolling via the scrollbar as well to avoid fighting their interaction
        try:
            vbar = self.scroll_area.verticalScrollBar()
            vbar.sliderPressed.connect(lambda: setattr(self, 'user_scrolled', True))
        except Exception:
            pass
        
        # No events message
        self.no_events_label = QLabel("No events scheduled for today")
        self.no_events_label.setObjectName("no_events")
        self.no_events_label.setAlignment(Qt.AlignCenter)
        self.no_events_label.hide()
        
        # Add to layout
        parent_layout.addWidget(self.scroll_area, 1)  # Stretch factor 1
        parent_layout.addWidget(self.no_events_label)
    
    def setup_timers(self):
        """Setup application timers"""
        # Calendar refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_calendar_data)
        self.refresh_timer.start(REFRESH_INTERVAL * 1000)  # Convert to milliseconds
        
        # Status update timer (every minute)
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_event_statuses)
        self.status_timer.start(60000)  # 1 minute
        
        # Time marker position update timer (every 30 seconds)
        self.marker_timer = QTimer()
        self.marker_timer.timeout.connect(self.update_time_marker_position)
        self.marker_timer.start(30000)  # 30 seconds
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect notification manager signals
        self.notification_manager.show_notification.connect(
            self.ui_notification_manager.show_notification
        )
        self.notification_manager.hide_notification.connect(
            self.ui_notification_manager.dismiss_current
        )
        
        # Connect events updated signal
        self.events_updated.connect(self.on_events_updated)
    
    def refresh_calendar_data(self):
        """Refresh calendar data from Google Calendar"""
        try:
            self.header_widget.show_status("Refreshing calendar...", 2000)
            
            # Fetch events
            events = self.calendar_service.get_today_events()
            
            # Update UI
            self.current_events = events
            self.last_refresh = datetime.now(self.timezone)
            
            # Emit signal
            self.events_updated.emit(events)
            
            # Update status
            if events:
                self.header_widget.show_status(f"Loaded {len(events)} events", 2000)
            else:
                self.header_widget.show_status("No events today", 2000)
                
            print(f"Calendar refreshed: {len(events)} events loaded")
            
        except Exception as error:
            print(f"Error refreshing calendar: {error}")
            self.header_widget.show_status("Calendar refresh failed", 3000)
    
    def on_events_updated(self, events):
        """Handle events updated signal"""
        if events:
            # Show event list
            self.event_list_widget.update_events(events)
            self.event_list_widget.show()
            self.no_events_label.hide()
            # Auto-scroll to the current/next event unless the user has manually scrolled
            if not getattr(self, 'user_scrolled', False):
                # Delay slightly to allow layout to settle
                QTimer.singleShot(200, self.scroll_to_closest_event)
        else:
            # Show no events message
            self.event_list_widget.hide()
            self.no_events_label.show()
    
    def update_event_statuses(self):
        """Update event statuses (called every minute)"""
        if not self.current_events:
            return
        
        # Track if any event transitions from current to past
        marker_needs_update = False
        
        # Update statuses in calendar service
        for event in self.current_events:
            now = datetime.now(self.timezone)
            start_time = event['start_datetime']
            end_time = event['end_datetime']
            
            old_status = event.get('status', 'upcoming')
            
            if now < start_time:
                event['status'] = 'upcoming'
            elif start_time <= now <= end_time:
                event['status'] = 'current'
            else:
                event['status'] = 'past'
            
            # Check if an event just ended (transitioned from current to past)
            if old_status == 'current' and event['status'] == 'past':
                marker_needs_update = True
        
        # Update UI
        self.events_updated.emit(self.current_events)
        
        # Force marker position update if an event just ended
        if marker_needs_update:
            self.update_time_marker_position()
        
        print("Event statuses updated")

    def update_time_marker_position(self):
        """Update the position of the current time marker"""
        if hasattr(self, 'event_list_widget') and self.event_list_widget:
            self.event_list_widget.update_current_time_marker_position()

    def scroll_to_closest_event(self):
        """Scroll the events list to center the current or next upcoming event."""
        if not hasattr(self, 'scroll_area') or self.scroll_area is None:
            return
        target_widget = None
        # Prefer the current event widget
        if hasattr(self, 'event_list_widget'):
            target_widget = self.event_list_widget.get_current_event_widget()
            if not target_widget:
                # Find first upcoming event
                for w in self.event_list_widget.event_widgets:
                    if w.is_upcoming_event():
                        target_widget = w
                        break
            if not target_widget and self.event_list_widget.event_widgets:
                target_widget = self.event_list_widget.event_widgets[0]
        if not target_widget:
            return
        # Center the widget in the viewport
        bar = self.scroll_area.verticalScrollBar()
        widget_y = target_widget.y()
        viewport_height = self.scroll_area.viewport().height()
        center_value = int(widget_y - (viewport_height // 2) + (target_widget.height() // 2))
        bar.setValue(max(0, center_value))
    
    def eventFilter(self, obj, event):
        """Handle touch/mouse events on the scroll viewport to detect manual user interaction."""
        try:
            if obj is self.scroll_area.viewport():
                if event.type() in (QEvent.TouchBegin, QEvent.TouchUpdate, QEvent.TouchEnd,
                                    QEvent.MouseButtonPress, QEvent.MouseMove, QEvent.MouseButtonRelease):
                    # Mark that user interacted; cancel auto-centering for a while
                    self.user_scrolled = True
                    # Restart the auto-scroll re-enable timer so it counts from the last interaction
                    try:
                        self._auto_scroll_timer.start(int(AUTO_SCROLL_REENABLE_SECONDS * 1000))
                    except Exception:
                        # Fallback to singleShot if timer not available
                        QTimer.singleShot(int(AUTO_SCROLL_REENABLE_SECONDS * 1000), lambda: setattr(self, 'user_scrolled', False))
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def get_current_event(self):
        """Get the currently active event"""
        return self.calendar_service.get_current_event()
    
    def get_next_event(self):
        """Get the next upcoming event"""
        return self.calendar_service.get_next_event()
    
    def get_events_count(self):
        """Get the number of events for today"""
        return len(self.current_events)
    
    def force_refresh(self):
        """Force an immediate calendar refresh"""
        self.refresh_calendar_data()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        key = event.key()
        
        if key == Qt.Key_Escape:
            # Exit fullscreen or close app
            if self.isFullScreen():
                self.showNormal()
            else:
                self.close()
        
        elif key == Qt.Key_F11:
            # Toggle fullscreen
            self.toggle_fullscreen()
        
        elif key == Qt.Key_F5:
            # Force refresh
            self.force_refresh()
        
        elif key == Qt.Key_Q and event.modifiers() == Qt.ControlModifier:
            # Quit application
            self.close()
        
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            # Dismiss any active notifications (only if notification manager exists)
            if (hasattr(self, 'ui_notification_manager') and 
                self.ui_notification_manager is not None and
                hasattr(self.ui_notification_manager, 'notification_widget') and
                self.ui_notification_manager.notification_widget.is_showing()):
                self.ui_notification_manager.dismiss_current()
        
        super().mousePressEvent(event)
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        
        # Resize notification overlay (only if it exists and is not None)
        if hasattr(self, 'ui_notification_manager') and self.ui_notification_manager is not None:
            self.ui_notification_manager.resize(self.size())
    
    def closeEvent(self, event):
        """Handle window close event"""
        print("Shutting down calendar display...")
        
        # Stop timers
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        if hasattr(self, 'marker_timer'):
            self.marker_timer.stop()
        
        # Stop notification monitoring
        if hasattr(self, 'notification_manager'):
            self.notification_manager.stop_monitoring()
        
        # Cleanup event widgets
        if hasattr(self, 'event_list_widget'):
            self.event_list_widget.clear_events()
        
        event.accept()


def main():
    """Main application entry point"""
    # Set application properties BEFORE creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    # Enable touch/mouse synthesis so touchscreens without full Qt touch drivers still work
    QApplication.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTouchEvents, True)
    QApplication.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("Calendar Display")
    
    try:
        # Create and show main window
        window = CalendarDisplayWindow()
        window.show()
        
        print(f"Starting {APP_NAME}...")
        print(f"Screen resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        print(f"Fullscreen mode: {FULLSCREEN}")
        print(f"Refresh interval: {REFRESH_INTERVAL} seconds")
        print("Press F5 to refresh, F11 to toggle fullscreen, Esc to exit")
        
        # Run application
        sys.exit(app.exec_())
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as error:
        print(f"Application error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
