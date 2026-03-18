from PyQt6.QtCore import QObject, pyqtSignal
from aurora_theme import AURORA_THEME
from mechanical_theme import MECHANICAL_THEME
from colors import COLORS as CATPPUCCIN_THEME

class ThemeManager(QObject):
    theme_changed = pyqtSignal(str)
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            # We need to initialize QObject properly
            QObject.__init__(cls._instance)
            cls._instance.current_theme_name = "mechanical"
            cls._instance.themes = {
                "catppuccin": CATPPUCCIN_THEME,
                "aurora": AURORA_THEME,
                "mechanical": MECHANICAL_THEME
            }
        return cls._instance
    
    def get_theme(self):
        return self.themes.get(self.current_theme_name, AURORA_THEME)
    
    def set_theme(self, name):
        if name in self.themes and name != self.current_theme_name:
            self.current_theme_name = name
            self.theme_changed.emit(name)
            
theme_manager = ThemeManager()
