"""
Google Calendar Service
Handles fetching and processing calendar events
"""

import os
import sys
from datetime import datetime, timedelta
import pytz
from googleapiclient.errors import HttpError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import TIMEZONE, MAX_EVENTS_DISPLAY
from services.google_auth import GoogleCalendarAuth


class CalendarService:
    """Manages calendar events and data"""
    
    def __init__(self):
        self.auth = GoogleCalendarAuth()
        self.timezone = pytz.timezone(TIMEZONE)
        self.events = []
        self.last_update = None
        
    def get_today_events(self):
        """
        Fetch today's events from all calendars
        Returns list of events sorted by start time
        """
        try:
            service = self.auth.get_service()
            if not service:
                print("Failed to get calendar service")
                return []
            
            # Get start and end of today in the specified timezone
            now = datetime.now(self.timezone)
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Convert to UTC for API call
            time_min = start_of_day.astimezone(pytz.UTC).isoformat()
            time_max = end_of_day.astimezone(pytz.UTC).isoformat()
            
            all_events = []
            
            # Get list of calendars
            calendars = self.auth.get_calendar_list()
            
            for calendar in calendars:
                try:
                    # Fetch events for this calendar
                    events_result = service.events().list(
                        calendarId=calendar['id'],
                        timeMin=time_min,
                        timeMax=time_max,
                        singleEvents=True,
                        orderBy='startTime',
                        maxResults=MAX_EVENTS_DISPLAY
                    ).execute()
                    
                    events = events_result.get('items', [])
                    
                    # Process each event
                    for event in events:
                        processed_event = self._process_event(event, calendar)
                        if processed_event:
                            all_events.append(processed_event)
                            
                except HttpError as error:
                    print(f"Error fetching events from calendar {calendar['summary']}: {error}")
                    continue
            
            # Sort all events by start time
            all_events.sort(key=lambda x: x['start_datetime'])
            
            # Limit to max display count
            self.events = all_events[:MAX_EVENTS_DISPLAY]
            self.last_update = datetime.now(self.timezone)
            
            print(f"Fetched {len(self.events)} events for today")
            return self.events
            
        except Exception as error:
            print(f"Error fetching today's events: {error}")
            return []
    
    def _process_event(self, event, calendar):
        """
        Process a raw event from Google Calendar API
        Returns processed event dict or None if invalid
        """
        try:
            # Get event start time
            start = event['start'].get('dateTime', event['start'].get('date'))
            if not start:
                return None
            
            # Parse start time
            if 'T' in start:  # DateTime event
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                if start_dt.tzinfo is None:
                    start_dt = self.timezone.localize(start_dt)
                else:
                    start_dt = start_dt.astimezone(self.timezone)
                is_all_day = False
            else:  # All-day event
                start_dt = datetime.strptime(start, '%Y-%m-%d')
                start_dt = self.timezone.localize(start_dt)
                is_all_day = True
            
            # Get event end time
            end = event['end'].get('dateTime', event['end'].get('date'))
            if end and 'T' in end:
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                if end_dt.tzinfo is None:
                    end_dt = self.timezone.localize(end_dt)
                else:
                    end_dt = end_dt.astimezone(self.timezone)
            else:
                end_dt = start_dt + timedelta(hours=1)  # Default 1 hour duration
            
            # Create processed event
            processed_event = {
                'id': event['id'],
                'title': event.get('summary', 'No Title'),
                'description': event.get('description', ''),
                'location': event.get('location', ''),
                'start_datetime': start_dt,
                'end_datetime': end_dt,
                'is_all_day': is_all_day,
                'calendar_name': calendar['summary'],
                'calendar_color': calendar.get('backgroundColor', '#ffffff'),
                'status': self._get_event_status(start_dt, end_dt),
                'formatted_time': self._format_event_time(start_dt, end_dt, is_all_day)
            }
            
            return processed_event
            
        except Exception as error:
            print(f"Error processing event: {error}")
            return None
    
    def _get_event_status(self, start_dt, end_dt):
        """
        Determine event status (past, current, upcoming)
        """
        now = datetime.now(self.timezone)
        
        if now < start_dt:
            return 'upcoming'
        elif start_dt <= now <= end_dt:
            return 'current'
        else:
            return 'past'
    
    def _format_event_time(self, start_dt, end_dt, is_all_day):
        """
        Format event time for display
        """
        if is_all_day:
            return "All Day"
        
        start_time = start_dt.strftime("%I:%M %p").lstrip('0')
        end_time = end_dt.strftime("%I:%M %p").lstrip('0')
        
        # If same day, show time range
        if start_dt.date() == end_dt.date():
            return f"{start_time} - {end_time}"
        else:
            return start_time
    
    def get_current_event(self):
        """
        Get the currently active event
        Returns event dict or None
        """
        now = datetime.now(self.timezone)
        
        for event in self.events:
            if event['start_datetime'] <= now <= event['end_datetime']:
                return event
        
        return None
    
    def get_next_event(self):
        """
        Get the next upcoming event
        Returns event dict or None
        """
        now = datetime.now(self.timezone)
        
        for event in self.events:
            if event['start_datetime'] > now:
                return event
        
        return None
    
    def get_events_needing_notification(self, warning_minutes=10):
        """
        Get events that need notifications (10 min warning or starting now)
        Returns list of (event, notification_type) tuples
        """
        now = datetime.now(self.timezone)
        notifications = []
        
        for event in self.events:
            # Skip past events
            if event['status'] == 'past':
                continue
            
            # Check for start notification (event starting now, within 1 minute)
            time_to_start = (event['start_datetime'] - now).total_seconds()
            if 0 <= time_to_start <= 60:  # Starting within next minute
                notifications.append((event, 'start'))
            
            # Check for warning notification (10 minutes before)
            elif (warning_minutes * 60 - 60) <= time_to_start <= (warning_minutes * 60 + 60):
                notifications.append((event, 'warning'))
        
        return notifications
    
    def refresh_events(self):
        """
        Refresh events from Google Calendar
        Returns True if successful, False otherwise
        """
        try:
            self.get_today_events()
            return True
        except Exception as error:
            print(f"Error refreshing events: {error}")
            return False
    
    def get_time_until_next_event(self):
        """
        Get time until next event in minutes
        Returns minutes as integer or None if no upcoming events
        """
        next_event = self.get_next_event()
        if not next_event:
            return None
        
        now = datetime.now(self.timezone)
        time_diff = next_event['start_datetime'] - now
        return int(time_diff.total_seconds() / 60)


if __name__ == "__main__":
    # Test the calendar service
    service = CalendarService()
    events = service.get_today_events()
    
    print(f"\n=== Today's Events ({len(events)}) ===")
    for event in events:
        status_icon = {
            'past': '✓',
            'current': '▶',
            'upcoming': ' '
        }.get(event['status'], ' ')
        
        print(f"{status_icon} {event['formatted_time']} - {event['title']}")
        if event['location']:
            print(f"   📍 {event['location']}")
    
    current = service.get_current_event()
    if current:
        print(f"\n🔴 Current Event: {current['title']}")
    
    next_event = service.get_next_event()
    if next_event:
        minutes = service.get_time_until_next_event()
        print(f"\n⏰ Next Event: {next_event['title']} (in {minutes} minutes)")
