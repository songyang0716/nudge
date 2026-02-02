"""Dialog for adding a new study item."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)
from sqlalchemy.orm import Session

from nudge.core.models import Tag
from nudge.ui.widgets.tag_input import TagInputWidget


class AddItemDialog(QDialog):
    """Dialog for adding a new study item."""
    
    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.session = session
        self.item_name = ""
        self.selected_tags = []
        
        self.setup_ui()
        self.load_tags()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Add Study Item")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Item name input
        layout.addWidget(QLabel("Item Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter item name...")
        layout.addWidget(self.name_input)
        
        # Tag input
        layout.addWidget(QLabel("Tags:"))
        self.tag_widget = TagInputWidget([])
        layout.addWidget(self.tag_widget)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_tags(self):
        """Load existing tags from database."""
        tags = self.session.query(Tag).all()
        self.tag_widget.update_available_tags(tags)
    
    def accept(self):
        """Handle OK button click."""
        # First, ensure any pending tag input is processed by triggering editingFinished
        if self.tag_widget.combo.lineEdit().text().strip():
            self.tag_widget.on_edit_finished()
        
        self.item_name = self.name_input.text().strip()
        self.selected_tags = self.tag_widget.get_selected_tags()
        
        if not self.item_name:
            return  # Don't accept empty name
        
        super().accept()
    
    def get_item_data(self):
        """Get the entered item data.
        
        Returns:
            Tuple of (item_name, tag_names)
        """
        return self.item_name, self.selected_tags
