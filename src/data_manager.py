"""
Data management layer for Progress Visualizer
Handles loading, saving, and validation of project data
"""

import json
import os
from typing import List, Dict, Optional, Tuple

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT_DIR, "data.json")


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class DataManager:
    """Manages project data with validation"""
    
    def __init__(self, data_file: str = DATA_FILE):
        self.data_file = data_file
        self.data: List[Dict] = []
    
    def load_data(self) -> List[Dict]:
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                return self.data
            except json.JSONDecodeError as e:
                raise ValidationError(f"Помилка читання JSON: {e}")
        return []
    
    def save_data(self, data: Optional[List[Dict]] = None) -> None:
        """Save data to JSON file with validation"""
        if data is not None:
            self.data = data
        
        # Validate all projects before saving
        for i, project in enumerate(self.data):
            try:
                self.validate_project(project)
            except ValidationError as e:
                raise ValidationError(f"Помилка у проєкті #{i+1}: {e}")
        
        # Save to file
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def validate_project(self, project: Dict) -> None:
        """Validate project structure"""
        # Check required fields
        if "game" not in project:
            raise ValidationError("Відсутнє поле 'game'")
        
        if not project["game"].strip():
            raise ValidationError("Назва гри не може бути порожньою")
        
        if "is_released" in project and project["is_released"]:
            return  # Skip sections validation for released projects
            
        if "sections" not in project:
            raise ValidationError("Відсутнє поле 'sections'")
        
        if not isinstance(project["sections"], list):
            raise ValidationError("'sections' має бути списком")
        
        # if len(project["sections"]) == 0:
        #     raise ValidationError("Проєкт має містити хоча б одну секцію")
        
        # Check icon file if specified
        if "icon" in project and project["icon"]:
            if not os.path.exists(project["icon"]):
                raise ValidationError(f"Файл іконки не знайдено: {project['icon']}")
        
        # Check header file if specified
        if "header" in project and project["header"]:
            if not os.path.exists(project["header"]):
                raise ValidationError(f"Файл гедера не знайдено: {project['header']}")
        
        # Check unit
        valid_units = ["слів", "рядків", "файлів"]
        if "unit" in project and project["unit"] not in valid_units:
            raise ValidationError(f"Невідома одиниця виміру: {project['unit']}")

        # Validate all sections
        for i, section in enumerate(project["sections"]):
            try:
                self.validate_section(section)
            except ValidationError as e:
                raise ValidationError(f"Секція #{i+1}: {e}")
    
    def validate_section(self, section: Dict) -> None:
        """Validate section structure"""
        # Check required fields
        required_fields = ["name", "total", "translated", "approved"]
        for field in required_fields:
            if field not in section:
                raise ValidationError(f"Відсутнє поле '{field}'")
        
        # Check name
        if not section["name"].strip():
            raise ValidationError("Назва секції не може бути порожньою")
        
        # Check numeric fields
        try:
            total = int(section["total"])
            translated = int(section["translated"])
            approved = int(section["approved"])
        except (ValueError, TypeError):
            raise ValidationError("Поля total/translated/approved мають бути цілими числами")
        
        # Check logic
        if total < 0:
            raise ValidationError("total не може бути від'ємним")
        
        if translated < 0:
            raise ValidationError("translated не може бути від'ємним")
        
        if approved < 0:
            raise ValidationError("approved не може бути від'ємним")
        
        if translated > total:
            raise ValidationError(f"translated ({translated}) не може бути більше за total ({total})")
        
        if approved > translated:
            raise ValidationError(f"approved ({approved}) не може бути більше за translated ({translated})")
    
    def add_project(self, project: Dict) -> None:
        """Add a new project"""
        self.validate_project(project)
        self.data.append(project)
    
    def update_project(self, index: int, project: Dict) -> None:
        """Update existing project"""
        if index < 0 or index >= len(self.data):
            raise ValidationError(f"Невірний індекс проєкту: {index}")
        
        self.validate_project(project)
        self.data[index] = project
    
    def delete_project(self, index: int) -> None:
        """Delete project by index"""
        if index < 0 or index >= len(self.data):
            raise ValidationError(f"Невірний індекс проєкту: {index}")
        
        del self.data[index]
    
    def get_project(self, index: int) -> Optional[Dict]:
        """Get project by index"""
        if 0 <= index < len(self.data):
            return self.data[index]
        return None
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects"""
        return self.data
    
    def move_project(self, old_index: int, new_index: int) -> None:
        """Move project from old_index to new_index"""
        if old_index < 0 or old_index >= len(self.data):
            raise ValidationError(f"Невірний поточний індекс: {old_index}")
        
        if new_index < 0 or new_index >= len(self.data):
            raise ValidationError(f"Невірний новий індекс: {new_index}")
            
        if old_index == new_index:
            return
            
        project = self.data.pop(old_index)
        self.data.insert(new_index, project)


def load_data() -> List[Dict]:
    """Convenience function for backward compatibility"""
    manager = DataManager()
    return manager.load_data()
