"""
Futuristic UI Styles and Themes
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import THEME, FONTS


def get_main_window_style():
    """Get the main window stylesheet"""
    return f"""
    QMainWindow {{
        background-color: {THEME['background']};
        color: {THEME['text_primary']};
        border: none;
    }}
    """


def get_header_style():
    """Get the header section stylesheet"""
    return f"""
    QWidget#header {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                   stop:0 {THEME['background']},
                                   stop:1 rgba(0, 255, 255, 0.1));
        border-bottom: 2px solid {THEME['primary']};
        border-radius: 10px;
        margin: 5px;
        padding: 10px;
    }}
    
    QLabel#time_display {{
        color: {THEME['primary']};
        font-family: {FONTS['time_display'][0]};
        font-size: {FONTS['time_display'][1]}px;
        font-weight: {FONTS['time_display'][2]};
        text-align: center;
        background: transparent;
        border: none;
    }}
    
    QLabel#date_display {{
        color: {THEME['text_secondary']};
        font-family: {FONTS['date_display'][0]};
        font-size: {FONTS['date_display'][1]}px;
        font-weight: {FONTS['date_display'][2]};
        text-align: center;
        background: transparent;
        border: none;
    }}
    """


def get_event_list_style():
    """Get the event list stylesheet"""
    return f"""
    QScrollArea {{
        background-color: transparent;
        border: none;
        margin: 10px;
    }}
    
    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}
    
    QScrollBar:vertical {{
        background: rgba(255, 255, 255, 0.1);
        width: 8px;
        border-radius: 4px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background: {THEME['primary']};
        border-radius: 4px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {THEME['secondary']};
    }}
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    """


def get_event_widget_style(status='upcoming'):
    """Get event widget stylesheet based on status"""
    
    # Color mapping for different event statuses
    colors = {
        'past': THEME['past_event'],
        'current': THEME['current_event'],
        'upcoming': THEME['upcoming_event']
    }
    
    # Border effects for different statuses
    border_effects = {
        'past': f"border: 1px solid {THEME['past_event']};",
        'current': f"border: 2px solid {THEME['current_event']};",
        'upcoming': f"border: 1px solid rgba(255, 255, 255, 0.3);"
    }
    
    text_color = colors.get(status, THEME['text_primary'])
    border_effect = border_effects.get(status, "border: 1px solid rgba(255, 255, 255, 0.3);")
    
    return f"""
    QWidget#event_widget {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 rgba(0, 0, 0, 0.3),
                                   stop:1 rgba(255, 255, 255, 0.05));
        {border_effect}
        border-radius: 12px;
        margin: 8px 15px;
        padding: 15px 20px;
        min-height: 60px;
    }}
    
    QWidget#event_widget:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 rgba(0, 255, 255, 0.1),
                                   stop:1 rgba(255, 255, 255, 0.1));
    }}
    
    QLabel#event_time {{
        color: {text_color};
        font-family: {FONTS['event_time'][0]};
        font-size: {FONTS['event_time'][1]}px;
        font-weight: {FONTS['event_time'][2]};
        background: transparent;
        border: none;
        min-width: 100px;
    }}
    
    QLabel#event_title {{
        color: {text_color};
        font-family: {FONTS['event_title'][0]};
        font-size: {FONTS['event_title'][1]}px;
        font-weight: {FONTS['event_title'][2]};
        background: transparent;
        border: none;
    }}
    
    QLabel#status_indicator {{
        color: {text_color};
        font-size: 16px;
        background: transparent;
        border: none;
        min-width: 20px;
        max-width: 20px;
    }}
    """


def get_notification_style(notification_type='warning'):
    """Get notification overlay stylesheet"""
    
    # Color scheme based on notification type
    if notification_type == 'start':
        bg_color = THEME['error']
        border_color = THEME['error']
        glow_color = THEME['error']
    else:  # warning
        bg_color = THEME['warning']
        border_color = THEME['warning']
        glow_color = THEME['warning']
    
    return f"""
    QWidget#notification_overlay {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                   stop:0 rgba(0, 0, 0, 0.9),
                                   stop:0.5 rgba(255, 69, 0, 0.3),
                                   stop:1 rgba(0, 0, 0, 0.9));
        border: 3px solid {border_color};
        border-radius: 15px;
    }}
    
    QLabel#notification_title {{
        color: {border_color};
        font-family: {FONTS['notification_title'][0]};
        font-size: {FONTS['notification_title'][1]}px;
        font-weight: {FONTS['notification_title'][2]};
        text-align: center;
        background: transparent;
        border: none;
    }}
    
    QLabel#notification_subtitle {{
        color: {THEME['text_primary']};
        font-family: {FONTS['notification_text'][0]};
        font-size: {FONTS['notification_text'][1]}px;
        font-weight: bold;
        text-align: center;
        background: transparent;
        border: none;
        margin: 10px 0;
    }}
    
    QLabel#notification_message {{
        color: {THEME['text_secondary']};
        font-family: {FONTS['notification_text'][0]};
        font-size: 16px;
        text-align: center;
        background: transparent;
        border: none;
    }}
    
    QLabel#notification_time {{
        color: {border_color};
        font-family: {FONTS['notification_text'][0]};
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        background: transparent;
        border: none;
    }}
    
    QPushButton#dismiss_button {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 rgba(255, 255, 255, 0.1),
                                   stop:1 rgba(255, 255, 255, 0.2));
        border: 2px solid {THEME['primary']};
        border-radius: 8px;
        color: {THEME['primary']};
        font-family: {FONTS['notification_text'][0]};
        font-size: 14px;
        font-weight: bold;
        padding: 8px 16px;
        margin: 10px;
    }}
    
    QPushButton#dismiss_button:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 rgba(0, 255, 255, 0.2),
                                   stop:1 rgba(0, 255, 255, 0.3));
    }}
    
    QPushButton#dismiss_button:pressed {{
        background: rgba(0, 255, 255, 0.4);
    }}
    """


def get_time_indicator_style():
    """Get time progress indicator stylesheet"""
    return f"""
    QWidget#time_indicator {{
        background: transparent;
        border: none;
        margin: 5px 10px;
    }}
    
    QProgressBar {{
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 5px;
        text-align: center;
        height: 8px;
    }}
    
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 {THEME['primary']},
                                   stop:1 {THEME['secondary']});
        border-radius: 4px;
    }}
    
    QLabel#time_indicator_label {{
        color: {THEME['text_secondary']};
        font-family: {FONTS['event_time'][0]};
        font-size: 12px;
        text-align: center;
        background: transparent;
        border: none;
        margin: 2px 0;
    }}
    """


def get_no_events_style():
    """Get style for no events message"""
    return f"""
    QLabel#no_events {{
        color: {THEME['text_secondary']};
        font-family: {FONTS['event_title'][0]};
        font-size: 18px;
        text-align: center;
        background: transparent;
        border: 2px dashed rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        padding: 40px 20px;
        margin: 20px;
    }}
    """


def apply_futuristic_effects():
    """Additional CSS effects for futuristic look"""
    return """
    /* Global selection effects */
    * {
        selection-background-color: rgba(0, 255, 255, 0.3);
        selection-color: white;
    }
    
    /* Custom scrollbar styling */
    QScrollBar:vertical {
        background: rgba(255, 255, 255, 0.05);
        width: 6px;
        border-radius: 3px;
    }
    
    QScrollBar::handle:vertical {
        background: rgba(0, 255, 255, 0.7);
        border-radius: 3px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: rgba(0, 255, 255, 1.0);
    }
    """


def get_combined_stylesheet():
    """Get the complete combined stylesheet for the application"""
    return f"""
    {get_main_window_style()}
    {get_header_style()}
    {get_event_list_style()}
    {get_time_indicator_style()}
    {get_no_events_style()}
    {apply_futuristic_effects()}
    """


# Font loading helper
def load_custom_fonts():
    """Load custom fonts if available"""
    try:
        from PyQt5.QtGui import QFontDatabase
        
        font_db = QFontDatabase()
        
        # Try to load Orbitron font with absolute path
        orbitron_path = os.path.abspath("fonts/Orbitron-VariableFont_wght.ttf")
        
        if os.path.exists(orbitron_path):
            # Try loading with absolute path
            font_id = font_db.addApplicationFont(orbitron_path)
            
            if font_id != -1:
                font_families = font_db.applicationFontFamilies(font_id)
                
                if font_families:
                    actual_font_name = font_families[0]
                    print(f"✅ Loaded Orbitron font successfully as: '{actual_font_name}'")
                    # Update the settings to use the actual font name
                    update_font_settings(actual_font_name)
                    return
                else:
                    print("❌ Font loaded but no families returned")
            else:
                print("❌ Font loading failed - trying system Orbitron")
                # Try using system Orbitron if available
                available_families = font_db.families()
                if 'Orbitron' in available_families:
                    print("✅ Found system Orbitron font")
                    update_font_settings('Orbitron')
                    return
        
        print("ℹ️ Using system fonts (Helvetica Neue) for clean modern look")
            
    except Exception as e:
        print(f"ℹ️ Using system fonts: {e}")


def update_font_settings(orbitron_name):
    """Update font settings with the actual loaded font name"""
    from config.settings import FONTS
    
    # Update ALL font settings to use the actual loaded font name for full futuristic look
    FONTS['time_display'] = (orbitron_name, 48, 'bold')
    FONTS['date_display'] = (orbitron_name, 24, 'normal')
    FONTS['event_title'] = (orbitron_name, 20, 'bold')
    FONTS['event_time'] = (orbitron_name, 18, 'bold')
    FONTS['notification_title'] = (orbitron_name, 28, 'bold')
    FONTS['notification_text'] = (orbitron_name, 22, 'normal')
    
    print(f"✅ Updated ALL font settings to use: '{orbitron_name}' for full futuristic look")


if __name__ == "__main__":
    # Test stylesheet generation
    print("=== Main Window Style ===")
    print(get_main_window_style())
    
    print("\n=== Event Widget Style (Current) ===")
    print(get_event_widget_style('current'))
    
    print("\n=== Notification Style (Start) ===")
    print(get_notification_style('start'))
