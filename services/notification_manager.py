"""
Notification Manager
Handles event notifications and alerts
"""

import os
import sys
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
import pytz

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import WARNING_MINUTES, NOTIFICATION_TIMEOUT, TIMEZONE


class NotificationManager(QObject):
    """Manages event notifications and timing"""
    
    # Signals for UI updates
    show_notification = pyqtSignal(dict, str)  # event, notification_type
    hide_notification = pyqtSignal()
    
    def __init__(self, calendar_service):
        super().__init__()
        self.calendar_service = calendar_service
        self.timezone = pytz.timezone(TIMEZONE)
        
        # Track shown notifications to avoid duplicates
        self.shown_notifications = set()
        
        # Timer for checking notifications
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.check_notifications)
        self.notification_timer.start(30000)  # Check every 30 seconds
        
        # Timer for auto-dismissing notifications
        self.dismiss_timer = QTimer()
        self.dismiss_timer.timeout.connect(self.auto_dismiss_notification)
        self.dismiss_timer.setSingleShot(True)
        
        # Current notification state
        self.current_notification = None
        self.notification_start_time = None
        
    def check_notifications(self):
        """
        Check for events that need notifications
        Called periodically by timer
        """
        try:
            notifications = self.calendar_service.get_events_needing_notification(WARNING_MINUTES)
            
            for event, notification_type in notifications:
                notification_key = f"{event['id']}_{notification_type}"
                
                # Skip if we've already shown this notification
                if notification_key in self.shown_notifications:
                    continue
                
                # Show the notification
                self.show_event_notification(event, notification_type)
                
                # Mark as shown
                self.shown_notifications.add(notification_key)
                
                # Clean up old notification keys (older than 2 hours)
                self._cleanup_old_notifications()
                
        except Exception as error:
            print(f"Error checking notifications: {error}")
    
    def show_event_notification(self, event, notification_type):
        """
        Show a notification for an event
        """
        try:
            # Dismiss any current notification first
            if self.current_notification:
                self.hide_notification.emit()
            
            # Set current notification
            self.current_notification = {
                'event': event,
                'type': notification_type,
                'timestamp': datetime.now(self.timezone)
            }
            self.notification_start_time = datetime.now(self.timezone)
            
            # Emit signal to show notification in UI
            self.show_notification.emit(event, notification_type)
            
            # Start auto-dismiss timer
            self.dismiss_timer.start(NOTIFICATION_TIMEOUT * 1000)
            
            print(f"Showing {notification_type} notification for: {event['title']}")
            
        except Exception as error:
            print(f"Error showing notification: {error}")
    
    def dismiss_notification(self):
        """
        Manually dismiss the current notification
        """
        if self.current_notification:
            self.hide_notification.emit()
            self.current_notification = None
            self.notification_start_time = None
            self.dismiss_timer.stop()
    
    def auto_dismiss_notification(self):
        """
        Auto-dismiss notification after timeout
        """
        if self.current_notification:
            print(f"Auto-dismissing notification after {NOTIFICATION_TIMEOUT} seconds")
            self.dismiss_notification()
    
    def get_notification_message(self, event, notification_type):
        """
        Generate notification message text
        """
        if notification_type == 'warning':
            minutes_until = self.calendar_service.get_time_until_next_event()
            if minutes_until and minutes_until <= WARNING_MINUTES:
                return {
                    'title': '⚠️ UPCOMING EVENT ⚠️',
                    'subtitle': event['title'],
                    'message': f"Starts in {minutes_until} minutes",
                    'time': event['formatted_time']
                }
        
        elif notification_type == 'start':
            return {
                'title': '🔴 EVENT STARTING NOW 🔴',
                'subtitle': event['title'],
                'message': 'Starting now',
                'time': event['formatted_time']
            }
        
        return {
            'title': 'Event Notification',
            'subtitle': event['title'],
            'message': 'Event notification',
            'time': event['formatted_time']
        }
    
    def _cleanup_old_notifications(self):
        """
        Remove old notification keys to prevent memory buildup
        """
        try:
            # Remove notifications older than 2 hours
            cutoff_time = datetime.now(self.timezone) - timedelta(hours=2)
            
            # Since we can't easily track timestamps for each key,
            # we'll just clear all if we have too many
            if len(self.shown_notifications) > 100:
                self.shown_notifications.clear()
                print("Cleared old notification cache")
                
        except Exception as error:
            print(f"Error cleaning up notifications: {error}")
    
    def reset_notifications(self):
        """
        Reset all notification tracking (useful for testing or daily reset)
        """
        self.shown_notifications.clear()
        self.dismiss_notification()
        print("Reset all notifications")
    
    def is_notification_active(self):
        """
        Check if a notification is currently being displayed
        """
        return self.current_notification is not None
    
    def get_current_notification(self):
        """
        Get the current notification details
        """
        return self.current_notification
    
    def start_monitoring(self):
        """
        Start notification monitoring
        """
        if not self.notification_timer.isActive():
            self.notification_timer.start(30000)
            print("Started notification monitoring")
    
    def stop_monitoring(self):
        """
        Stop notification monitoring
        """
        self.notification_timer.stop()
        self.dismiss_timer.stop()
        self.dismiss_notification()
        print("Stopped notification monitoring")
    
    def force_check_notifications(self):
        """
        Force an immediate check for notifications (useful for testing)
        """
        self.check_notifications()


class NotificationTester:
    """Helper class for testing notifications"""
    
    def __init__(self, notification_manager):
        self.notification_manager = notification_manager
    
    def create_test_event(self, title, minutes_from_now):
        """Create a test event for notification testing"""
        now = datetime.now(pytz.timezone(TIMEZONE))
        start_time = now + timedelta(minutes=minutes_from_now)
        end_time = start_time + timedelta(hours=1)
        
        return {
            'id': f'test_{minutes_from_now}',
            'title': title,
            'description': 'Test event for notifications',
            'location': 'Test Location',
            'start_datetime': start_time,
            'end_datetime': end_time,
            'is_all_day': False,
            'calendar_name': 'Test Calendar',
            'calendar_color': '#ff0000',
            'status': 'upcoming',
            'formatted_time': start_time.strftime("%I:%M %p").lstrip('0')
        }
    
    def test_warning_notification(self):
        """Test a 10-minute warning notification"""
        test_event = self.create_test_event("Test Warning Event", WARNING_MINUTES)
        self.notification_manager.show_event_notification(test_event, 'warning')
    
    def test_start_notification(self):
        """Test an event start notification"""
        test_event = self.create_test_event("Test Start Event", 0)
        self.notification_manager.show_event_notification(test_event, 'start')


if __name__ == "__main__":
    # Test the notification manager
    from services.calendar_service import CalendarService
    
    calendar_service = CalendarService()
    notification_manager = NotificationManager(calendar_service)
    
    # Test notifications
    tester = NotificationTester(notification_manager)
    
    print("Testing notification system...")
    print("1. Testing warning notification...")
    tester.test_warning_notification()
    
    print("2. Testing start notification...")
    tester.test_start_notification()
