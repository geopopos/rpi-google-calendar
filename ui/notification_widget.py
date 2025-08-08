"""
Notification Widget Component
Overlay notification display for event alerts
"""

import os
import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime
import pytz

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import THEME, FONTS, TIMEZONE, ANIMATIONS
from ui.styles import get_notification_style


class NotificationWidget(QWidget):
    """Notification overlay widget for event alerts"""
    
    # Signals
    dismissed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timezone = pytz.timezone(TIMEZONE)
        self.current_event = None
        self.notification_type = None
        
        # Set object name for styling
        self.setObjectName("notification_overlay")
        
        # Setup UI
        self.setup_ui()
        
        # Animation setup
        self.setup_animations()
        
        # Hide initially
        self.hide()
        
        # Auto-dismiss timer
        self.auto_dismiss_timer = QTimer()
        self.auto_dismiss_timer.timeout.connect(self.auto_dismiss)
        self.auto_dismiss_timer.setSingleShot(True)
    
    def setup_ui(self):
        """Setup the notification UI"""
        # Make widget fill parent and stay on top
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Notification container
        self.notification_container = QWidget()
        self.notification_container.setObjectName("notification_container")
        self.notification_container.setFixedSize(400, 250)
        
        container_layout = QVBoxLayout(self.notification_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        container_layout.setAlignment(Qt.AlignCenter)
        
        # Title label
        self.title_label = QLabel()
        self.title_label.setObjectName("notification_title")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        container_layout.addWidget(self.title_label)
        
        # Subtitle (event name)
        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("notification_subtitle")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        container_layout.addWidget(self.subtitle_label)
        
        # Message label
        self.message_label = QLabel()
        self.message_label.setObjectName("notification_message")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        container_layout.addWidget(self.message_label)
        
        # Time label
        self.time_label = QLabel()
        self.time_label.setObjectName("notification_time")
        self.time_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(self.time_label)
        
        # Spacer
        container_layout.addStretch()
        
        # Dismiss button
        self.dismiss_button = QPushButton("DISMISS")
        self.dismiss_button.setObjectName("dismiss_button")
        self.dismiss_button.clicked.connect(self.dismiss)
        self.dismiss_button.setFixedHeight(40)
        container_layout.addWidget(self.dismiss_button)
        
        main_layout.addWidget(self.notification_container)
    
    def setup_animations(self):
        """Setup fade in/out animations"""
        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect()
        self.notification_container.setGraphicsEffect(self.opacity_effect)
        
        # Fade in animation
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(ANIMATIONS['notification_fade_duration'])
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Fade out animation
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(ANIMATIONS['notification_fade_duration'])
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out_animation.finished.connect(self.hide)
    
    def show_notification(self, event_data, notification_type):
        """Show notification for an event"""
        self.current_event = event_data
        self.notification_type = notification_type
        
        # Update content
        self.update_content()
        
        # Apply styling
        self.apply_styling()
        
        # Show and animate
        self.show()
        self.raise_()  # Bring to front
        self.fade_in_animation.start()
        
        # Start auto-dismiss timer (30 seconds)
        self.auto_dismiss_timer.start(30000)
        
        print(f"Showing {notification_type} notification for: {event_data['title']}")
    
    def update_content(self):
        """Update notification content based on event and type"""
        if not self.current_event or not self.notification_type:
            return
        
        event = self.current_event
        
        if self.notification_type == 'warning':
            self.title_label.setText("⚠️ UPCOMING EVENT ⚠️")
            self.subtitle_label.setText(event['title'])
            
            # Calculate minutes until start
            now = datetime.now(self.timezone)
            time_diff = event['start_datetime'] - now
            minutes = int(time_diff.total_seconds() / 60)
            
            if minutes > 0:
                self.message_label.setText(f"Starts in {minutes} minutes")
            else:
                self.message_label.setText("Starting soon")
                
        elif self.notification_type == 'start':
            self.title_label.setText("🔴 EVENT STARTING NOW 🔴")
            self.subtitle_label.setText(event['title'])
            self.message_label.setText("Your event is starting now!")
        
        # Set time
        self.time_label.setText(event['formatted_time'])
        
        # Add location if available
        location = event.get('location', '')
        if location:
            current_message = self.message_label.text()
            self.message_label.setText(f"{current_message}\n📍 {location}")
    
    def apply_styling(self):
        """Apply styling based on notification type"""
        style = get_notification_style(self.notification_type)
        self.setStyleSheet(style)
        
        # Additional container styling
        container_style = f"""
        QWidget#notification_container {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                       stop:0 rgba(0, 0, 0, 0.95),
                                       stop:0.5 rgba(255, 69, 0, 0.2),
                                       stop:1 rgba(0, 0, 0, 0.95));
            border: 3px solid {THEME['warning'] if self.notification_type == 'warning' else THEME['error']};
            border-radius: 15px;
        }}
        """
        self.notification_container.setStyleSheet(container_style)
    
    def dismiss(self):
        """Dismiss the notification"""
        self.auto_dismiss_timer.stop()
        self.fade_out_animation.start()
        self.dismissed.emit()
        print("Notification dismissed by user")
    
    def auto_dismiss(self):
        """Auto-dismiss the notification"""
        self.fade_out_animation.start()
        self.dismissed.emit()
        print("Notification auto-dismissed")
    
    def is_showing(self):
        """Check if notification is currently showing"""
        return self.isVisible() and self.opacity_effect.opacity() > 0
    
    def get_current_event(self):
        """Get the current event being displayed"""
        return self.current_event
    
    def get_notification_type(self):
        """Get the current notification type"""
        return self.notification_type
    
    def mousePressEvent(self, event):
        """Handle mouse clicks - dismiss on click outside button"""
        if event.button() == Qt.LeftButton:
            # Check if click is outside the notification container
            container_rect = self.notification_container.geometry()
            if not container_rect.contains(event.pos()):
                self.dismiss()
        super().mousePressEvent(event)
    
    def keyPressEvent(self, event):
        """Handle key presses - dismiss on Escape"""
        if event.key() == Qt.Key_Escape:
            self.dismiss()
        super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        """Handle resize events to keep notification centered"""
        super().resizeEvent(event)
        if hasattr(self, 'notification_container'):
            # Center the notification container
            container_size = self.notification_container.size()
            parent_size = self.size()
            
            x = (parent_size.width() - container_size.width()) // 2
            y = (parent_size.height() - container_size.height()) // 2
            
            self.notification_container.move(x, y)


class NotificationManager(QWidget):
    """Manager for handling multiple notification types"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notification_widget = NotificationWidget(self)
        self.notification_widget.dismissed.connect(self.on_notification_dismissed)
        
        # Queue for pending notifications
        self.notification_queue = []
        self.current_notification = None
        
        # Timer for processing queue
        self.queue_timer = QTimer()
        self.queue_timer.timeout.connect(self.process_queue)
        self.queue_timer.start(1000)  # Check every second
    
    def show_notification(self, event_data, notification_type):
        """Show a notification (queue if one is already showing)"""
        notification = {
            'event': event_data,
            'type': notification_type,
            'timestamp': datetime.now(pytz.timezone(TIMEZONE))
        }
        
        if self.notification_widget.is_showing():
            # Add to queue if not already there
            if not any(n['event']['id'] == event_data['id'] and n['type'] == notification_type 
                      for n in self.notification_queue):
                self.notification_queue.append(notification)
                print(f"Queued notification: {notification_type} for {event_data['title']}")
        else:
            # Show immediately
            self.current_notification = notification
            self.notification_widget.show_notification(event_data, notification_type)
    
    def process_queue(self):
        """Process the notification queue"""
        if not self.notification_widget.is_showing() and self.notification_queue:
            # Show next notification in queue
            next_notification = self.notification_queue.pop(0)
            self.current_notification = next_notification
            self.notification_widget.show_notification(
                next_notification['event'], 
                next_notification['type']
            )
    
    def on_notification_dismissed(self):
        """Handle notification dismissal"""
        self.current_notification = None
        # Process queue will handle showing next notification
    
    def dismiss_current(self):
        """Dismiss the current notification"""
        if self.notification_widget.is_showing():
            self.notification_widget.dismiss()
    
    def clear_queue(self):
        """Clear all pending notifications"""
        self.notification_queue.clear()
        print("Cleared notification queue")
    
    def get_queue_size(self):
        """Get the number of pending notifications"""
        return len(self.notification_queue)
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        if hasattr(self, 'notification_widget'):
            self.notification_widget.resize(self.size())


if __name__ == "__main__":
    # Test the notification widget
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
    from datetime import datetime, timedelta
    import pytz
    
    app = QApplication(sys.argv)
    
    # Create test window
    window = QMainWindow()
    window.setWindowTitle("Notification Widget Test")
    window.resize(800, 600)
    window.setStyleSheet("background-color: #0a0a0a;")
    
    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout(central_widget)
    
    # Create notification manager
    notification_manager = NotificationManager(central_widget)
    
    # Test buttons
    warning_button = QPushButton("Test Warning Notification")
    start_button = QPushButton("Test Start Notification")
    
    layout.addWidget(warning_button)
    layout.addWidget(start_button)
    layout.addStretch()
    
    # Test event data
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    
    test_event = {
        'id': 'test_event',
        'title': 'Important Meeting with Client',
        'location': 'Conference Room A',
        'start_datetime': now + timedelta(minutes=10),
        'end_datetime': now + timedelta(hours=1),
        'formatted_time': '2:00 PM - 3:00 PM',
        'calendar_name': 'Work'
    }
    
    # Connect buttons
    warning_button.clicked.connect(
        lambda: notification_manager.show_notification(test_event, 'warning')
    )
    start_button.clicked.connect(
        lambda: notification_manager.show_notification(test_event, 'start')
    )
    
    window.show()
    sys.exit(app.exec_())
