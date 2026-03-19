"""
Released Projects Editor for Progress Visualizer
A specialized tool for managing finished project entries.
"""

import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QSplitter,
    QListWidget, QFrame, QFileDialog, QPlainTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon

from data_manager import DataManager, ValidationError
from theme_manager import theme_manager

COLORS = theme_manager.get_theme()

class ReleasedEditorWidget(QWidget):
    """Editor for released projects"""
    
    data_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager = DataManager()
        self.released_projects = []
        self.current_project_index = -1
        self.init_ui()
        self.load_released_projects()
        
        theme_manager.theme_changed.connect(self.on_theme_changed)

    def on_theme_changed(self, theme_name):
        global COLORS
        COLORS = theme_manager.get_theme()
        self.apply_theme_styles()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel (List)
        left_panel = self.create_list_panel()
        splitter.addWidget(left_panel)
        
        # Right Panel (Form)
        right_panel = self.create_form_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([250, 750])
        layout.addWidget(splitter)
        self.setLayout(layout)
        self.apply_theme_styles()

    def create_list_panel(self):
        panel = QFrame()
        layout = QVBoxLayout(panel)
        
        header = QLabel("РЕЛІЗНУТІ ПРОЄКТИ")
        header.setStyleSheet("font-weight: 800; font-size: 14px; letter-spacing: 1px;")
        layout.addWidget(header)
        
        self.project_list = QListWidget()
        self.project_list.currentRowChanged.connect(self.on_selection_changed)
        layout.addWidget(self.project_list)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Додати")
        self.add_btn.clicked.connect(self.add_new_project)
        self.del_btn = QPushButton("Вилучити")
        self.del_btn.clicked.connect(self.delete_project)
        
        self.up_btn = QPushButton("↑")
        self.up_btn.setFixedWidth(40)
        self.up_btn.clicked.connect(self.move_project_up)
        self.down_btn = QPushButton("↓")
        self.down_btn.setFixedWidth(40)
        self.down_btn.clicked.connect(self.move_project_down)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addWidget(self.up_btn)
        btn_layout.addWidget(self.down_btn)
        layout.addLayout(btn_layout)
        
        return panel

    def create_form_panel(self):
        panel = QFrame()
        self.form_layout = QVBoxLayout(panel)
        self.form_layout.setContentsMargins(30, 20, 30, 20)
        
        # Title
        self.form_layout.addWidget(QLabel("НАЗВА ГРИ / ПРОЄКТУ"))
        self.title_input = QLineEdit()
        self.form_layout.addWidget(self.title_input)

        # Icon Section
        self.form_layout.addWidget(QLabel("ЛОГОТИП ПРОЄКТУ"))
        icon_row = QHBoxLayout()
        self.icon_preview = QLabel("📷")
        self.icon_preview.setFixedSize(64, 64)
        self.icon_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_preview.setStyleSheet(f"border: 1px solid {COLORS['border']}; border-radius: 8px; background: {COLORS['overlay']};")
        
        icon_info = QVBoxLayout()
        self.icon_path_display = QLineEdit()
        self.icon_path_display.setPlaceholderText("Шлях не вибрано")
        self.icon_path_display.setReadOnly(True)
        
        self.pick_icon_btn = QPushButton("Вибрати логотип")
        self.pick_icon_btn.clicked.connect(self.pick_icon)
        
        icon_info.addWidget(self.icon_path_display)
        icon_info.addWidget(self.pick_icon_btn)
        
        icon_row.addWidget(self.icon_preview)
        icon_row.addLayout(icon_info)
        self.form_layout.addLayout(icon_row)

        # Header Section
        self.form_layout.addWidget(QLabel("ГЕДЕР ПРОЄКТУ (Wide Banner)"))
        header_row = QVBoxLayout()
        self.header_preview = QLabel("🖼️")
        self.header_preview.setFixedSize(400, 100)
        self.header_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_preview.setStyleSheet(f"border: 1px solid {COLORS['border']}; border-radius: 8px; background: {COLORS['overlay']};")
        
        header_ctrls = QHBoxLayout()
        self.header_path_display = QLineEdit()
        self.header_path_display.setPlaceholderText("Шлях до гедера не вибрано")
        self.header_path_display.setReadOnly(True)
        
        self.pick_header_btn = QPushButton("Вибрати гедер")
        self.pick_header_btn.clicked.connect(self.pick_header)
        
        header_ctrls.addWidget(self.header_path_display)
        header_ctrls.addWidget(self.pick_header_btn)
        
        header_row.addWidget(self.header_preview)
        header_row.addLayout(header_ctrls)
        self.form_layout.addLayout(header_row)
        
        # Status
        self.status_input = QLineEdit()
        self.form_layout.addWidget(self.status_input)
        
        # Authors
        self.form_layout.addWidget(QLabel("АВТОРИ ПЕРЕКЛАДУ"))
        self.coauthors_input = QLineEdit()
        self.coauthors_input.setPlaceholderText("Введіть імена співавторів...")
        self.form_layout.addWidget(self.coauthors_input)
        
        # Description
        self.form_layout.addWidget(QLabel("ОПИС ПРОЄКТУ (Детальна інформація)"))
        self.description_input = QPlainTextEdit()
        self.description_input.setPlaceholderText("Введіть опис гри...")
        self.description_input.setMaximumHeight(150)
        self.form_layout.addWidget(self.description_input)
        
        # Links Table
        self.form_layout.addWidget(QLabel("ПОСИЛАННЯ (Label, URL)"))
        self.links_table = QTableWidget(0, 2)
        self.links_table.setHorizontalHeaderLabels(["Назва", "URL (Посилання)"])
        self.links_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.links_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.form_layout.addWidget(self.links_table)
        
        link_btns = QHBoxLayout()
        add_link = QPushButton("+ Посилання")
        add_link.clicked.connect(self.add_link_row)
        del_link = QPushButton("- Посилання")
        del_link.clicked.connect(self.del_link_row)
        
        self.link_up_btn = QPushButton("↑")
        self.link_up_btn.setFixedWidth(40)
        self.link_up_btn.clicked.connect(self.move_link_up)
        self.link_down_btn = QPushButton("↓")
        self.link_down_btn.setFixedWidth(40)
        self.link_down_btn.clicked.connect(self.move_link_down)
        
        link_btns.addWidget(add_link)
        link_btns.addWidget(del_link)
        link_btns.addWidget(self.link_up_btn)
        link_btns.addWidget(self.link_down_btn)
        link_btns.addStretch()
        self.form_layout.addLayout(link_btns)
        
        self.form_layout.addStretch()
        
        # Action Buttons
        actions = QHBoxLayout()
        self.save_btn = QPushButton("ЗБЕРЕГТИ ЗМІНИ")
        self.save_btn.setStyleSheet("font-weight: 800; padding: 10px;")
        self.save_btn.clicked.connect(self.save_current)
        actions.addStretch()
        actions.addWidget(self.save_btn)
        self.form_layout.addLayout(actions)
        
        return panel

    def apply_theme_styles(self):
        global COLORS
        COLORS = theme_manager.get_theme()
        accent_grad = COLORS.get('gradient_translated', COLORS.get('accent', '#06b6d4'))
        
        self.setStyleSheet(f"""
            QWidget {{ background-color: {COLORS['background']}; color: {COLORS['text']}; font-family: 'Outfit'; }}
            QLabel {{ color: {COLORS['subtext']}; font-size: 11px; font-weight: 700; margin-top: 10px; }}
            QLineEdit {{ background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 8px; color: {COLORS['text']}; }}
            QListWidget {{ background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; border-radius: 10px; padding: 5px; }}
            QListWidget::item {{ padding: 10px; border-radius: 6px; }}
            QListWidget::item:selected {{ background: {accent_grad}; color: {COLORS['background']}; font-weight: 800; }}
            QTableWidget {{ background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; border-radius: 8px; }}
            QPlainTextEdit {{ background-color: {COLORS['surface']}; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 8px; color: {COLORS['text']}; }}
            QPushButton {{ background-color: {COLORS['overlay']}; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 6px 12px; font-weight: 600; min-width: 80px; }}
            QPushButton:hover {{ background-color: {COLORS['hover']}; border-color: {COLORS['accent']}; }}
            #icon_preview {{ border: 1px solid {COLORS['border']}; border-radius: 8px; background: {COLORS['overlay']}; }}
        """)

    def pick_icon(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Вибрати логотип", "./icons", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            # Convert to relative path if within project
            cwd = os.getcwd()
            if file_path.startswith(cwd):
                file_path = "." + file_path[len(cwd):]
            
            self.icon_path_display.setText(file_path)
            self.update_icon_preview(file_path)

    def update_icon_preview(self, path):
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.icon_preview.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
                self.icon_preview.setText("")
                return
        self.icon_preview.setPixmap(QPixmap())
        self.icon_preview.setText("📷")

    def pick_header(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Вибрати гедер", "./icons/headers", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            cwd = os.getcwd()
            if file_path.startswith(cwd):
                file_path = "." + file_path[len(cwd):]
            
            self.header_path_display.setText(file_path)
            self.update_header_preview(file_path)

    def update_header_preview(self, path):
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.header_preview.setPixmap(pixmap.scaled(400, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                self.header_preview.setText("")
                return
        self.header_preview.setPixmap(QPixmap())
        self.header_preview.setText("🖼️")

    def load_released_projects(self):
        all_data = self.data_manager.load_data()
        self.released_projects = [p for p in all_data if p.get('is_released')]
        self.refresh_project_list()

    def refresh_project_list(self):
        self.project_list.clear()
        for p in self.released_projects:
            self.project_list.addItem(p.get('game', 'Без назви'))

    def on_selection_changed(self, index):
        if index < 0 or index >= len(self.released_projects):
            self.clear_form()
            return
        
        self.current_project_index = index
        project = self.released_projects[index]
        self.title_input.setText(project.get('game', ''))
        self.status_input.setText(project.get('status', ''))
        self.description_input.setPlainText(project.get('description', ''))
        self.coauthors_input.setText(project.get('coauthors', ''))
        
        icon_path = project.get('icon', '')
        self.icon_path_display.setText(icon_path)
        self.update_icon_preview(icon_path)
        
        header_path = project.get('header', '')
        self.header_path_display.setText(header_path)
        self.update_header_preview(header_path)
        
        links = project.get('links', [])
        self.links_table.setRowCount(len(links))
        for i, link in enumerate(links):
            self.links_table.setItem(i, 0, QTableWidgetItem(link.get('label', '')))
            self.links_table.setItem(i, 1, QTableWidgetItem(link.get('url', '')))

    def clear_form(self):
        self.title_input.clear()
        self.status_input.clear()
        self.description_input.clear()
        self.coauthors_input.clear()
        self.icon_path_display.clear()
        self.update_icon_preview("")
        self.header_path_display.clear()
        self.update_header_preview("")
        self.links_table.setRowCount(0)
        self.current_project_index = -1

    def add_link_row(self):
        self.links_table.insertRow(self.links_table.rowCount())

    def del_link_row(self):
        row = self.links_table.currentRow()
        if row >= 0:
            self.links_table.removeRow(row)

    def move_link_up(self):
        row = self.links_table.currentRow()
        if row > 0:
            self.swap_link_rows(row, row - 1)
            self.links_table.setCurrentCell(row - 1, self.links_table.currentColumn())

    def move_link_down(self):
        row = self.links_table.currentRow()
        if row >= 0 and row < self.links_table.rowCount() - 1:
            self.swap_link_rows(row, row + 1)
            self.links_table.setCurrentCell(row + 1, self.links_table.currentColumn())

    def swap_link_rows(self, row1, row2):
        for col in range(self.links_table.columnCount()):
            item1 = self.links_table.takeItem(row1, col)
            item2 = self.links_table.takeItem(row2, col)
            self.links_table.setItem(row1, col, item2)
            self.links_table.setItem(row2, col, item1)

    def move_project_up(self):
        idx = self.project_list.currentRow()
        if idx > 0:
            self.released_projects[idx], self.released_projects[idx-1] = \
                self.released_projects[idx-1], self.released_projects[idx]
            self.refresh_project_list()
            self.project_list.setCurrentRow(idx - 1)

    def move_project_down(self):
        idx = self.project_list.currentRow()
        if idx >= 0 and idx < len(self.released_projects) - 1:
            self.released_projects[idx], self.released_projects[idx+1] = \
                self.released_projects[idx+1], self.released_projects[idx]
            self.refresh_project_list()
            self.project_list.setCurrentRow(idx + 1)

    def add_new_project(self):
        new_p = {"game": "Новий проєкт", "is_released": True, "status": "Релізнуте", "links": [], "icon": ""}
        self.released_projects.append(new_p)
        self.project_list.addItem(new_p["game"])
        self.project_list.setCurrentRow(len(self.released_projects) - 1)

    def delete_project(self):
        idx = self.project_list.currentRow()
        if idx >= 0:
            res = QMessageBox.question(self, "Вилучення", f"Вилучити проєкт '{self.released_projects[idx].get('game')}'?")
            if res == QMessageBox.StandardButton.Yes:
                self.released_projects.pop(idx)
                if self.save_all_data():
                    self.load_released_projects()
                    self.clear_form()

    def save_all_data(self):
        """Save all data including current order of released projects"""
        all_data = self.data_manager.load_data()
        active_only = [p for p in all_data if not p.get('is_released')]
        final_data = active_only + self.released_projects
        
        try:
            self.data_manager.save_data(final_data)
            # Run index updater
            try:
                import update_index
                update_index.main()
            except Exception as updater_e:
                print(f"Помилка під час оновлення index.html: {updater_e}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти: {e}")
            return False

    def save_current(self):
        idx = self.current_project_index
        if idx < 0: return

        proj = self.released_projects[idx]
        proj["game"] = self.title_input.text()
        proj["status"] = self.status_input.text()
        proj["description"] = self.description_input.toPlainText()
        proj["coauthors"] = self.coauthors_input.text()
        proj["icon"] = self.icon_path_display.text()
        proj["header"] = self.header_path_display.text()
        
        links = []
        for i in range(self.links_table.rowCount()):
            label_item = self.links_table.item(i, 0)
            url_item = self.links_table.item(i, 1)
            label = label_item.text() if label_item else ""
            url = url_item.text() if url_item else ""
            if label or url:
                links.append({"label": label, "url": url})
        proj["links"] = links
        
        if self.save_all_data():
            self.load_released_projects()
            self.project_list.setCurrentRow(idx)
            self.data_changed.emit()
            QMessageBox.information(self, "Збережено", "Дані оновлено успішно!")
