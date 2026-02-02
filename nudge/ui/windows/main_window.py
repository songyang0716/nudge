"""Main application window."""
from datetime import datetime
from typing import List

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy.orm import Session

from nudge.core.database import get_database
from nudge.core.models import Item, Tag
from nudge.core.scheduler import get_interval_name, mark_as_reviewed
from nudge.ui.dialogs.add_item_dialog import AddItemDialog


class ItemTableModel(QAbstractTableModel):
    """Table model for displaying study items."""
    
    COLUMNS = ["Name", "Tags", "Date Added", "Next Review", "Interval"]
    
    def __init__(self, session: Session):
        super().__init__()
        self.session = session
        self.items: List[Item] = []
        self.load_items()
    
    def load_items(self):
        """Load items from database."""
        self.beginResetModel()
        self.items = (
            self.session.query(Item)
            .join(Item.review_schedule)
            .order_by(Item.review_schedule.property.mapper.class_.next_review_date)
            .all()
        )
        self.endResetModel()
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.items)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.COLUMNS)
    
    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        item = self.items[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:  # Name
                return item.name
            elif col == 1:  # Tags
                return ", ".join(tag.name for tag in item.tags)
            elif col == 2:  # Date Added
                return item.date_added.strftime("%Y-%m-%d")
            elif col == 3:  # Next Review
                if item.review_schedule:
                    return item.review_schedule.next_review_date.strftime("%Y-%m-%d")
                return ""
            elif col == 4:  # Interval
                if item.review_schedule:
                    return get_interval_name(item.review_schedule.current_interval_index)
                return ""
        
        elif role == Qt.ItemDataRole.BackgroundRole:
            # Highlight overdue items
            if col == 3 and item.review_schedule:
                if item.review_schedule.next_review_date.date() < datetime.now().date():
                    return QColor("#FFE5E5")  # Light red
                elif item.review_schedule.next_review_date.date() == datetime.now().date():
                    return QColor("#FFF8E5")  # Light yellow
        
        elif role == Qt.ItemDataRole.UserRole:
            # Store item ID for actions
            return item.id
        
        return None
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.COLUMNS[section]
        return None
    
    def get_item_at_row(self, row: int) -> Item | None:
        """Get item at specific row."""
        if 0 <= row < len(self.items):
            return self.items[row]
        return None
    
    def sort_items(self, column: int, ascending: bool = True):
        """Sort items by the specified column."""
        reverse = not ascending
        
        if column == 0:  # Name
            self.items.sort(key=lambda x: x.name.lower(), reverse=reverse)
        elif column == 1:  # Tags
            self.items.sort(key=lambda x: ", ".join(tag.name for tag in x.tags).lower(), reverse=reverse)
        elif column == 2:  # Date Added
            self.items.sort(key=lambda x: x.date_added, reverse=reverse)
        elif column == 3:  # Next Review
            self.items.sort(key=lambda x: x.review_schedule.next_review_date if x.review_schedule else datetime.max, reverse=reverse)
        elif column == 4:  # Interval
            self.items.sort(key=lambda x: x.review_schedule.current_interval_index if x.review_schedule else -1, reverse=reverse)
        
        self.layoutChanged.emit()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.db = get_database()
        self.session = self.db.get_session()
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Nudge - Study Reminder")
        self.setMinimumSize(900, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search items...")
        self.search_box.textChanged.connect(self.on_search)
        toolbar.addWidget(self.search_box)
        
        # Add button
        self.add_btn = QPushButton("Add Item")
        self.add_btn.clicked.connect(self.add_item)
        toolbar.addWidget(self.add_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_data)
        toolbar.addWidget(self.refresh_btn)
        
        layout.addLayout(toolbar)
        
        # Table view
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().sortIndicatorChanged.connect(self.on_sort_changed)
        self.table.doubleClicked.connect(self.on_table_double_click)
        
        self.model = ItemTableModel(self.session)
        self.table.setModel(self.model)
        
        layout.addWidget(self.table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.mark_reviewed_btn = QPushButton("Mark as Reviewed")
        self.mark_reviewed_btn.clicked.connect(self.mark_as_reviewed)
        action_layout.addWidget(self.mark_reviewed_btn)
        
        self.delete_btn = QPushButton("Delete Item")
        self.delete_btn.clicked.connect(self.delete_item)
        action_layout.addWidget(self.delete_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
    
    def load_data(self):
        """Load data into the table."""
        self.model.load_items()
    
    def refresh_data(self):
        """Refresh the table data."""
        self.session.expire_all()
        self.load_data()
    
    def on_search(self, text: str):
        """Handle search text change."""
        # Simple filtering - reload with filter
        text = text.lower().strip()
        if not text:
            self.load_data()
            return
        
        self.model.beginResetModel()
        all_items = self.session.query(Item).all()
        self.model.items = [
            item for item in all_items
            if text in item.name.lower() or
            any(text in tag.name.lower() for tag in item.tags)
        ]
        self.model.endResetModel()
    
    def add_item(self):
        """Show dialog to add new item."""
        dialog = AddItemDialog(self.session, self)
        if dialog.exec():
            item_name, tag_names = dialog.get_item_data()
            
            # Create item
            from nudge.core.models import Item, Tag
            from nudge.core.scheduler import create_review_schedule
            
            item = Item(name=item_name)
            
            # Add tags
            for tag_name in tag_names:
                tag = self.session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
                    # Create new tag with random color
                    from nudge.ui.widgets.tag_input import get_or_create_tag_color
                    existing_tags = {t.name: t.color for t in self.session.query(Tag).all()}
                    color = get_or_create_tag_color(tag_name, existing_tags)
                    tag = Tag(name=tag_name, color=color)
                    self.session.add(tag)
                    self.session.flush()  # Flush to ensure tag gets an ID
                item.tags.append(tag)
            
            self.session.add(item)
            self.session.flush()  # Flush to ensure item gets an ID before review schedule
            self.session.commit()
            
            # Create review schedule
            create_review_schedule(self.session, item)
            
            self.refresh_data()
    
    def mark_as_reviewed(self):
        """Mark selected item as reviewed."""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select an item to mark as reviewed.")
            return
        
        row = selected[0].row()
        item = self.model.get_item_at_row(row)
        
        if item:
            try:
                mark_as_reviewed(self.session, item.id)
                self.refresh_data()
                QMessageBox.information(
                    self, "Success",
                    f"Item '{item.name}' marked as reviewed!\nNext review: {item.review_schedule.next_review_date.strftime('%Y-%m-%d')}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to mark item as reviewed: {str(e)}")
    
    def delete_item(self):
        """Delete selected item."""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select an item to delete.")
            return
        
        row = selected[0].row()
        item = self.model.get_item_at_row(row)
        
        if item:
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Delete item '{item.name}'?\nThis cannot be undone.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.session.delete(item)
                self.session.commit()
                self.refresh_data()
    
    def on_sort_changed(self, logicalIndex, order):
        """Handle sort order change."""
        self.model.sort_items(logicalIndex, order == Qt.SortOrder.AscendingOrder)
    
    def on_table_double_click(self, index: QModelIndex):
        """Handle double-click on table row."""
        # Could open edit dialog in the future
        pass
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Don't actually close, just hide
        event.ignore()
        self.hide()
