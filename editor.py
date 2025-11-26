"""
Modern GUI Editor for Progress Visualizer
Uses native PyQt6 with custom styling
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QHeaderView, QSpinBox, QCheckBox, QMessageBox, QSplitter,
    QListWidget, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon

from data_manager import DataManager, ValidationError
from colors import COLORS


class EditorWidget(QWidget):
    """Main editor widget with Fluent Design"""
    
    data_changed = pyqtSignal()  # Signal when data is saved
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager = DataManager()
        self.current_project_index = -1
        self.init_ui()
        self.load_projects()
    
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
        
        # Apply dark theme
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
            QLabel {{
                color: {COLORS['text']};
            }}
            QLineEdit, QSpinBox {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                color: {COLORS['text']};
                min-height: 20px;
                min-width: 100px;
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border: 1px solid {COLORS['accent']};
            }}
            QTableWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                gridline-color: {COLORS['border']};
                color: {COLORS['text']};
            }}
            QTableWidget::item {{
                padding: 4px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['overlay']};
                color: {COLORS['text']};
                padding: 6px;
                border: none;
                font-weight: bold;
            }}
        """)
    
    def create_project_list_panel(self) -> QWidget:
        """Create left panel with project list"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Проєкти")
        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['text']};
            padding: 10px;
        """)
        layout.addWidget(title)
        
        # Project list
        self.project_list = QListWidget()
        self.project_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['accent']};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        self.project_list.currentRowChanged.connect(self.on_project_selected)
        layout.addWidget(self.project_list)
        
        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)
        
        add_btn = QPushButton("Додати проєкт")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #7aa4f0;
            }}
        """)
        add_btn.clicked.connect(self.add_project)
        btn_layout.addWidget(add_btn)
        
        delete_btn = QPushButton("Видалити проєкт")
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['error']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #e74c6c;
            }}
        """)
        delete_btn.clicked.connect(self.delete_project)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        return panel
    
    def create_editor_panel(self) -> QWidget:
        """Create right panel with project editor"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        self.editor_title = QLabel("Виберіть проєкт для редагування")
        self.editor_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {COLORS['text']};
            padding: 10px;
        """)
        layout.addWidget(self.editor_title)
        
        # Game info card
        info_card = QFrame()
        info_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
                padding: 16px;
            }}
        """)
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
        icon_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['overlay']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        icon_btn.clicked.connect(self.pick_icon)
        icon_layout.addWidget(icon_label)
        icon_layout.addWidget(self.icon_path_label, 1)
        icon_layout.addWidget(icon_btn)
        info_layout.addLayout(icon_layout)
        
        layout.addWidget(info_card)
        
        # Sections title
        sections_label = QLabel("Секції")
        sections_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['text']};
            padding: 10px 0;
        """)
        layout.addWidget(sections_label)
        
        # Sections table
        self.sections_table = QTableWidget()
        self.sections_table.setColumnCount(8)
        self.sections_table.setHorizontalHeaderLabels([
            "Назва", "Всього", "Перекладено", "Мітка 'Перекладено'",
            "Затверджено", "Мітка 'Затверджено'", "Виключити", "Дії"
        ])
        
        header = self.sections_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 8):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.sections_table.verticalHeader().setVisible(False)
        self.sections_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.sections_table)
        
        # Add section button
        add_section_btn = QPushButton("Додати секцію")
        add_section_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['overlay']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        add_section_btn.clicked.connect(self.add_section)
        layout.addWidget(add_section_btn)
        
        # Bottom toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addStretch()
        
        save_btn = QPushButton("Зберегти")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #7aa4f0;
            }}
        """)
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
        else:
            self.icon_path_label.setText("Не вибрано")
            self.icon_path_label.setProperty('icon_path', '')
        
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
        name_input.setMinimumWidth(200)
        self.sections_table.setCellWidget(row, 0, name_input)
        
        # Total
        total_spin = QSpinBox()
        total_spin.setMaximum(999999999)
        total_spin.setValue(section.get('total', 0) if section else 0)
        total_spin.setMinimumWidth(100)
        self.sections_table.setCellWidget(row, 1, total_spin)
        
        # Translated
        translated_spin = QSpinBox()
        translated_spin.setMaximum(999999999)
        translated_spin.setValue(section.get('translated', 0) if section else 0)
        translated_spin.setMinimumWidth(100)
        self.sections_table.setCellWidget(row, 2, translated_spin)
        
        # Translated Label (custom)
        trans_label_input = QLineEdit()
        trans_label_input.setText(section.get('translated_label', '') if section else '')
        trans_label_input.setPlaceholderText("Перекладено")
        trans_label_input.setMinimumWidth(120)
        self.sections_table.setCellWidget(row, 3, trans_label_input)
        
        # Approved
        approved_spin = QSpinBox()
        approved_spin.setMaximum(999999999)
        approved_spin.setValue(section.get('approved', 0) if section else 0)
        approved_spin.setMinimumWidth(100)
        self.sections_table.setCellWidget(row, 4, approved_spin)
        
        # Approved Label (custom)
        appr_label_input = QLineEdit()
        appr_label_input.setText(section.get('approved_label', '') if section else '')
        appr_label_input.setPlaceholderText("Затверджено")
        appr_label_input.setMinimumWidth(120)
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
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(30, 30)
        delete_btn.clicked.connect(lambda: self.delete_section(row))
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['error']};
                border: none;
                border-radius: 4px;
                color: white;
            }}
            QPushButton:hover {{
                background-color: #e74c6c;
            }}
        """)
        self.sections_table.setCellWidget(row, 7, delete_btn)
    
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
            self.sections_table.setRowCount(0)
