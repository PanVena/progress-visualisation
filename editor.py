"""
Modern GUI Editor for Progress Visualizer
Uses native PyQt6 with custom styling
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QSpinBox, QCheckBox, QMessageBox, QSplitter,
    QListWidget, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QFont

from data_manager import DataManager, ValidationError
from theme_manager import theme_manager

COLORS = theme_manager.get_theme()


class EditorWidget(QWidget):
    """Main editor widget with Fluent Design"""
    
    data_changed = pyqtSignal()  # Signal when data is saved
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager = DataManager()
        self.current_project_index = -1
        self.init_ui()
        self.load_projects()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def on_theme_changed(self, theme_name):
        """Handle theme changes"""
        global COLORS
        COLORS = theme_manager.get_theme()
        self.apply_theme_styles()
    
    def apply_theme_styles(self):
        """Apply styles for the current theme"""
        # Main layout styles
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - project list
        left_panel = self.create_project_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - project editor
        right_panel = self.create_editor_panel()
        splitter.addWidget(right_panel)
        
        # Set initial sizes (30% left, 70% right)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
        self.apply_theme_styles()

    def apply_theme_styles(self):
        """Apply styles based on current theme - Unified Aurora Aesthetic"""
        global COLORS
        COLORS = theme_manager.get_theme()
        
        # Primary Gradient for "Fancy" buttons
        accent_grad = COLORS.get('gradient_translated', COLORS.get('accent', '#06b6d4'))
        error_grad = "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #f43f5e, stop:1 #fb7185)"
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
            QLabel {{
                color: {COLORS['text']};
                background: transparent;
                border: none;
            }}
            QLineEdit, QSpinBox {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 13px;
                color: {COLORS['text']};
                selection-background-color: {COLORS['accent']};
            }}
            /* Compact inputs inside the table */
            QTableWidget QLineEdit, QTableWidget QSpinBox {{
                font-size: 11px;
                padding: 2px 6px;
                border-radius: 4px;
                background-color: transparent;
                border: 1px solid transparent;
            }}
            QTableWidget QLineEdit:hover, QTableWidget QSpinBox:hover {{
                background-color: {COLORS['overlay']};
                border: 1px solid {COLORS['accent']};
            }}
            QTableWidget QLineEdit:focus, QTableWidget QSpinBox:focus {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['accent']};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0px;
                height: 0px;
                border: none;
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border: 1px solid {COLORS['accent']};
                background-color: {COLORS['overlay']};
            }}
            QListWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                outline: none;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 12px;
                border-radius: 8px;
                margin: 2px;
                color: {COLORS['subtext']};
            }}
            QListWidget::item:selected {{
                background: {accent_grad};
                color: {COLORS['background']};
                font-weight: bold;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLORS['hover']};
                color: {COLORS['text']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['overlay']};
                color: {COLORS['text']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['overlay']};
                color: {COLORS['accent']};
                padding: 10px;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                font-weight: bold;
                font-size: 10px;
                text-transform: uppercase;
            }}
            /* Checkbox Styling */
            QCheckBox {{
                spacing: 5px;
                color: {COLORS['text']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid {COLORS['accent']};
                background-color: {COLORS['overlay']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['accent']};
            }}
            /* ScrollBar Styling */
            QScrollBar:vertical {{
                background: {COLORS['mantle']};
                width: 12px;
                margin: 0px;
                border: none;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['overlay']};
                min-height: 30px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['accent']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background: {COLORS['mantle']};
                height: 12px;
                margin: 0px;
                border: none;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background: {COLORS['overlay']};
                min-width: 30px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {COLORS['accent']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            /* Buttons Styling */
            QPushButton {{
                background-color: {COLORS['overlay']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 13px;
            }}
            /* Small table buttons */
            QTableWidget QPushButton {{
                padding: 4px 8px;
                font-size: 11px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
                border: 1px solid {COLORS['accent']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['pressed']};
            }}
            /* Primary/Fancy Buttons */
            QPushButton#primary_btn {{
                background: {accent_grad};
                color: {COLORS['background']};
                border: none;
            }}
            QPushButton#primary_btn:hover {{
                opacity: 0.9;
                background-color: {COLORS.get('aurora_teal', COLORS['accent'])};
            }}
            /* Danger Buttons */
            QPushButton#danger_btn {{
                background-color: transparent;
                border: 1px solid {COLORS['error']};
                color: {COLORS['error']};
            }}
            QPushButton#danger_btn:hover {{
                background: {error_grad};
                color: white;
                border: none;
            }}
            /* Header Styling */
            QLabel#section_header {{
                color: {COLORS['text']};
                padding: 5px 0;
            }}
            /* Toolbar items */
            QFrame#info_card {{
                background-color: {COLORS['surface']};
                border-radius: 16px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        
        # We need to re-apply styles to specific elements if they have custom style sheets
        # If we had references, we'd update them here. 
        # For simplicity, we can let init_ui handle most of it or refresh the whole widget.
        # But setStyleSheet on self should propagate down unless overwritten.
    
    def create_project_list_panel(self) -> QWidget:
        """Create left panel with project list"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Проєкти")
        title.setObjectName("section_header")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Project list
        self.project_list = QListWidget()
        self.project_list.currentRowChanged.connect(self.on_project_selected)
        layout.addWidget(self.project_list)
        
        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)
        
        add_btn = QPushButton("Додати проєкт")
        add_btn.setObjectName("primary_btn")
        add_btn.clicked.connect(self.add_project)
        btn_layout.addWidget(add_btn)
        
        delete_btn = QPushButton("Видалити проєкт")
        delete_btn.setObjectName("danger_btn")
        delete_btn.clicked.connect(self.delete_project)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        # Move buttons
        move_layout = QHBoxLayout()
        move_layout.setSpacing(8)
        
        move_up_btn = QPushButton("↑")
        move_up_btn.setToolTip("Перемістити вгору")
        move_up_btn.clicked.connect(self.move_project_up)
        move_layout.addWidget(move_up_btn)
        
        move_down_btn = QPushButton("↓")
        move_down_btn.setToolTip("Перемістити вниз")
        move_down_btn.clicked.connect(self.move_project_down)
        move_layout.addWidget(move_down_btn)
        
        layout.addLayout(move_layout)
        
        return panel
    
    def create_editor_panel(self) -> QWidget:
        """Create right panel with project editor"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        self.editor_title = QLabel("Виберіть проєкт для редагування")
        self.editor_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(self.editor_title)
        
        # Game info card
        info_card = QFrame()
        info_card.setObjectName("info_card")
        info_layout = QVBoxLayout(info_card)
        
        # Game name
        name_layout = QHBoxLayout()
        name_label = QLabel("Назва гри:")
        name_label.setFixedWidth(100)
        self.game_name_input = QLineEdit()
        self.game_name_input.setPlaceholderText("Введіть назву гри...")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.game_name_input)
        info_layout.addLayout(name_layout)
        
        # Icon picker
        icon_layout = QHBoxLayout()
        icon_label = QLabel("Іконка:")
        icon_label.setFixedWidth(100)
        self.icon_path_label = QLabel("Не вибрано")
        self.icon_path_label.setStyleSheet(f"color: {COLORS['subtext']};")
        icon_btn = QPushButton("Вибрати іконку")
        icon_btn.clicked.connect(self.pick_icon)
        icon_layout.addWidget(self.icon_path_label, 1)
        icon_layout.addWidget(icon_btn)
        info_layout.addLayout(icon_layout)
        
        # Unit selection
        unit_layout = QHBoxLayout()
        unit_label = QLabel("Одиниці виміру:")
        unit_label.setFixedWidth(100)
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["слів", "рядків", "файлів"])
        self.unit_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 4px 10px;
                color: {COLORS['text']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
        """)
        unit_layout.addWidget(unit_label)
        unit_layout.addWidget(self.unit_combo)
        unit_layout.addStretch()
        info_layout.addLayout(unit_layout)

        layout.addWidget(info_card)
        
        # Sections title
        sections_label = QLabel("Секції")
        sections_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(sections_label)
        
        # Sections table
        self.sections_table = QTableWidget()
        self.sections_table.setColumnCount(8)
        self.sections_table.setHorizontalHeaderLabels([
            "Назва", "Всього", "Перекладено", "<—Підпис",
            "Затверджено", "<—Підпис", "Виключити", "Видалення"
        ])
        
        header = self.sections_table.horizontalHeader()
        # Set all columns to interactive by default
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        # Ensure name column has enough space
        header.resizeSection(0, 250)
        # Ensure Translated and Approved columns are readable
        header.resizeSection(2, 110)
        header.resizeSection(4, 110)

        
        self.sections_table.verticalHeader().setVisible(False)
        self.sections_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        self.sections_table.setShowGrid(False)
        layout.addWidget(self.sections_table)
        
        # Add section button
        add_section_btn = QPushButton("Додати секцію")
        add_section_btn.clicked.connect(self.add_section)
        
        # Section buttons row
        section_btns_layout = QHBoxLayout()
        section_btns_layout.addWidget(add_section_btn)
        
        move_sec_up_btn = QPushButton("↑")
        move_sec_up_btn.setToolTip("Перемістити секцію вгору")
        move_sec_up_btn.setFixedWidth(40)
        move_sec_up_btn.clicked.connect(self.move_section_up)
        section_btns_layout.addWidget(move_sec_up_btn)
        
        move_sec_down_btn = QPushButton("↓")
        move_sec_down_btn.setToolTip("Перемістити секцію вниз")
        move_sec_down_btn.setFixedWidth(40)
        move_sec_down_btn.clicked.connect(self.move_section_down)
        section_btns_layout.addWidget(move_sec_down_btn)
        
        layout.addLayout(section_btns_layout)
        
        # Bottom toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addStretch()
        
        save_btn = QPushButton("Зберегти")
        save_btn.setObjectName("primary_btn")
        save_btn.clicked.connect(self.save_project)
        toolbar_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['overlay']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        cancel_btn.clicked.connect(self.cancel_edit)
        toolbar_layout.addWidget(cancel_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Initially disable editor
        self.set_editor_enabled(False)
        
        return panel
    
    def load_projects(self):
        """Load projects into the list"""
        self.project_list.clear()
        data = self.data_manager.load_data()
        
        for project in data:
            self.project_list.addItem(project['game'])
            
        # Select first project if available and nothing selected
        if self.project_list.count() > 0 and self.project_list.currentRow() == -1:
            self.project_list.setCurrentRow(0)
    
    def on_project_selected(self, index: int):
        """Handle project selection"""
        if index < 0:
            self.set_editor_enabled(False)
            return
        
        self.current_project_index = index
        project = self.data_manager.get_project(index)
        
        if project:
            self.load_project_to_editor(project)
            self.set_editor_enabled(True)
    
    def load_project_to_editor(self, project: dict):
        """Load project data into editor"""
        # Set game name
        self.game_name_input.setText(project.get('game', ''))
        self.editor_title.setText(project.get('game', 'Проєкт'))
        
        # Set icon
        icon_path = project.get('icon', '')
        if icon_path:
            self.icon_path_label.setText(icon_path)
            self.icon_path_label.setProperty('icon_path', icon_path)
            self.icon_path_label.setText("Не вибрано")
            self.icon_path_label.setProperty('icon_path', '')
        
        # Set unit
        unit = project.get('unit', 'слів')
        index = self.unit_combo.findText(unit)
        if index >= 0:
            self.unit_combo.setCurrentIndex(index)
        else:
            self.unit_combo.setCurrentIndex(0)
        
        # Load sections
        self.sections_table.setRowCount(0)
        sections = project.get('sections', [])
        
        for section in sections:
            self.add_section_to_table(section)
    
    def add_section_to_table(self, section: dict = None):
        """Add a section row to the table"""
        row = self.sections_table.rowCount()
        self.sections_table.insertRow(row)
        
        # Name
        name_input = QLineEdit()
        name_input.setText(section.get('name', '') if section else '')
        name_input.setPlaceholderText("Назва секції")
        self.sections_table.setCellWidget(row, 0, name_input)
        
        # Total
        total_spin = QSpinBox()
        total_spin.setMaximum(999999999)
        total_spin.setValue(section.get('total', 0) if section else 0)
        self.sections_table.setCellWidget(row, 1, total_spin)
        
        # Translated
        translated_spin = QSpinBox()
        translated_spin.setMaximum(999999999)
        translated_spin.setValue(section.get('translated', 0) if section else 0)
        self.sections_table.setCellWidget(row, 2, translated_spin)
        
        # Translated Label (custom)
        trans_label_input = QLineEdit()
        trans_label_input.setText(section.get('translated_label', '') if section else '')
        trans_label_input.setPlaceholderText("Перекладено")
        self.sections_table.setCellWidget(row, 3, trans_label_input)
        
        # Approved
        approved_spin = QSpinBox()
        approved_spin.setMaximum(999999999)
        approved_spin.setValue(section.get('approved', 0) if section else 0)
        self.sections_table.setCellWidget(row, 4, approved_spin)
        
        # Approved Label (custom)
        appr_label_input = QLineEdit()
        appr_label_input.setText(section.get('approved_label', '') if section else '')
        appr_label_input.setPlaceholderText("Затверджено")
        self.sections_table.setCellWidget(row, 5, appr_label_input)
        
        # Exclude checkbox
        exclude_check = QCheckBox()
        exclude_check.setChecked(section.get('exclude_from_total', False) if section else False)
        exclude_widget = QWidget()
        exclude_layout = QHBoxLayout(exclude_widget)
        exclude_layout.addWidget(exclude_check)
        exclude_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        exclude_layout.setContentsMargins(0, 0, 0, 0)
        self.sections_table.setCellWidget(row, 6, exclude_widget)
        
        # Delete button
        delete_btn = QPushButton("Видалити")
        delete_btn.setObjectName("danger_btn")
        delete_btn.clicked.connect(lambda: self.delete_section(row))
        delete_widget = QWidget()
        delete_layout = QHBoxLayout(delete_widget)
        delete_layout.addWidget(delete_btn)
        delete_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        delete_layout.setContentsMargins(0, 0, 0, 0)
        self.sections_table.setCellWidget(row, 7, delete_widget)
    
    def add_section(self):
        """Add new empty section"""
        self.add_section_to_table()
    
    def delete_section(self, row: int):
        """Delete section from table"""
        self.sections_table.removeRow(row)
    
    def add_project(self):
        """Add new project"""
        # Create empty project
        new_project = {
            'game': 'Новий проєкт',
            'icon': '',
            'unit': 'слів',
            'sections': [
                {
                    'name': 'Текст',
                    'total': 0,
                    'translated': 0,
                    'approved': 0
                }
            ]
        }

        self.data_manager.add_project(new_project)
        self.data_manager.save_data() # Save the new project
        self.load_projects()

        # Select the new project
        self.project_list.setCurrentRow(len(self.data_manager.get_all_projects()) - 1)
        self.data_changed.emit()

        # Show success message
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Успіх")
        msg.setText("Новий проєкт додано")
        msg.exec()

    def delete_project(self):
        """Delete selected project"""
        if self.current_project_index < 0:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Підтвердження",
            "Ви впевнені, що хочете видалити цей проєкт?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_project(self.current_project_index)
            self.data_manager.save_data()
            self.load_projects()
            self.set_editor_enabled(False)
            self.data_changed.emit()
            
            # Show success message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Успіх")
            msg.setText("Проєкт видалено")
            msg.exec()
    
    def save_project(self):
        """Save current project"""
        try:
            # Build project dict
            project = {
                'game': self.game_name_input.text().strip(),
                'icon': self.icon_path_label.property('icon_path') or '',
                'unit': self.unit_combo.currentText(),
                'sections': []
            }
            
            # Get sections from table
            for row in range(self.sections_table.rowCount()):
                name_input = self.sections_table.cellWidget(row, 0)
                total_spin = self.sections_table.cellWidget(row, 1)
                translated_spin = self.sections_table.cellWidget(row, 2)
                translated_label_input = self.sections_table.cellWidget(row, 3)
                approved_spin = self.sections_table.cellWidget(row, 4)
                approved_label_input = self.sections_table.cellWidget(row, 5)
                exclude_widget = self.sections_table.cellWidget(row, 6)
                exclude_check = exclude_widget.findChild(QCheckBox)
                
                section = {
                    'name': name_input.text().strip(),
                    'total': total_spin.value(),
                    'translated': translated_spin.value(),
                    'approved': approved_spin.value(),
                }
                
                # Add custom labels if provided
                translated_label = translated_label_input.text().strip()
                if translated_label:
                    section['translated_label'] = translated_label
                
                approved_label = approved_label_input.text().strip()
                if approved_label:
                    section['approved_label'] = approved_label
                
                if exclude_check.isChecked():
                    section['exclude_from_total'] = True
                
                project['sections'].append(section)
            
            # Update or add project
            if self.current_project_index >= 0:
                self.data_manager.update_project(self.current_project_index, project)
            else:
                self.data_manager.add_project(project)
            
            # Save to file
            self.data_manager.save_data()
            self.load_projects()
            self.data_changed.emit()
            
            # Show success message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Успіх")
            msg.setText("Проєкт збережено")
            msg.exec()
            
        except ValidationError as e:
            # Show error message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Помилка валідації")
            msg.setText(str(e))
            msg.exec()
        except Exception as e:
            # Show error message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Помилка")
            msg.setText(f"Не вдалося зберегти: {e}")
            msg.exec()
    
    def cancel_edit(self):
        """Cancel editing and reload"""
        if self.current_project_index >= 0:
            project = self.data_manager.get_project(self.current_project_index)
            if project:
                self.load_project_to_editor(project)
    
    def pick_icon(self):
        """Open file dialog to pick icon"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Вибрати іконку",
            "./icons",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            self.icon_path_label.setText(file_path)
            self.icon_path_label.setProperty('icon_path', file_path)
    
    def set_editor_enabled(self, enabled: bool):
        """Enable/disable editor controls"""
        if not enabled:
            self.editor_title.setText("Виберіть проєкт для редагування")
            self.game_name_input.clear()
            self.icon_path_label.setText("Не вибрано")
            self.unit_combo.setCurrentIndex(0)
            self.sections_table.setRowCount(0)
            
    def move_project_up(self):
        """Move selected project up"""
        if self.current_project_index <= 0:
            return
            
        try:
            new_index = self.current_project_index - 1
            self.data_manager.move_project(self.current_project_index, new_index)
            self.data_manager.save_data()
            self.load_projects()
            self.project_list.setCurrentRow(new_index)
            self.data_changed.emit()
        except ValidationError as e:
            QMessageBox.warning(self, "Помилка", str(e))
            
    def move_project_down(self):
        """Move selected project down"""
        total_projects = len(self.data_manager.get_all_projects())
        if self.current_project_index < 0 or self.current_project_index >= total_projects - 1:
            return
            
        try:
            new_index = self.current_project_index + 1
            self.data_manager.move_project(self.current_project_index, new_index)
            self.data_manager.save_data()
            self.load_projects()
            self.project_list.setCurrentRow(new_index)
            self.data_changed.emit()
        except ValidationError as e:
            QMessageBox.warning(self, "Помилка", str(e))

    def get_sections_data(self) -> list:
        """Helper to get current sections data from table"""
        sections = []
        for row in range(self.sections_table.rowCount()):
            name_input = self.sections_table.cellWidget(row, 0)
            total_spin = self.sections_table.cellWidget(row, 1)
            translated_spin = self.sections_table.cellWidget(row, 2)
            translated_label_input = self.sections_table.cellWidget(row, 3)
            approved_spin = self.sections_table.cellWidget(row, 4)
            approved_label_input = self.sections_table.cellWidget(row, 5)
            exclude_widget = self.sections_table.cellWidget(row, 6)
            exclude_check = exclude_widget.findChild(QCheckBox)
            
            section = {
                'name': name_input.text().strip(),
                'total': total_spin.value(),
                'translated': translated_spin.value(),
                'approved': approved_spin.value(),
            }
            
            # Add custom labels if provided
            translated_label = translated_label_input.text().strip()
            if translated_label:
                section['translated_label'] = translated_label
            
            approved_label = approved_label_input.text().strip()
            if approved_label:
                section['approved_label'] = approved_label
            
            if exclude_check.isChecked():
                section['exclude_from_total'] = True
                
            sections.append(section)
        return sections

    def move_section_up(self):
        """Move selected section up"""
        current_row = self.sections_table.currentRow()
        if current_row <= 0:
            return
            
        # Get data, swap, and reload
        sections = self.get_sections_data()
        sections[current_row], sections[current_row - 1] = sections[current_row - 1], sections[current_row]
        
        # Clear and reload
        self.sections_table.setRowCount(0)
        for section in sections:
            self.add_section_to_table(section)
            
        # Restore selection
        self.sections_table.selectRow(current_row - 1)

    def move_section_down(self):
        """Move selected section down"""
        current_row = self.sections_table.currentRow()
        if current_row < 0 or current_row >= self.sections_table.rowCount() - 1:
            return
            
        # Get data, swap, and reload
        sections = self.get_sections_data()
        sections[current_row], sections[current_row + 1] = sections[current_row + 1], sections[current_row]
        
        # Clear and reload
        self.sections_table.setRowCount(0)
        for section in sections:
            self.add_section_to_table(section)
            
        # Restore selection
        self.sections_table.selectRow(current_row + 1)
