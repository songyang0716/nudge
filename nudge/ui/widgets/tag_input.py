"""Tag input widget with autocomplete and color management."""
import random
from typing import List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QKeyEvent
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from nudge.core.models import Tag

# Material Design color palette
PRESET_COLORS = [
    "#FF6B6B",  # Red
    "#4ECDC4",  # Teal
    "#45B7D1",  # Blue
    "#FFA07A",  # Orange
    "#98D8C8",  # Mint
    "#F7DC6F",  # Yellow
    "#BB8FCE",  # Purple
    "#85C1E2",  # Light Blue
    "#F8B88B",  # Peach
    "#52BE80",  # Green
]


class TagChip(QWidget):
    """A colored chip widget displaying a tag with remove button."""
    
    removed = pyqtSignal(str)  # Emits tag name when removed
    
    def __init__(self, tag_name: str, color: str, parent=None):
        super().__init__(parent)
        self.tag_name = tag_name
        self.color = color
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)
        
        # Tag label
        self.label = QLabel(tag_name)
        self.label.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: #000000;
                border-radius: 10px;
                padding: 4px 8px;
                font-size: 12px;
            }}
        """)
        
        # Remove button
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(20, 20)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #000;
            }
        """)
        self.remove_btn.clicked.connect(lambda: self.removed.emit(self.tag_name))
        
        layout.addWidget(self.label)
        layout.addWidget(self.remove_btn)


class TagInputWidget(QWidget):
    """Widget for managing multiple tags with autocomplete."""
    
    tagsChanged = pyqtSignal(list)  # Emits list of tag names
    
    def __init__(self, available_tags: List[Tag], parent=None):
        super().__init__(parent)
        self.available_tags = {tag.name: tag.color for tag in available_tags}
        self.selected_tags: List[str] = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Combo box for tag selection
        self.combo = QComboBox()
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo.setPlaceholderText("Select or type to add tag...")
        self.combo.addItems(sorted(self.available_tags.keys()))
        # Use activated signal for dropdown selection
        self.combo.activated.connect(self.on_tag_activated)
        # Connect editingFinished to handle Return key or focus loss
        self.combo.lineEdit().editingFinished.connect(self.on_edit_finished)
        layout.addWidget(self.combo)
        
        # Container for tag chips
        self.chips_container = QWidget()
        self.chips_layout = QHBoxLayout(self.chips_container)
        self.chips_layout.setContentsMargins(0, 4, 0, 0)
        self.chips_layout.setSpacing(4)
        self.chips_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.chips_container)
    
    def eventFilter(self, obj, event):
        """Handle Return key press in combo box."""
        if obj == self.combo.lineEdit():
            if event.type() == event.Type.KeyPress:
                print(f"DEBUG: Key pressed: {event.key()}")
                if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    print(f"DEBUG: Enter key detected, processing tag input")
                    self.process_tag_input()
                    event.accept()  # Mark event as handled
                    return True
        return super().eventFilter(obj, event)
    
    def on_edit_finished(self):
        """Handle when editing is finished (Return key or focus loss)."""
        self.process_tag_input()
    
    def on_tag_activated(self, index: int):
        """Handle tag selection from dropdown."""
        self.process_tag_input()
    
    def process_tag_input(self):
        """Process the current text in the combo box as a new tag."""
        text = self.combo.currentText().strip()
        if not text or text in self.selected_tags:
            self.combo.setCurrentIndex(-1)
            self.combo.clearEditText()
            return
        
        # Get or create tag color
        if text in self.available_tags:
            color = self.available_tags[text]
        else:
            color = random.choice(PRESET_COLORS)
            self.available_tags[text] = color
        
        # Add tag chip
        self.add_tag(text, color)
        
        # Clear combo box
        self.combo.setCurrentIndex(-1)
        self.combo.clearEditText()
    
    def add_tag(self, tag_name: str, color: str):
        """Add a tag chip to the display."""
        if tag_name in self.selected_tags:
            return
        
        self.selected_tags.append(tag_name)
        
        chip = TagChip(tag_name, color)
        chip.removed.connect(self.remove_tag)
        self.chips_layout.addWidget(chip)
        
        self.tagsChanged.emit(self.selected_tags)
    
    def remove_tag(self, tag_name: str):
        """Remove a tag chip."""
        if tag_name in self.selected_tags:
            self.selected_tags.remove(tag_name)
        
        # Remove chip widget
        for i in range(self.chips_layout.count()):
            widget = self.chips_layout.itemAt(i).widget()
            if isinstance(widget, TagChip) and widget.tag_name == tag_name:
                widget.deleteLater()
                break
        
        self.tagsChanged.emit(self.selected_tags)
    
    def get_selected_tags(self) -> List[str]:
        """Get list of selected tag names."""
        return self.selected_tags.copy()
    
    def set_tags(self, tag_names: List[str]):
        """Set the selected tags."""
        # Clear existing chips
        for i in reversed(range(self.chips_layout.count())):
            self.chips_layout.itemAt(i).widget().deleteLater()
        
        self.selected_tags.clear()
        
        # Add new chips
        for tag_name in tag_names:
            color = self.available_tags.get(tag_name, random.choice(PRESET_COLORS))
            self.add_tag(tag_name, color)
    
    def update_available_tags(self, tags: List[Tag]):
        """Update the list of available tags."""
        self.available_tags = {tag.name: tag.color for tag in tags}
        current_text = self.combo.currentText()
        self.combo.clear()
        self.combo.addItems(sorted(self.available_tags.keys()))
        self.combo.setCurrentText(current_text)


def get_or_create_tag_color(tag_name: str, existing_tags: dict) -> str:
    """Get color for a tag or create a random one.
    
    Args:
        tag_name: Name of the tag
        existing_tags: Dictionary of {tag_name: color}
        
    Returns:
        Hex color code
    """
    if tag_name in existing_tags:
        return existing_tags[tag_name]
    return random.choice(PRESET_COLORS)
