"""
Mechanical Sci-Fi Theme definition
Matches index.html styling
"""

MECHANICAL_THEME = {
    'background': '#0a0e1a',      # Deep Space Navy
    'surface': '#111827',         # Dark Industrial Surface
    'overlay': '#1f2937',         # Lighter Industrial Overlay
    'mantle': '#030712',          # Void
    
    # Text colors
    'text': '#ffffff',            # Pure white
    'subtext': '#94a3b8',         # Cool grey
    'subtext_dim': '#64748b',      # Dimmest grey
    
    # Accent colors (High contrast from index.html)
    'accent': '#00f0ff',          # Cyber Cyan (Translated)
    'success': '#00ffaa',         # Plasma Green (Approved)
    'warning': '#fbbf24',         # Amber alert
    'error': '#f43f5e',           # Laser red
    'info': '#8b5cf6',            # Neon purple
    
    # UI elements
    'border': '#1e293b',          # Industrial Border
    'hover': '#111827',           
    'pressed': '#1f2937',         
    
    # Progress (Gradient Bases)
    'progress_translated': '#00f0ff',
    'progress_approved': '#00ffaa',
    
    # Special: Frozen effect
    'frozen_accent': '#7dd3fc',   # Frost blue
    'frozen_surface': 'rgba(12, 74, 110, 0.3)', # Deep sea frost
    
    # Gradients (Linear & Sharp)
    'gradient_translated': 'qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 #0066cc, stop:1 #00f0ff)',
    'gradient_approved': 'qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 #009944, stop:1 #00ffaa)',
    'gradient_card': 'qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #111827, stop:1 #0a0e1a)',
    'gradient_hover': 'qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1f2937, stop:1 #111827)',
}
