"""
Visualization widget for displaying translation progress
Refactored from original main.py
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QFrame, QScrollArea, QHeaderView, QProgressBar,
    QPushButton, QFileDialog, QLayout, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QColor, QFont, QPainter, QLinearGradient, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRect, QPoint, QSize

from data_manager import DataManager
from theme_manager import theme_manager

COLORS = theme_manager.get_theme()


class FlowLayout(QLayout):
    """Standard FlowLayout implementation"""
    def __init__(self, parent=None, margin=0, hSpacing=10, vSpacing=10):
        super(FlowLayout, self).__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self._hSpacing = hSpacing
        self._vSpacing = vSpacing
        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def horizontalSpacing(self):
        return self._hSpacing

    def verticalSpacing(self):
        return self._vSpacing

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        spacing = self.verticalSpacing()
        
        # Smart Grid Logic: Calculate how many items fit in a row
        # then distribute width equally
        
        visible_items = [item for item in self._item_list if not item.widget().isHidden()]
        if not visible_items:
            return 0
            
        available_width = rect.width()
        
        # Estimate col count
        ref_item = visible_items[0]
        min_item_width = ref_item.sizeHint().width()
        if min_item_width <= 0: min_item_width = 100
            
        columns = max(1, (available_width + self.horizontalSpacing()) // (min_item_width + self.horizontalSpacing()))
        item_width = (available_width - (columns - 1) * self.horizontalSpacing()) // columns
        
        # Buffer for current row items to equalize height
        row_items = []
        
        for i, item in enumerate(visible_items):
            row_items.append(item)
            
            # If row is full or last item, process the row
            if len(row_items) == columns or i == len(visible_items) - 1:
                # Calculate max height for this row
                max_h = 0
                for ri in row_items:
                    if ri.hasHeightForWidth():
                        h = ri.heightForWidth(item_width)
                    else:
                        h = ri.sizeHint().height()
                    # Ensure minimum height is respected
                    h = max(h, ri.minimumSize().height()) 
                    max_h = max(max_h, h)
                
                # Apply geometry to all items in this row
                for col_index, ri in enumerate(row_items):
                    current_x = rect.x() + col_index * (item_width + self.horizontalSpacing())
                    
                    if not testOnly:
                        ri.setGeometry(QRect(QPoint(current_x, y), QSize(item_width, max_h)))
                
                # Advance Y based on the max height of the row
                y += max_h + spacing
                row_items = []
                
        return y - spacing - rect.y()


class AuroraCard(QFrame):
    """Custom frame for Aurora theme with a subtle background logo"""
    def __init__(self, icon_path=None, parent=None):
        super().__init__(parent)
        self.icon_path = icon_path
        self.bg_pixmap = None
        if icon_path and os.path.exists(icon_path):
            self.bg_pixmap = QPixmap(icon_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        # Adjusted stops to match theme spirit
        c1 = QColor(COLORS.get('surface', '#0b0c1a'))
        c2 = QColor(COLORS.get('overlay', '#12142b'))
        
        gradient = QLinearGradient(0, 0, rect.width(), rect.height())
        gradient.setColorAt(0, c1)
        gradient.setColorAt(0.4, c2)
        gradient.setColorAt(1, c1)
        
        # Background
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 16, 16)
        
        # Transparent Logo
        if self.bg_pixmap and not self.bg_pixmap.isNull():
            painter.setOpacity(0.08) # Subtle "fancy" opacity
            
            # Scale to fit within the tile (Contain)
            scaled_pix = self.bg_pixmap.scaled(
                rect.width(), rect.height(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Center horizontally, position at bottom with 10px margin
            px = (rect.width() - scaled_pix.width()) // 2
            py = rect.height() - scaled_pix.height() - 10
            
            # Clip to rounded rect using QPainterPath
            path = QPainterPath()
            path.addRoundedRect(rect.toRectF(), 16, 16)
            painter.setClipPath(path)
            
            painter.drawPixmap(px, py, scaled_pix)
            painter.setClipping(False)
            
        # Border
        painter.setOpacity(1.0)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QColor(COLORS.get('border', '#1e293b')))
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), 16, 16)


class VisualizerWidget(QWidget):
    """Widget for visualizing translation progress"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager = DataManager()
        self.init_ui()
        self.refresh()
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self.on_theme_changed)
    
    def on_theme_changed(self, theme_name):
        """Handle theme changes"""
        # Re-apply styles to main scroll area
        self.apply_base_styles()
        
        # Total layout refresh
        self.refresh()
    
    def init_ui(self):
        """Initialize the UI"""
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for projects
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        # Scroll widget will be created in refresh()
        self.scroll_widget = None
        self.main_layout = None
        
        layout.addWidget(self.scroll)
        
        # Export button
        self.export_btn = QPushButton("Експортувати як зображення")
        self.export_btn.clicked.connect(self.export_as_image)
        layout.addWidget(self.export_btn)
        
        # Apply initial styles
        self.apply_base_styles()
        
        self.setLayout(layout)
    
    def apply_base_styles(self):
        """Apply base styles that don't change with contents"""
        # Update colors reference in case it changed
        global COLORS
        COLORS = theme_manager.get_theme()
        
        self.scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {COLORS['background']};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {COLORS['surface']};
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['overlay']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        if self.scroll_widget:
            self.scroll_widget.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # Export button styles
        accent_color = COLORS.get('accent', '#3b82f6')
        hover_color = COLORS.get('hover', '#7aa4f0')
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: {COLORS['background']};
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['pressed']};
            }}
        """)
    
    def refresh(self):
        """Refresh the visualization with current data"""
        # Update colors reference in case it changed
        global COLORS
        COLORS = theme_manager.get_theme()
        
        # Create new scroll widget based on theme
        if self.scroll_widget:
            self.scroll_widget.deleteLater()
            
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # Root layout for scroll content is ALWAYS vertical
        # This ensures the date label acts as a header above the content
        root_layout = QVBoxLayout(self.scroll_widget)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(20)
        
        self.scroll.setWidget(self.scroll_widget)
        
        # --- Date Label (Header) ---
        today_str = datetime.now().strftime("%d.%m.%Y")
        date_label = QLabel(f"Станом на {today_str}")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['surface']};
                color: {COLORS['subtext']};
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        # Add to ROOT layout (above projects)
        root_layout.addWidget(date_label)
        
        # --- Projects Container ---
        projects_container = QWidget()
        projects_container.setStyleSheet("background: transparent;")
        
        if theme_manager.current_theme_name == "aurora":
            self.main_layout = FlowLayout(projects_container, margin=0, hSpacing=20, vSpacing=20)
        else:
            self.main_layout = QVBoxLayout(projects_container)
            self.main_layout.setSpacing(10)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            
        root_layout.addWidget(projects_container)
        
        # Update export button style
        accent_color = COLORS.get('accent', '#3b82f6')
        hover_color = COLORS.get('hover', '#7aa4f0')
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: {COLORS['background']};
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['pressed']};
            }}
        """)
        
        # Load data
        data = self.data_manager.load_data()
        
        # Determine if we need a Hero tile (Odd count + Aurora)
        is_odd = len(data) % 2 != 0
        use_hero = is_odd and theme_manager.current_theme_name == "aurora"
        
        # Add projects logic
        for i, game in enumerate(data):
            if i == 0 and use_hero:
                # Special case: Hero card takes full width by being placed in root_layout
                game_frame = self.create_aurora_game_frame(game, is_hero=True)
                # Insert after date label (index 0)
                root_layout.insertWidget(1, game_frame)
                continue
                
            if theme_manager.current_theme_name == "aurora":
                game_frame = self.create_aurora_game_frame(game)
            else:
                game_frame = self.create_classic_game_frame(game)
            
            self.main_layout.addWidget(game_frame)
    
    def create_classic_game_frame(self, game: dict) -> QFrame:
        """Create a frame for a single game (Classic Layout)"""
        game_frame = QFrame()
        game_frame.setFrameStyle(QFrame.Shape.NoFrame)
        surface_gradient = COLORS.get('gradient_card', COLORS['surface'])
        game_frame.setStyleSheet(f"""
            QFrame {{
                background: {surface_gradient};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        game_layout = QHBoxLayout(game_frame)
        game_layout.setContentsMargins(0, 0, 0, 0)
        game_layout.setSpacing(0)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(200, 160)
        if game.get("icon") and os.path.exists(game["icon"]):
            pixmap = QPixmap(game["icon"])
            # Use KeepAspectRatio to prevent stretching
            scaled_pixmap = pixmap.scaled(200, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['mantle']};
                border-right: 1px solid {COLORS['border']};
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            }}
        """)
        game_layout.addWidget(icon_label)
        
        # Right side - title + table
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Title
        title_label = QLabel(game['game'])
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {COLORS['text']};
                font-weight: bold;
                font-size: 18px;
                padding: 12px 15px;
                border-bottom: 1px solid {COLORS['border']};
            }}
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
    
    def create_aurora_game_frame(self, game: dict, is_hero: bool = False) -> QFrame:
        """Create a frame for a single game (Aurora Nebula Card Layout)"""
        # Use our custom card with background logo support
        game_frame = AuroraCard(icon_path=game.get("icon"))
        game_frame.setFrameStyle(QFrame.Shape.NoFrame)
        
        if is_hero:
            # Hero takes full width available in root layout
            game_frame.setMinimumHeight(350)
            game_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        else:
            # Pairs are squares/regular tiles
            game_frame.setMinimumSize(400, 400)
            game_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        main_layout = QVBoxLayout(game_frame)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # --- Header Section ---
        header_container = QWidget()
        # Set a fixed height for the header to ensure alignment across all cards
        # 140px accommodates icon (120px) + margins comfortably
        header_container.setFixedHeight(140)
        header_container.setStyleSheet("background: transparent; border: none;")
        
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(120, 120)
        if game.get("icon") and os.path.exists(game["icon"]):
            pixmap = QPixmap(game["icon"])
            scaled_pixmap = pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Fancy radial glow for the icon container
        icon_bg = f"qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.6, fx:0.5, fy:0.5, stop:0 {COLORS.get('overlay', '#12142b')}, stop:1 {COLORS.get('mantle', '#000000')})"
        icon_label.setStyleSheet(f"""
            background-color: {icon_bg};
            border-radius: 16px;
            border: 1px solid {COLORS['border']};
        """)
        header_layout.addWidget(icon_label)
        
        # Title and Overall Stats
        title_stats_layout = QVBoxLayout()
        # Align title/stats to center vertically within the header
        title_stats_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Title
        title_label = QLabel(game['game'])
        title_label.setStyleSheet(f"""
            background-color: transparent;
            color: {COLORS['text']};
            font-weight: bold;
            font-size: 24px;
            border: none;
        """)
        title_stats_layout.addWidget(title_label)
        
        # Overall Progress
        sections = game.get("sections", [])
        if sections:
            included_sections = [s for s in sections if not s.get("exclude_from_total", False)]
            total_sum = sum(s["total"] for s in included_sections)
            translated_sum = sum(s["translated"] for s in included_sections)
            approved_sum = sum(s["approved"] for s in included_sections)
            
            overall_trans_pct = round(translated_sum / total_sum * 100, 2) if total_sum > 0 else 0
            overall_appr_pct = round(approved_sum / total_sum * 100, 2) if total_sum > 0 else 0
            
            # Custom Progress Widget (Simulated with layout)
            progress_widget = QWidget()
            progress_widget.setStyleSheet("background: transparent; border: none;")
            prog_layout = QVBoxLayout(progress_widget)
            prog_layout.setContentsMargins(0, 5, 0, 0)
            prog_layout.setSpacing(8)
            
            # Trans bar
            t_bar = self.create_aurora_progress_bar(overall_trans_pct, COLORS['gradient_translated'])
            t_label = QLabel(f"ПЕРЕКЛАДЕНО: {overall_trans_pct:.1f}% ({translated_sum}/{total_sum})")
            t_label.setStyleSheet(f"color: {COLORS['accent']}; font-weight: bold; font-size: 12px; border: none;")
            prog_layout.addWidget(t_label)
            prog_layout.addWidget(t_bar)
            
            # Appr bar
            a_bar = self.create_aurora_progress_bar(overall_appr_pct, COLORS['gradient_approved'])
            a_label = QLabel(f"ЗАТВЕРДЖЕНО: {overall_appr_pct:.1f}% ({approved_sum}/{total_sum})")
            a_label.setStyleSheet(f"color: {COLORS['info']}; font-weight: bold; font-size: 12px; border: none;")
            prog_layout.addWidget(a_label)
            prog_layout.addWidget(a_bar)
            
            title_stats_layout.addWidget(progress_widget)
            
        header_layout.addLayout(title_stats_layout)
        
        # Add header container to main layout
        # Ensure it doesn't stretch vertically
        main_layout.addWidget(header_container, 0, Qt.AlignmentFlag.AlignTop)
        
        # Separator using QFrame line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet(f"background-color: {COLORS['border']}; border: none; max-height: 1px;")
        main_layout.addWidget(line)
        
        # --- Sections Grid ---
        # Instead of a table, we use a Flow Layout or just a VBox of styled rows
        # This layout needs to be able to expand
        sections_widget = QWidget()
        sections_widget.setStyleSheet("background: transparent;")
        # Allow sections widget to expand
        sections_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        sections_layout = QVBoxLayout(sections_widget)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(10)
        # Align contents to top so they don't spread out weirdly if we don't want them to
        # But user said "sections stretch". This usually implies the *area* stretches.
        # If we align top, the bottom will be empty space.
        sections_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        for section in sections:
            sec_widget = self.create_aurora_section_row(section)
            sections_layout.addWidget(sec_widget)
            
        main_layout.addWidget(sections_widget)
        # Add a stretch at the end to ensure empty space is at the bottom if any
        # Although Expanding policy on sections_widget should handle it if layout respects it
        # main_layout.addStretch() # Only if we want to force everything up
        
        return game_frame

    def create_aurora_progress_bar(self, value, chunk_color):
        """Helper to create a slim, modern progress bar with rounded corners even for low values"""
        bar = QProgressBar()
        # Use 0-1000 for higher precision in rendering
        bar.setRange(0, 1000)
        
        # Calculate visual value (ensure > 0 results in a visible dot/circle)
        # For an 8px high bar, we want at least ~12px width for a nice rounded pill.
        # 40/1000 = 4%. On a 300px bar, that's 12px.
        visual_value = int(value * 10)
        if value > 0:
            visual_value = max(visual_value, 40)
            
        bar.setValue(visual_value)
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                background-color: {COLORS['mantle']};
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background: {chunk_color};
                border-radius: 4px;
                min-width: 8px;
            }}
        """)
        return bar

    def create_aurora_section_row(self, section):
        """Create a stylish row for a section with subtle glow borders"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['overlay']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
            QFrame:hover {{
                border: 1px solid {COLORS['accent']};
            }}
        """)
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Name
        name_label = QLabel(section['name'])
        name_label.setFixedWidth(200)
        name_label.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold; font-size: 14px; border: none; background: transparent;")
        layout.addWidget(name_label)
        
        # Stats Container
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(4)
        
        total = section['total']
        trans = section['translated']
        appr = section['approved']
        
        trans_pct = trans / total * 100 if total > 0 else 0
        appr_pct = appr / total * 100 if total > 0 else 0
        
        # Get labels
        t_label_full = section.get("translated_label", "Перекладено")
        t_char = t_label_full[0].upper() if t_label_full else "T"
        
        a_label_full = section.get("approved_label", "Затверджено")
        a_char = a_label_full[0].upper() if a_label_full else "Z"
        
        # Translated Row
        t_row = QHBoxLayout()
        t_lbl = QLabel(f"{t_char}: {trans_pct:.1f}%")
        t_lbl.setFixedWidth(60)
        t_lbl.setStyleSheet(f"color: {COLORS['subtext']}; font-size: 11px; border: none; background: transparent;")
        t_bar = self.create_aurora_progress_bar(trans_pct, COLORS['gradient_translated'])
        t_row.addWidget(t_lbl)
        t_row.addWidget(t_bar)
        stats_layout.addLayout(t_row)
        
        # Approved Row
        a_row = QHBoxLayout()
        a_lbl = QLabel(f"{a_char}: {appr_pct:.1f}%")
        a_lbl.setFixedWidth(60)
        a_lbl.setStyleSheet(f"color: {COLORS['subtext_dim']}; font-size: 11px; border: none; background: transparent;")
        a_bar = self.create_aurora_progress_bar(appr_pct, COLORS['gradient_approved'])
        a_row.addWidget(a_lbl)
        a_row.addWidget(a_bar)
        stats_layout.addLayout(a_row)
        
        layout.addLayout(stats_layout)
        
        # Counts (Right aligned)
        counts_layout = QVBoxLayout()
        c_trans = QLabel(f"{trans}/{total}")
        c_trans.setAlignment(Qt.AlignmentFlag.AlignRight)
        c_trans.setStyleSheet(f"color: {COLORS['text']}; font-weight: bold; border: none; background: transparent;")
        
        c_appr = QLabel(f"{appr}/{total}")
        c_appr.setAlignment(Qt.AlignmentFlag.AlignRight)
        c_appr.setStyleSheet(f"color: {COLORS['subtext_dim']}; border: none; background: transparent;")
        
        counts_layout.addWidget(c_trans)
        counts_layout.addWidget(c_appr)
        
        layout.addLayout(counts_layout)
        
        return widget
    
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
            section_item.setBackground(QColor(COLORS['overlay']))
            section_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            table.setItem(0, col_start, section_item)
            table.setSpan(0, col_start, 1, 2)
            
            # Subheaders
            translated_label = section.get("translated_label", "Перекладено")
            approved_label = section.get("approved_label", "Затверджено")
            
            translated_header = QTableWidgetItem(translated_label)
            translated_header.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            translated_header.setBackground(QColor(COLORS['surface']))
            table.setItem(1, col_start, translated_header)
            
            approved_header = QTableWidgetItem(approved_label)
            approved_header.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            approved_header.setBackground(QColor(COLORS['surface']))
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
            translated_progress.setFixedHeight(20)
            trans_grad = COLORS.get('gradient_translated', COLORS['progress_translated'])
            translated_progress.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {COLORS['border']};
                    border-radius: 4px;
                    background-color: {COLORS['mantle']};
                    text-align: center;
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    margin: 2px;
                }}
                QProgressBar::chunk {{
                    background: {trans_grad};
                    border-radius: 3px;
                }}
            """)
            table.setCellWidget(3, col_start, translated_progress)
            
            approved_progress = QProgressBar()
            approved_progress.setValue(int(approved_percent))
            approved_progress.setFormat(f"{approved_percent:.2f}%")
            approved_progress.setFixedHeight(20)
            appr_grad = COLORS.get('gradient_approved', COLORS['progress_approved'])
            approved_progress.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {COLORS['border']};
                    border-radius: 4px;
                    background-color: {COLORS['mantle']};
                    text-align: center;
                    color: white;
                    font-size: 11px;
                    font-weight: bold;
                    margin: 2px;
                }}
                QProgressBar::chunk {{
                    background: {appr_grad};
                    border-radius: 3px;
                }}
            """)
            table.setCellWidget(3, col_start + 1, approved_progress)
        
        # Table settings
        table.setFixedHeight(120)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(True)
        
        table.setRowHeight(0, 32)
        table.setRowHeight(1, 28)
        table.setRowHeight(2, 28)
        table.setRowHeight(3, 32)
        
        header = table.horizontalHeader()
        for i in range(table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        table.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: {COLORS['border']};
                background-color: {COLORS['mantle']};
                color: {COLORS['text']};
                border: none;
                font-size: 12px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['overlay']};
                color: {COLORS['text']};
                padding: 5px;
                border: 1px solid {COLORS['border']};
                font-weight: bold;
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 5px;
                border: 1px solid {COLORS['border']};
            }}
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
        translated_progress.setMinimumHeight(24)
        trans_grad = COLORS.get('gradient_translated', COLORS['progress_translated'])
        translated_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                background-color: {COLORS['mantle']};
                text-align: center;
                color: white;
                font-weight: bold;
                margin-bottom: 2px;
            }}
            QProgressBar::chunk {{
                background: {trans_grad};
                border-radius: 5px;
            }}
        """)
        
        # Approved progress
        approved_progress = QProgressBar()
        approved_progress.setValue(int(overall_approved_percent))
        approved_progress.setFormat(f"Затверджено: {overall_approved_percent:.2f}% {words_info_appr}")
        approved_progress.setMinimumHeight(24)
        appr_grad = COLORS.get('gradient_approved', COLORS['progress_approved'])
        approved_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                background-color: {COLORS['mantle']};
                text-align: center;
                color: white;
                font-weight: bold;
                margin-top: 2px;
            }}
            QProgressBar::chunk {{
                background: {appr_grad};
                border-radius: 5px;
            }}
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
