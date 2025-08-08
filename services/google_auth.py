"""
Google Calendar Authentication Service
Handles OAuth 2.0 authentication and token management
"""

import os
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import SCOPES, CREDENTIALS_FILE, TOKEN_FILE


class GoogleCalendarAuth:
    """Handles Google Calendar API authentication"""
    
    def __init__(self):
        self.credentials = None
        self.service = None
        
    def authenticate(self):
        """
        Authenticate with Google Calendar API
        Returns True if successful, False otherwise
        """
        try:
            # Load existing credentials if available
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # If there are no valid credentials, request authorization
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    # Refresh expired credentials
                    print("Refreshing expired credentials...")
                    self.credentials.refresh(Request())
                else:
                    # Run OAuth flow for new credentials
                    if not os.path.exists(CREDENTIALS_FILE):
                        print(f"Error: {CREDENTIALS_FILE} not found!")
                        print("Please download your OAuth 2.0 credentials from Google Cloud Console")
                        print("and save them as 'config/credentials.json'")
                        return False
                    
                    print("Starting OAuth flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, SCOPES)
                    self.credentials = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(self.credentials, token)
                    
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            print("Successfully authenticated with Google Calendar API")
            return True
            
        except FileNotFoundError as e:
            print(f"Credentials file not found: {e}")
            return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def get_service(self):
        """
        Get the authenticated Google Calendar service
        Returns the service object or None if not authenticated
        """
        if not self.service:
            if not self.authenticate():
                return None
        return self.service
    
    def test_connection(self):
        """
        Test the connection to Google Calendar API
        Returns True if successful, False otherwise
        """
        try:
            service = self.get_service()
            if not service:
                return False
                
            # Try to get calendar list to test connection
            calendars_result = service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            print(f"Successfully connected. Found {len(calendars)} calendars.")
            return True
            
        except HttpError as error:
            print(f"HTTP error occurred: {error}")
            return False
        except Exception as error:
            print(f"An error occurred: {error}")
            return False
    
    def get_calendar_list(self):
        """
        Get list of user's calendars
        Returns list of calendar objects or empty list if error
        """
        try:
            service = self.get_service()
            if not service:
                return []
                
            calendars_result = service.calendarList().list().execute()
            calendars = calendars_result.get('items', [])
            
            # Return simplified calendar info
            calendar_list = []
            for calendar in calendars:
                calendar_info = {
                    'id': calendar['id'],
                    'summary': calendar['summary'],
                    'primary': calendar.get('primary', False),
                    'backgroundColor': calendar.get('backgroundColor', '#ffffff')
                }
                calendar_list.append(calendar_info)
                
            return calendar_list
            
        except Exception as error:
            print(f"Error getting calendar list: {error}")
            return []


def setup_credentials():
    """
    Helper function to set up credentials for first-time use
    This should be run on a desktop/laptop with a browser
    """
    print("=== Google Calendar Setup ===")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable the Google Calendar API")
    print("4. Create OAuth 2.0 credentials (Desktop application)")
    print("5. Download the credentials JSON file")
    print("6. Save it as 'config/credentials.json'")
    print("7. Run this script again")
    print()
    
    if os.path.exists(CREDENTIALS_FILE):
        print("Credentials file found! Testing authentication...")
        auth = GoogleCalendarAuth()
        if auth.authenticate():
            print("✅ Authentication successful!")
            if auth.test_connection():
                print("✅ Connection test passed!")
                calendars = auth.get_calendar_list()
                print(f"✅ Found {len(calendars)} calendars:")
                for cal in calendars:
                    primary = " (PRIMARY)" if cal['primary'] else ""
                    print(f"  - {cal['summary']}{primary}")
            else:
                print("❌ Connection test failed!")
        else:
            print("❌ Authentication failed!")
    else:
        print(f"❌ Credentials file not found: {CREDENTIALS_FILE}")


if __name__ == "__main__":
    setup_credentials()
