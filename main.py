"""
Futuristic Google Calendar Display
Main application entry point for Raspberry Pi
"""

import os
import sys
import argparse
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from main_window import main as run_main_window
from services.google_auth import setup_credentials


def setup_mode():
    """Run setup mode for first-time configuration"""
    print("=" * 60)
    print("🚀 FUTURISTIC CALENDAR DISPLAY - SETUP MODE")
    print("=" * 60)
    print()
    
    print("This setup will help you configure Google Calendar access.")
    print("You'll need to:")
    print("1. Create a Google Cloud Project")
    print("2. Enable the Google Calendar API")
    print("3. Create OAuth 2.0 credentials")
    print("4. Download the credentials file")
    print()
    
    input("Press Enter to continue with setup instructions...")
    print()
    
    # Run the setup
    setup_credentials()


def test_mode():
    """Run test mode to verify configuration"""
    print("=" * 60)
    print("🧪 FUTURISTIC CALENDAR DISPLAY - TEST MODE")
    print("=" * 60)
    print()
    
    try:
        from services.google_auth import GoogleCalendarAuth
        from services.calendar_service import CalendarService
        
        print("Testing Google Calendar authentication...")
        auth = GoogleCalendarAuth()
        
        if auth.authenticate():
            print("✅ Authentication successful!")
            
            if auth.test_connection():
                print("✅ Connection test passed!")
                
                # Test calendar service
                print("\nTesting calendar service...")
                calendar_service = CalendarService()
                events = calendar_service.get_today_events()
                
                print(f"✅ Found {len(events)} events for today")
                
                if events:
                    print("\nToday's events:")
                    for i, event in enumerate(events[:3], 1):  # Show first 3
                        status_icon = {
                            'past': '✓',
                            'current': '▶',
                            'upcoming': '○'
                        }.get(event['status'], '○')
                        
                        print(f"  {i}. {status_icon} {event['formatted_time']} - {event['title']}")
                        if event.get('location'):
                            print(f"     📍 {event['location']}")
                    
                    if len(events) > 3:
                        print(f"     ... and {len(events) - 3} more events")
                
                print("\n✅ All tests passed! Ready to run the calendar display.")
                
            else:
                print("❌ Connection test failed!")
                return False
        else:
            print("❌ Authentication failed!")
            return False
            
    except Exception as error:
        print(f"❌ Test failed: {error}")
        return False
    
    return True


def display_mode():
    """Run the main calendar display"""
    print("=" * 60)
    print("🎯 STARTING FUTURISTIC CALENDAR DISPLAY")
    print("=" * 60)
    print()
    
    # Check if credentials exist
    if not os.path.exists('config/credentials.json'):
        print("❌ Google Calendar credentials not found!")
        print("Please run setup mode first: python main.py --setup")
        return
    
    # Run the main application
    try:
        run_main_window()
    except KeyboardInterrupt:
        print("\n👋 Calendar display stopped by user")
    except Exception as error:
        print(f"❌ Application error: {error}")
        print("Try running test mode: python main.py --test")


def main():
    """Main entry point with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Futuristic Google Calendar Display for Raspberry Pi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run the calendar display
  python main.py --setup            # First-time setup
  python main.py --test             # Test configuration
  python main.py --help             # Show this help

For Raspberry Pi autostart, add to ~/.bashrc or create a systemd service.
        """
    )
    
    parser.add_argument(
        '--setup', 
        action='store_true',
        help='Run first-time setup for Google Calendar authentication'
    )
    
    parser.add_argument(
        '--test', 
        action='store_true',
        help='Test Google Calendar connection and configuration'
    )
    
    parser.add_argument(
        '--version', 
        action='version',
        version='Futuristic Calendar Display v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Change to script directory
    os.chdir(current_dir)
    
    # Run appropriate mode
    if args.setup:
        setup_mode()
    elif args.test:
        test_mode()
    else:
        display_mode()


if __name__ == "__main__":
    main()
