import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QFrame, QScrollArea, QHeaderView, QProgressBar,
    QPushButton, QFileDialog
)
from PyQt6.QtGui import QPixmap, QPalette, QColor, QFont, QPainter
from PyQt6.QtCore import Qt

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

class StatsWindow(QWidget):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Статистика перекладу")
        self.resize(1200, 400)

        # Прокрутка
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setSpacing(1)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        for game in data:
            # Головний контейнер для гри
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
            
            # Іконка гри зліва
            icon_label = QLabel()
            icon_label.setFixedSize(200, 150)
            if game.get("icon") and os.path.exists(game["icon"]):
                pixmap = QPixmap(game["icon"])
                pixmap = pixmap.scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("background-color: #1e1e1e; border-right: 1px solid #3e3e42;")
            
            game_layout.addWidget(icon_label)
            
            # Права частина - заголовок + таблиця
            right_widget = QWidget()
            right_layout = QVBoxLayout(right_widget)
            right_layout.setContentsMargins(0, 0, 0, 0)
            right_layout.setSpacing(0)
            
            # Заголовок з назвою гри
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
            
            # Таблиця
            table = QTableWidget()
            sections = game.get("sections", [])
            
            if sections:
                # 4 рядки: назви секцій, підзаголовки, кількості, прогрес-бари
                table.setRowCount(4)
                table.setColumnCount(len(sections) * 2)
                
                # Створюємо заголовки та об'єднуємо комірки для назв секцій
                for i, section in enumerate(sections):
                    col_start = i * 2
                    
                    # Назва секції (об'єднана комірка)
                    section_item = QTableWidgetItem(section["name"])
                    section_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    section_item.setBackground(QColor(60, 60, 60))
                    section_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
                    table.setItem(0, col_start, section_item)
                    table.setSpan(0, col_start, 1, 2)  # Об'єднуємо 2 колонки
                    
                    # Перевіряємо, чи секція озвучки
                    if section.get("voice", "N").upper() == "Y":
                        first_label = "Озвучено"
                    else:
                        first_label = "Перекладено"

                    # Підзаголовки
                    translated_header = QTableWidgetItem(first_label)
                    translated_header.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    translated_header.setBackground(QColor(80, 80, 80))
                    table.setItem(1, col_start, translated_header)
                                        
                    approved_header = QTableWidgetItem("Затверджено")
                    approved_header.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    approved_header.setBackground(QColor(80, 80, 80))
                    table.setItem(1, col_start + 1, approved_header)
                
                # Заповнюємо дані
                for i, section in enumerate(sections):
                    col_start = i * 2
                    total = section["total"]
                    translated = section["translated"]
                    approved = section["approved"]
                    
                    # Кількості (рядок 2)
                    translated_count = QTableWidgetItem(f"{translated}/{total}")
                    translated_count.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.setItem(2, col_start, translated_count)
                    
                    approved_count = QTableWidgetItem(f"{approved}/{total}")
                    approved_count.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.setItem(2, col_start + 1, approved_count)
                    
                    # Прогрес-бари для кожної секції (рядки 3 і 4)
                    translated_percent = int(translated / total * 100) if total > 0 else 0
                    approved_percent = int(approved / total * 100) if total > 0 else 0
                    
                    # Прогрес-бар для перекладу цієї секції
                    translated_progress = QProgressBar()
                    translated_progress.setValue(translated_percent)
                    translated_progress.setFormat(f"{translated_percent}%")
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
                    
                    # Прогрес-бар для перевірки цієї секції  
                    approved_progress = QProgressBar()
                    approved_progress.setValue(approved_percent)
                    approved_progress.setFormat(f"{approved_percent}%")
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
                
                # Загальні відсотки - додаємо прогрес-бари під таблицею
                total_sum = sum(section["total"] for section in sections)
                translated_sum = sum(section["translated"] for section in sections)
                approved_sum = sum(section["approved"] for section in sections)
                
                overall_translated_percent = int(translated_sum / total_sum * 100) if total_sum > 0 else 0
                overall_approved_percent = int(approved_sum / total_sum * 100) if total_sum > 0 else 0
                
                # Налаштування таблиці
                table.setFixedHeight(120)  # Компактна висота
                table.horizontalHeader().setVisible(False)  # Ховаємо заголовки колонок
                table.verticalHeader().setVisible(False)
                table.setShowGrid(True)
                
                # Встановлюємо висоту рядків
                table.setRowHeight(0, 25)  # Назви секцій
                table.setRowHeight(1, 20)  # Підзаголовки
                table.setRowHeight(2, 20)  # Кількості
                table.setRowHeight(3, 25)  # Прогрес-бари
                
                # Автоматичне розтягування колонок
                header = table.horizontalHeader()
                for i in range(table.columnCount()):
                    header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
                
                # Стиль таблиці
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
                
                right_layout.addWidget(table)
                
                # Додаємо прогрес-бари для загального прогресу
                progress_container = QWidget()
                progress_layout = QVBoxLayout(progress_container)
                progress_layout.setContentsMargins(5, 2, 5, 2)
                progress_layout.setSpacing(2)
                
                # Прогрес-бар перекладу
                translated_progress = QProgressBar()
                translated_progress.setValue(overall_translated_percent)
                translated_progress.setFormat(f"Перекладено: {overall_translated_percent}%")
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
                
                # Прогрес-бар перевірки
                approved_progress = QProgressBar()
                approved_progress.setValue(overall_approved_percent)
                approved_progress.setFormat(f"Затверджено: {overall_approved_percent}%")
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
                
                right_layout.addWidget(progress_container)
            
            game_layout.addWidget(right_widget)
            main_layout.addWidget(game_frame)
        
        scroll.setWidget(scroll_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)
        self.setLayout(layout)

        # --- Кнопка для експорту ---


        export_btn = QPushButton("Експортувати як зображення")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1490df;
            }
        """)

        def export_as_image():
            widget = scroll.widget()
            widget.adjustSize()

            # Масштаб — у скільки разів збільшити чіткість
            scale_factor = 2  

            # Створюємо велике зображення
            orig_size = widget.size()
            scaled_size = orig_size * scale_factor

            # Рендеримо вручну в більший QPixmap
            pixmap = QPixmap(scaled_size)
            pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(pixmap)
            painter.scale(scale_factor, scale_factor)
            widget.render(painter)
            painter.end()

            # Збереження у файл
            save_path, _ = QFileDialog.getSaveFileName(self, "Зберегти зображення", "statystyka.png", "PNG files (*.png)")
            if save_path:
                pixmap.save(save_path, "PNG")
                print(f"✅ Збережено: {save_path}")


        export_btn.clicked.connect(export_as_image)

        # Додаємо кнопку під усе вікно
        layout.addWidget(export_btn)


def apply_dark_theme(app):
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 48))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(37, 37, 38))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 48))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, Qt.GlobalColor.gray)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, Qt.GlobalColor.gray)

    app.setPalette(dark_palette)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_dark_theme(app)

    data = load_data()
    window = StatsWindow(data)
    window.show()

    sys.exit(app.exec())