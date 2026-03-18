"""
Catppuccin Mocha color scheme for modern dark theme
https://github.com/catppuccin/catppuccin
"""

# Base colors
BACKGROUND = '#12121a'      # Main background (Darker)
SURFACE = '#1a1a24'         # Cards, elevated surfaces (Darker)
OVERLAY = '#242430'         # Overlays, hover states (Darker)
MANTLE = '#0a0a0f'          # Deeper background (Darker)

# Text colors
TEXT = '#cdd6f4'            # Primary text
SUBTEXT = '#a6adc8'         # Secondary text
SUBTEXT_DIM = '#9399b2'     # Tertiary text

# Accent colors
ACCENT = '#3b82f6'          # Blue - primary accent (Darker standard blue)
SUCCESS = '#22c55e'         # Green - success states (Darker standard green)
WARNING = '#f9e2af'         # Yellow - warnings
ERROR = '#f38ba8'           # Red - errors
INFO = '#74c7ec'            # Cyan - info

# Additional colors
LAVENDER = '#b4befe'        # Purple accent
PINK = '#f5c2e7'            # Pink accent
MAUVE = '#cba6f7'           # Mauve accent
PEACH = '#fab387'           # Orange accent

# UI element colors
BORDER = '#3e3e42'          # Borders
HOVER = '#45475a'           # Hover state
PRESSED = '#585b70'         # Pressed state

# Progress bar colors
PROGRESS_TRANSLATED = ACCENT    # Blue for translated
PROGRESS_APPROVED = SUCCESS     # Green for approved

# Color dictionary for easy access
COLORS = {
    'background': BACKGROUND,
    'surface': SURFACE,
    'overlay': OVERLAY,
    'mantle': MANTLE,
    'text': TEXT,
    'subtext': SUBTEXT,
    'subtext_dim': SUBTEXT_DIM,
    'accent': ACCENT,
    'success': SUCCESS,
    'warning': WARNING,
    'error': ERROR,
    'info': INFO,
    'lavender': LAVENDER,
    'pink': PINK,
    'mauve': MAUVE,
    'peach': PEACH,
    'border': BORDER,
    'hover': HOVER,
    'pressed': PRESSED,
    'progress_translated': PROGRESS_TRANSLATED,
    'progress_approved': PROGRESS_APPROVED,
}
