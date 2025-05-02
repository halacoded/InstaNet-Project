"""
This module contains all the constants and configuration settings used across the Instagram Clone application.

The constants are organized into several categories:
- Color schemes for the UI
- Font configurations
- Socket and network settings
- File paths and data storage locations
- Default user configurations
- Message display settings
- UI layout and sizing configurations

These constants ensure consistency across the application and make it easy to modify
the application's appearance and behavior by changing values in a single location.
"""

# Color constants
INSTAGRAM_COLORS = {
    "background": "#fafafa",  # Main background color
    "card": "#ffffff",        # Color for card-like elements
    "primary": "#3897f0",     # Primary blue color for buttons and active elements
    "primary_hover": "#4cb5f9",  # Hover state for primary color
    "hover_gray": "#efefef",  # Gray color for hover states
    "text_main": "#262626",   # Main text color
    "text_subtle": "#8e8e8e"  # Secondary text color
}

# Font constants
FONT_BOLD = ("Helvetica", 14, "bold")      # Bold font for headings
FONT_REGULAR = ("Helvetica", 12)           # Regular font for normal text
FONT_SMALL = ("Helvetica", 10)             # Small font for secondary text

# Socket configuration
DEFAULT_HOST = 'localhost'     # Default host for socket connections
DEFAULT_PORT = 5000           # Default port for socket connections
MAX_RETRIES = 3               # Maximum number of connection retries
RETRY_DELAY = 2               # Delay between retries in seconds
BUFFER_SIZE = 4096            # Size of socket buffer for data transfer

# File paths
DATA_DIRECTORIES = [          # List of directories needed for data storage
    'data/users',            # User data and profiles
    'data/posts',            # Post data and images
    'data/messages',         # Message history
    'data/images'            # Image storage
]
USERS_FILE = 'data/users/users.json'    # Path to users data file
POSTS_FILE = 'data/posts/posts.json'    # Path to posts data file

# Default users configuration
DEFAULT_USERS_COUNT = 10      # Number of default users to create
DEFAULT_USER_PREFIX = "user"  # Prefix for default usernames
DEFAULT_PASS_PREFIX = "pass"  # Prefix for default passwords

# Message configuration
MESSAGE_BUBBLE_RADIUS = 16    # Corner radius for message bubbles
MESSAGE_WRAP_LENGTH = 220     # Maximum width for message text before wrapping
MESSAGE_PADDING = 8           # Horizontal padding for messages
MESSAGE_VERTICAL_PADDING = 4  # Vertical padding for messages

# UI configuration
WINDOW_TITLE = "InstaNet"     # Application window title
WINDOW_SIZE = "500x800"       # Default window size (width x height)
LOGIN_FRAME_SIZE = (340, 400) # Size of the login frame (width, height)
INPUT_FIELD_HEIGHT = 40       # Height of input fields
BUTTON_HEIGHT = 40            # Height of buttons
CORNER_RADIUS = 10            # Default corner radius for UI elements
PADDING = 20                  # Default padding for UI elements 