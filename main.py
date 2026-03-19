#!/usr/bin/env python3
"""
Progress Visualizer - Modern GUI Application
Combines visualization and editing in a single modern interface
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPalette, QColor

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from visualizer import VisualizerWidget
from old_visualizer import OldVisualizerWidget
from editor import EditorWidget
from released_editor import ReleasedEditorWidget
from theme_manager import theme_manager

COLORS = theme_manager.get_theme()


class MainWindow(QMainWindow):
    """Main application window with modern design"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Візуалізатор поступу")
        self.visualizer = VisualizerWidget(self)
        self.old_visualizer = OldVisualizerWidget()
        self.editor = EditorWidget()
        self.released_editor = ReleasedEditorWidget()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Connect editor to visualizers
        self.editor.data_changed.connect(self.on_data_changed)
        self.released_editor.data_changed.connect(self.on_data_changed)
        
        # Initial window size based on project count
        # If we have few projects, we don't need a huge window
        project_count = len(self.editor.data_manager.data)
        if project_count < 3:
            self.resize(1400, 500)
        else:
            self.resize(1400, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create navigation bar
        nav_bar = self.create_nav_bar()
        layout.addWidget(nav_bar)
        
        # Create stacked widget for views
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.visualizer)
        self.stacked_widget.addWidget(self.old_visualizer)
        self.stacked_widget.addWidget(self.editor)
        self.stacked_widget.addWidget(self.released_editor)
        layout.addWidget(self.stacked_widget)
        
        # Apply custom styling
        self.apply_custom_style()
    
    def on_data_changed(self):
        """Handle data changes from editors and refresh visualizers."""
        self.visualizer.refresh()
        self.old_visualizer.refresh()

    def create_nav_bar(self) -> QWidget:
        """Create navigation bar"""
        self.nav_widget = QWidget()
        self.nav_widget.setFixedHeight(50)
        self.update_nav_bar_style()
        
        layout = QHBoxLayout(self.nav_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        layout.addStretch()
        
        # Mechanical Theme button (New Modern)
        mechanical_btn = QPushButton("Механічна💅")
        mechanical_btn.setCheckable(True)
        mechanical_btn.setChecked(theme_manager.current_theme_name == "mechanical")
        mechanical_btn.clicked.connect(self.switch_to_mechanical)
        layout.addWidget(mechanical_btn)
        
        # Classic Theme button (Catppuccin)
        classic_btn = QPushButton("Класична тема")
        classic_btn.setCheckable(True)
        classic_btn.setChecked(theme_manager.current_theme_name == "catppuccin")
        classic_btn.clicked.connect(lambda: self.switch_to_classic())
        layout.addWidget(classic_btn)
        
        # Old view button
        self.old_btn = QPushButton("Старий вигляд")
        self.old_btn.setCheckable(True)
        self.old_btn.clicked.connect(lambda: self.switch_view(1, self.old_btn))
        layout.addWidget(self.old_btn)
        
        # Edit button
        self.edit_btn = QPushButton("Редагувати")
        self.edit_btn.setCheckable(True)
        self.edit_btn.clicked.connect(lambda: self.switch_view(2, self.edit_btn))
        layout.addWidget(self.edit_btn)

        # Released Projects button
        self.released_btn = QPushButton("Релізи 📦")
        self.released_btn.setCheckable(True)
        self.released_btn.clicked.connect(lambda: self.switch_view(3, self.released_btn))
        layout.addWidget(self.released_btn)
        
        layout.addStretch()
        
        self.nav_buttons = [mechanical_btn, classic_btn, self.old_btn, self.edit_btn, self.released_btn]
        self.update_button_styles()
        
        return self.nav_widget
    
    def switch_to_mechanical(self):
        theme_manager.set_theme("mechanical")
        self.switch_view(0, self.nav_buttons[0])
        
    def switch_to_classic(self):
        theme_manager.set_theme("catppuccin")
        self.switch_view(0, self.nav_buttons[1])

    def update_nav_bar_style(self):
        self.nav_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['mantle']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)

    def update_button_styles(self):
        for btn in self.nav_buttons:
            btn.setStyleSheet(self.get_nav_button_style(btn.isChecked()))
    
    def get_nav_button_style(self, active: bool) -> str:
        """Get navigation button style"""
        if active:
            return f"""
                QPushButton {{
                    background-color: {COLORS['accent']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: #7aa4f0;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text']};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['hover']};
                }}
            """
    
    def switch_view(self, index: int, active_btn: QPushButton):
        """Switch between views"""
        for btn in self.nav_buttons:
            btn.setChecked(btn == active_btn)
        self.update_button_styles()
        
        self.stacked_widget.setCurrentIndex(index)
        
        # Special case: ensuring editors/visualizers reload data
        if index == 2:
            self.editor.load_projects()
        elif index == 3:
            self.released_editor.load_released_projects()
        elif index == 0:
            self.visualizer.refresh()
        elif index == 1:
            self.old_visualizer.refresh()
    
    def on_theme_changed(self, theme_name):
        """Handle global theme change"""
        global COLORS
        COLORS = theme_manager.get_theme()
        self.update_nav_bar_style()
        self.update_button_styles()
        self.apply_custom_style()
        # Re-apply global theme styles
        apply_global_theme(QApplication.instance())
    
    def apply_custom_style(self):
        """Apply custom Catppuccin Mocha colors"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
        """)


def apply_global_theme(app: QApplication):
    """Apply global dark theme to the application"""
    app.setStyle("Fusion")
    
    # Set global stylesheet for consistency
    app.setStyleSheet(f"""
        * {{
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }}
        
        QToolTip {{
            background-color: {COLORS['overlay']};
            color: {COLORS['text']};
            border: 1px solid {COLORS['border']};
            border-radius: 4px;
            padding: 4px;
        }}
        
        QMessageBox {{
            background-color: {COLORS['surface']};
            color: {COLORS['text']};
        }}
        
        QMessageBox QPushButton {{
            background-color: {COLORS['accent']};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 16px;
            min-width: 60px;
        }}
        
        QMessageBox QPushButton:hover {{
            background-color: {COLORS['hover']};
        }}
    """)


def main():
    """Main entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # Apply global theme
    apply_global_theme(app)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
