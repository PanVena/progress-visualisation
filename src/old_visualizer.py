"""
Legacy visualization widget for displaying translation progress
Original design from main_old.py
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QFrame, QScrollArea, QHeaderView, QProgressBar,
    QPushButton, QFileDialog
)
from PyQt6.QtGui import QPixmap, QColor, QFont, QPainter
from PyQt6.QtCore import Qt

from data_manager import DataManager


class OldVisualizerWidget(QWidget):
    """Widget for visualizing translation progress using legacy design"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager = DataManager()
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the UI"""
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for projects
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #2d2d30;
            }
            QScrollBar:vertical {
                border: none;
                background: #3c3c3c;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: #2d2d30;")
        self.main_layout = QVBoxLayout(self.scroll_widget)
        self.main_layout.setSpacing(1)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll)
        
        # Export button
        export_btn = QPushButton("Експортувати як зображення")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1490df;
            }
        """)
        export_btn.clicked.connect(self.export_as_image)
        layout.addWidget(export_btn)
        
        self.setLayout(layout)
    
    def refresh(self):
        """Refresh the visualization with current data"""
        # Clear existing widgets
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Load data
        data = self.data_manager.load_data()
        
        # Add date label
        today_str = datetime.now().strftime("%d.%m.%Y")
        date_label = QLabel(f"Станом на {today_str}")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_label.setStyleSheet("""
            QLabel {
                background-color: #3c3c3c;
                color: white;
                font-weight: bold;
                font-size: 12px;
                padding: 4px;
            }
        """)
        self.main_layout.addWidget(date_label)
        
        # Add projects
        for game in data:
            if game.get('is_released'):
                continue
            game_frame = self.create_game_frame(game)
            self.main_layout.addWidget(game_frame)
    
    def create_game_frame(self, game: dict) -> QFrame:
        """Create a frame for a single game"""
        game_frame = QFrame()
        game_frame.setFrameStyle(QFrame.Shape.Box)
        game_frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d30;
                border: 1px solid #3e3e42;
            }
        """)
        
        game_layout = QHBoxLayout(game_frame)
        game_layout.setContentsMargins(0, 0, 0, 0)
        game_layout.setSpacing(0)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(200, 150)
        if game.get("icon") and os.path.exists(game["icon"]):
            pixmap = QPixmap(game["icon"])
            pixmap = pixmap.scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background-color: #1e1e1e; border-right: 1px solid #3e3e42;")
        game_layout.addWidget(icon_label)
        
        # Right side - title + table
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Title
        title_label = QLabel(game['game'])
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background-color: #3c3c3c;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 8px;
                border-bottom: 1px solid #3e3e42;
            }
        """)
        right_layout.addWidget(title_label)
        
        # Table
        sections = game.get("sections", [])
        if sections:
            table = self.create_sections_table(sections)
            right_layout.addWidget(table)
            
            # Overall progress bars
            progress_container = self.create_overall_progress(sections)
            right_layout.addWidget(progress_container)
        
        game_layout.addWidget(right_widget)
        return game_frame
    
    def create_sections_table(self, sections: list) -> QTableWidget:
        """Create table for sections"""
        table = QTableWidget()
        table.setRowCount(4)
        table.setColumnCount(len(sections) * 2)
        
        # Create headers and merge cells for section names
        for i, section in enumerate(sections):
            col_start = i * 2
            
            # Section name (merged cell)
            section_item = QTableWidgetItem(section["name"])
            section_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            section_item.setBackground(QColor(60, 60, 60))
            section_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            table.setItem(0, col_start, section_item)
            table.setSpan(0, col_start, 1, 2)
            
            # Subheaders
            translated_label = section.get("translated_label", "Перекладено")
            approved_label = section.get("approved_label", "Затверджено")
            
            translated_header = QTableWidgetItem(translated_label)
            translated_header.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            translated_header.setBackground(QColor(80, 80, 80))
            table.setItem(1, col_start, translated_header)
            
            approved_header = QTableWidgetItem(approved_label)
            approved_header.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            approved_header.setBackground(QColor(80, 80, 80))
            table.setItem(1, col_start + 1, approved_header)
        
        # Fill data
        for i, section in enumerate(sections):
            col_start = i * 2
            total = section["total"]
            translated = section["translated"]
            approved = section["approved"]
            
            # Counts (row 2)
            translated_count = QTableWidgetItem(f"{translated}/{total}")
            translated_count.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(2, col_start, translated_count)
            
            approved_count = QTableWidgetItem(f"{approved}/{total}")
            approved_count.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(2, col_start + 1, approved_count)
            
            # Progress bars (row 3)
            translated_percent = round(translated / total * 100, 2) if total > 0 else 0
            approved_percent = round(approved / total * 100, 2) if total > 0 else 0
            
            translated_progress = QProgressBar()
            translated_progress.setValue(int(translated_percent))
            translated_progress.setFormat(f"{translated_percent:.2f}%")
            translated_progress.setFixedHeight(18)
            translated_progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #3e3e42;
                    border-radius: 2px;
                    background-color: #2d2d30;
                    text-align: center;
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                }
                QProgressBar::chunk {
                    background-color: #0078d4;
                    border-radius: 1px;
                }
            """)
            table.setCellWidget(3, col_start, translated_progress)
            
            approved_progress = QProgressBar()
            approved_progress.setValue(int(approved_percent))
            approved_progress.setFormat(f"{approved_percent:.2f}%")
            approved_progress.setFixedHeight(18)
            approved_progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #3e3e42;
                    border-radius: 2px;
                    background-color: #2d2d30;
                    text-align: center;
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                }
                QProgressBar::chunk {
                    background-color: #28a745;
                    border-radius: 1px;
                }
            """)
            table.setCellWidget(3, col_start + 1, approved_progress)
        
        # Table settings
        table.setFixedHeight(120)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(True)
        
        table.setRowHeight(0, 25)
        table.setRowHeight(1, 20)
        table.setRowHeight(2, 20)
        table.setRowHeight(3, 25)
        
        header = table.horizontalHeader()
        for i in range(table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #3e3e42;
                background-color: #2d2d30;
                color: white;
                border: none;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #3c3c3c;
                color: white;
                padding: 5px;
                border: 1px solid #3e3e42;
                font-weight: bold;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 5px;
                border: 1px solid #3e3e42;
            }
        """)
        
        return table
    
    def create_overall_progress(self, sections: list) -> QWidget:
        """Create overall progress bars"""
        included_sections = [s for s in sections if not s.get("exclude_from_total", False)]
        
        total_sum = sum(s["total"] for s in included_sections)
        translated_sum = sum(s["translated"] for s in included_sections)
        approved_sum = sum(s["approved"] for s in included_sections)
        
        overall_translated_percent = round(translated_sum / total_sum * 100, 2) if total_sum > 0 else 0
        overall_approved_percent = round(approved_sum / total_sum * 100, 2) if total_sum > 0 else 0
        
        words_info_trans = f" ({translated_sum}/{total_sum} слів)" if total_sum > 0 else ""
        words_info_appr = f" ({approved_sum}/{total_sum} слів)" if total_sum > 0 else ""
        
        progress_container = QWidget()
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.setContentsMargins(5, 2, 5, 2)
        progress_layout.setSpacing(2)
        
        # Translated progress
        translated_progress = QProgressBar()
        translated_progress.setValue(int(overall_translated_percent))
        translated_progress.setFormat(f"Перекладено: {overall_translated_percent:.2f}% {words_info_trans}")
        translated_progress.setFixedHeight(20)
        translated_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 3px;
                background-color: #2d2d30;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
        """)
        
        # Approved progress
        approved_progress = QProgressBar()
        approved_progress.setValue(int(overall_approved_percent))
        approved_progress.setFormat(f"Затверджено: {overall_approved_percent:.2f}% {words_info_appr}")
        approved_progress.setFixedHeight(20)
        approved_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 3px;
                background-color: #2d2d30;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 2px;
            }
        """)
        
        progress_layout.addWidget(translated_progress)
        progress_layout.addWidget(approved_progress)
        
        return progress_container
    
    def export_as_image(self):
        """Export visualization as PNG image"""
        widget = self.scroll.widget()
        widget.adjustSize()
        
        # Scale factor for better quality
        scale_factor = 2
        
        # Create large image
        orig_size = widget.size()
        scaled_size = orig_size * scale_factor
        
        # Render to QPixmap
        pixmap = QPixmap(scaled_size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.scale(scale_factor, scale_factor)
        widget.render(painter)
        painter.end()
        
        # Save to file
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Зберегти зображення", "statystyka.png", "PNG files (*.png)"
        )
        if save_path:
            pixmap.save(save_path, "PNG")
            print(f"✅ Збережено: {save_path}")
