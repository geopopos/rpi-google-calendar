"""
Event Widget Component
Individual event display widget with futuristic styling
"""

import os
import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime
import pytz

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import THEME, FONTS, TIMEZONE
from ui.styles import get_event_widget_style


class EventWidget(QWidget):
    """Individual event display widget"""
    
    # Signal emitted when event is clicked
    event_clicked = pyqtSignal(dict)
    
    def __init__(self, event_data, parent=None):
        super().__init__(parent)
        self.event_data = event_data
        self.timezone = pytz.timezone(TIMEZONE)
        
        # Set object name for styling
        self.setObjectName("event_widget")
        
        # Setup UI
        self.setup_ui()
        self.update_display()
        
        # Timer for updating current event status
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(60000)  # Update every minute
        
        # Apply initial styling
        self.apply_styling()
    
    def setup_ui(self):
        """Setup the widget UI layout"""
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # Status indicator (left side)
        self.status_indicator = QLabel()
        self.status_indicator.setObjectName("status_indicator")
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_indicator.setFixedWidth(20)
        main_layout.addWidget(self.status_indicator)
        
        # Time display (left side)
        self.time_label = QLabel()
        self.time_label.setObjectName("event_time")
        self.time_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.time_label.setFixedWidth(100)
        main_layout.addWidget(self.time_label)
        
        # Event details (center)
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(2)
        
        # Event title
        self.title_label = QLabel()
        self.title_label.setObjectName("event_title")
        self.title_label.setWordWrap(True)
        details_layout.addWidget(self.title_label)
        
        # Event location (if available)
        self.location_label = QLabel()
        self.location_label.setObjectName("event_location")
        self.location_label.setWordWrap(True)
        self.location_label.hide()  # Hidden by default
        details_layout.addWidget(self.location_label)
        
        main_layout.addLayout(details_layout, 1)  # Stretch factor 1
        
        # Calendar indicator (right side)
        self.calendar_label = QLabel()
        self.calendar_label.setObjectName("calendar_name")
        self.calendar_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.calendar_label.setFixedWidth(80)
        main_layout.addWidget(self.calendar_label)
    
    def update_display(self):
        """Update the widget display with current event data"""
        # Update time
        self.time_label.setText(self.event_data['formatted_time'])
        
        # Update title - NO TRUNCATION, let it wrap naturally
        title = self.event_data['title']
        self.title_label.setText(title)
        
        # Update location if available
        location = self.event_data.get('location', '')
        if location:
            # Allow longer location text to wrap
            self.location_label.setText(f"📍 {location}")
            self.location_label.show()
        else:
            self.location_label.hide()
        
        # Update calendar name - keep short for space
        calendar_name = self.event_data.get('calendar_name', '')
        if len(calendar_name) > 10:
            calendar_name = calendar_name[:8] + "..."
        self.calendar_label.setText(calendar_name)
        
        # Update status indicator
        self.update_status_indicator()
    
    def update_status_indicator(self):
        """Update the status indicator based on event timing"""
        status = self.get_current_status()
        
        status_icons = {
            'past': '✓',
            'current': '▶',
            'upcoming': '○'
        }
        
        icon = status_icons.get(status, '○')
        self.status_indicator.setText(icon)
        
        # Update event data status
        self.event_data['status'] = status
    
    def get_current_status(self):
        """Get the current status of the event"""
        now = datetime.now(self.timezone)
        start_time = self.event_data['start_datetime']
        end_time = self.event_data['end_datetime']
        
        if now < start_time:
            return 'upcoming'
        elif start_time <= now <= end_time:
            return 'current'
        else:
            return 'past'
    
    def update_status(self):
        """Update event status (called by timer)"""
        old_status = self.event_data.get('status', 'upcoming')
        new_status = self.get_current_status()
        
        if old_status != new_status:
            self.event_data['status'] = new_status
            self.update_status_indicator()
            self.apply_styling()  # Re-apply styling for new status
    
    def apply_styling(self):
        """Apply styling based on current event status"""
        status = self.event_data.get('status', 'upcoming')
        style = get_event_widget_style(status)
        self.setStyleSheet(style)
        
        # Add location label styling if visible
        if not self.location_label.isHidden():
            location_style = f"""
            QLabel#event_location {{
                color: {THEME['text_secondary']};
                font-family: {FONTS['event_time'][0]};
                font-size: 12px;
                font-style: italic;
                background: transparent;
                border: none;
            }}
            """
            self.location_label.setStyleSheet(location_style)
        
        # Calendar name styling
        calendar_style = f"""
        QLabel#calendar_name {{
            color: {THEME['text_secondary']};
            font-family: {FONTS['event_time'][0]};
            font-size: 10px;
            background: transparent;
            border: none;
            font-weight: bold;
        }}
        """
        self.calendar_label.setStyleSheet(calendar_style)
    
    def mousePressEvent(self, event):
        """Handle mouse click events"""
        if event.button() == Qt.LeftButton:
            self.event_clicked.emit(self.event_data)
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter events for hover effects"""
        # Add hover glow effect
        current_style = self.styleSheet()
        hover_addition = """
        QWidget#event_widget {
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }
        """
        self.setStyleSheet(current_style + hover_addition)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave events"""
        # Remove hover effects
        self.apply_styling()
        super().leaveEvent(event)
    
    def get_event_data(self):
        """Get the event data"""
        return self.event_data
    
    def update_event_data(self, new_event_data):
        """Update the event data and refresh display"""
        self.event_data = new_event_data
        self.update_display()
        self.apply_styling()
    
    def is_current_event(self):
        """Check if this is the currently active event"""
        return self.event_data.get('status') == 'current'
    
    def is_past_event(self):
        """Check if this is a past event"""
        return self.event_data.get('status') == 'past'
    
    def is_upcoming_event(self):
        """Check if this is an upcoming event"""
        return self.event_data.get('status') == 'upcoming'
    
    def get_time_until_start(self):
        """Get minutes until event starts (negative if past/current)"""
        now = datetime.now(self.timezone)
        start_time = self.event_data['start_datetime']
        time_diff = start_time - now
        return int(time_diff.total_seconds() / 60)
    
    def cleanup(self):
        """Cleanup timers and resources"""
        if self.update_timer:
            self.update_timer.stop()
            self.update_timer = None


class CurrentTimeMarker(QWidget):
    """Widget that shows the current time position in the calendar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timezone = pytz.timezone(TIMEZONE)
        self.setObjectName("current_time_marker")
        self.setup_ui()
        
        # Timer to update current time
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_time)
        self.update_timer.start(1000)  # Update every second
        
        self.update_time()
        self.apply_styling()
    
    def setup_ui(self):
        """Setup the marker UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Left line
        self.left_line = QLabel("━━━")
        self.left_line.setObjectName("time_marker_line")
        layout.addWidget(self.left_line)
        
        # NOW indicator
        self.now_label = QLabel("NOW")
        self.now_label.setObjectName("time_marker_now")
        self.now_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.now_label)
        
        # Current time
        self.time_label = QLabel()
        self.time_label.setObjectName("time_marker_time")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        # Right line
        self.right_line = QLabel("━━━")
        self.right_line.setObjectName("time_marker_line")
        layout.addWidget(self.right_line)
        
        layout.addStretch()
    
    def update_time(self):
        """Update the current time display"""
        from config.settings import TIME_FORMAT_12_HOUR
        now = datetime.now(self.timezone)
        
        if TIME_FORMAT_12_HOUR:
            time_str = now.strftime("%I:%M %p")
        else:
            time_str = now.strftime("%H:%M")
        
        self.time_label.setText(time_str)
    
    def apply_styling(self):
        """Apply styling to the marker"""
        style = f"""
        QWidget#current_time_marker {{
            background: transparent;
            border: none;
            margin: 5px 0px;
        }}
        
        QLabel#time_marker_line {{
            color: {THEME['primary']};
            font-family: {FONTS['event_time'][0]};
            font-size: 14px;
            font-weight: bold;
            background: transparent;
            border: none;
        }}
        
        QLabel#time_marker_now {{
            color: {THEME['primary']};
            font-family: {FONTS['event_title'][0]};
            font-size: 16px;
            font-weight: bold;
            background: rgba(0, 255, 255, 0.1);
            border: 2px solid {THEME['primary']};
            border-radius: 15px;
            padding: 3px 8px;
            min-width: 40px;
        }}
        
        QLabel#time_marker_time {{
            color: {THEME['text_primary']};
            font-family: {FONTS['event_time'][0]};
            font-size: 14px;
            font-weight: bold;
            background: transparent;
            border: none;
            min-width: 80px;
        }}
        """
        self.setStyleSheet(style)
    
    def cleanup(self):
        """Cleanup timer"""
        if self.update_timer:
            self.update_timer.stop()
            self.update_timer = None


class EventListWidget(QWidget):
    """Container widget for multiple event widgets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.event_widgets = []
        self.current_time_marker = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the list layout"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        self.layout.addStretch()  # Add stretch at the end
    
    def add_event(self, event_data):
        """Add an event to the list"""
        event_widget = EventWidget(event_data)
        
        # Insert before the stretch
        self.layout.insertWidget(len(self.event_widgets), event_widget)
        self.event_widgets.append(event_widget)
        
        return event_widget
    
    def clear_events(self):
        """Clear all events from the list"""
        for widget in self.event_widgets:
            widget.cleanup()
            widget.deleteLater()
        
        self.event_widgets.clear()
        
        # Clear current time marker
        if self.current_time_marker:
            self.current_time_marker.cleanup()
            self.current_time_marker.deleteLater()
            self.current_time_marker = None
    
    def update_events(self, events_data):
        """Update the list with new events data"""
        self.clear_events()
        
        for event_data in events_data:
            self.add_event(event_data)
        
        # Add current time marker in the correct position
        self.add_current_time_marker()
    
    def add_current_time_marker(self):
        """Add the current time marker in the appropriate position"""
        if not self.event_widgets:
            return
        
        now = datetime.now(pytz.timezone(TIMEZONE))
        marker_position = 0
        
        # Find the correct position for the marker
        for i, widget in enumerate(self.event_widgets):
            event_start = widget.event_data['start_datetime']
            
            # If current time is before this event's start time
            if now < event_start:
                marker_position = i
                break
            else:
                marker_position = i + 1
        
        # Create and insert the marker
        self.current_time_marker = CurrentTimeMarker()
        self.layout.insertWidget(marker_position, self.current_time_marker)
    
    def update_current_time_marker_position(self):
        """Update the position of the current time marker if needed"""
        if not self.current_time_marker or not self.event_widgets:
            return
        
        now = datetime.now(pytz.timezone(TIMEZONE))
        current_position = self.layout.indexOf(self.current_time_marker)
        correct_position = 0
        
        # First, check if there's a currently active event
        current_event_widget = None
        for widget in self.event_widgets:
            if widget.is_current_event():
                current_event_widget = widget
                break
        
        if current_event_widget:
            # If there's a current event, position marker at that event
            widget_position = self.layout.indexOf(current_event_widget)
            correct_position = widget_position
        else:
            # No current event, use time-based positioning (original logic)
            for i, widget in enumerate(self.event_widgets):
                event_start = widget.event_data['start_datetime']
                widget_position = self.layout.indexOf(widget)
                
                if now < event_start:
                    correct_position = widget_position
                    break
                else:
                    correct_position = widget_position + 1
        
        # Move marker if it's in the wrong position
        if current_position != correct_position:
            self.layout.removeWidget(self.current_time_marker)
            self.layout.insertWidget(correct_position, self.current_time_marker)
    
    def get_current_event_widget(self):
        """Get the widget for the currently active event"""
        for widget in self.event_widgets:
            if widget.is_current_event():
                return widget
        return None
    
    def get_event_count(self):
        """Get the number of events in the list"""
        return len(self.event_widgets)


if __name__ == "__main__":
    # Test the event widget
    import sys
    from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
    from datetime import datetime, timedelta
    import pytz
    
    app = QApplication(sys.argv)
    
    # Create test window
    window = QWidget()
    window.setWindowTitle("Event Widget Test")
    window.resize(600, 400)
    window.setStyleSheet("background-color: #0a0a0a;")
    
    layout = QVBoxLayout(window)
    
    # Create test events
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    
    test_events = [
        {
            'id': '1',
            'title': 'Team Meeting - Weekly Standup',
            'location': 'Conference Room A',
            'start_datetime': now - timedelta(hours=1),
            'end_datetime': now - timedelta(minutes=30),
            'formatted_time': '9:00 AM - 10:00 AM',
            'calendar_name': 'Work',
            'status': 'past'
        },
        {
            'id': '2',
            'title': 'Current Event - Lunch Break',
            'location': 'Cafeteria',
            'start_datetime': now - timedelta(minutes=15),
            'end_datetime': now + timedelta(minutes=45),
            'formatted_time': '12:00 PM - 1:00 PM',
            'calendar_name': 'Personal',
            'status': 'current'
        },
        {
            'id': '3',
            'title': 'Project Review with Client',
            'location': 'Zoom Meeting',
            'start_datetime': now + timedelta(hours=2),
            'end_datetime': now + timedelta(hours=3),
            'formatted_time': '3:00 PM - 4:00 PM',
            'calendar_name': 'Work',
            'status': 'upcoming'
        }
    ]
    
    # Create event widgets
    for event_data in test_events:
        event_widget = EventWidget(event_data)
        layout.addWidget(event_widget)
    
    layout.addStretch()
    
    window.show()
    sys.exit(app.exec_())
