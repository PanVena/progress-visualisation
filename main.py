#!/usr/bin/env python3
"""
Progress Visualizer - Modern GUI Application
Combines visualization and editing in a single modern interface
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPalette, QColor

from visualizer import VisualizerWidget
from old_visualizer import OldVisualizerWidget
from editor import EditorWidget
from colors import COLORS


class MainWindow(QMainWindow):
    """Main application window with modern design"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Візуалізатор поступу")
        self.visualizer = VisualizerWidget(self)
        self.old_visualizer = OldVisualizerWidget(self)
        self.editor = EditorWidget(self)
        
        # Initial window size based on project count
        # If we have few projects, we don't need a huge window
        project_count = len(self.editor.data_manager.data)
        if project_count < 3:
            self.resize(1400, 500)
        else:
            self.resize(1400, 800)
        
        # Connect editor data changes to both visualizers refresh
        self.editor.data_changed.connect(self.visualizer.refresh)
        self.editor.data_changed.connect(self.old_visualizer.refresh)
        
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
        layout.addWidget(self.stacked_widget)
        
        # Apply custom styling
        self.apply_custom_style()
    
    def create_nav_bar(self) -> QWidget:
        """Create navigation bar"""
        nav_widget = QWidget()
        nav_widget.setFixedHeight(50)
        nav_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['mantle']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        
        layout = QHBoxLayout(nav_widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        layout.addStretch()
        
        # Modern view button
        modern_btn = QPushButton("Сучасніший вигляд")
        modern_btn.setCheckable(True)
        modern_btn.setChecked(True)
        modern_btn.clicked.connect(lambda: self.switch_view(0, modern_btn, old_btn, edit_btn))
        modern_btn.setStyleSheet(self.get_nav_button_style(True))
        layout.addWidget(modern_btn)
        
        # Old view button
        old_btn = QPushButton("Старий вигляд")
        old_btn.setCheckable(True)
        old_btn.clicked.connect(lambda: self.switch_view(1, old_btn, modern_btn, edit_btn))
        old_btn.setStyleSheet(self.get_nav_button_style(False))
        layout.addWidget(old_btn)
        
        # Edit button
        edit_btn = QPushButton("Редагування")
        edit_btn.setCheckable(True)
        edit_btn.clicked.connect(lambda: self.switch_view(2, edit_btn, modern_btn, old_btn))
        edit_btn.setStyleSheet(self.get_nav_button_style(False))
        layout.addWidget(edit_btn)
        
        layout.addStretch()
        
        self.modern_btn = modern_btn
        self.old_btn = old_btn
        self.edit_btn = edit_btn
        
        return nav_widget
    
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
    
    def switch_view(self, index: int, active_btn: QPushButton, inactive_btn1: QPushButton, inactive_btn2: QPushButton):
        """Switch between views"""
        self.stacked_widget.setCurrentIndex(index)
        active_btn.setStyleSheet(self.get_nav_button_style(True))
        inactive_btn1.setStyleSheet(self.get_nav_button_style(False))
        inactive_btn2.setStyleSheet(self.get_nav_button_style(False))
    
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
