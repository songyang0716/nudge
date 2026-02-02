"""System tray service for background operation."""
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon
from sqlalchemy.orm import Session

from nudge.ui.dialogs.add_item_dialog import AddItemDialog


class TrayService:
    """System tray icon and menu."""
    
    def __init__(self, app, main_window, session: Session):
        self.app = app
        self.main_window = main_window
        self.session = session
        
        self.tray_icon = QSystemTrayIcon(app)
        self.setup_tray()
    
    def setup_tray(self):
        """Set up system tray icon and menu."""
        # Create menu
        menu = QMenu()
        
        # Show/Hide window action
        self.show_action = QAction("Show Window", self.app)
        self.show_action.triggered.connect(self.toggle_window)
        menu.addAction(self.show_action)
        
        menu.addSeparator()
        
        # Quick add action
        quick_add_action = QAction("Quick Add Item", self.app)
        quick_add_action.triggered.connect(self.quick_add)
        menu.addAction(quick_add_action)
        
        menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit", self.app)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        
        # Set icon (using a simple placeholder text-based icon)
        # In production, you'd want to use an actual icon file
        self.tray_icon.setToolTip("Nudge - Study Reminder")
        
        # Double-click to show window
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        self.tray_icon.show()
    
    def toggle_window(self):
        """Show or hide the main window."""
        if self.main_window.isVisible():
            self.main_window.hide()
            self.show_action.setText("Show Window")
        else:
            self.main_window.show()
            self.main_window.activateWindow()
            self.main_window.raise_()
            self.show_action.setText("Hide Window")
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_window()
    
    def quick_add(self):
        """Show quick add dialog."""
        dialog = AddItemDialog(self.session, self.main_window)
        if dialog.exec():
            item_name, tag_names = dialog.get_item_data()
            
            # Create item (same logic as main window)
            from nudge.core.models import Item, Tag
            from nudge.core.scheduler import create_review_schedule
            
            item = Item(name=item_name)
            
            for tag_name in tag_names:
                tag = self.session.query(Tag).filter_by(name=tag_name).first()
                if not tag:
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
            
            create_review_schedule(self.session, item)
            
            # Refresh main window if visible
            if self.main_window.isVisible():
                self.main_window.refresh_data()
            
            self.tray_icon.showMessage(
                "Item Added",
                f"'{item_name}' has been added to your study list.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
    
    def quit_app(self):
        """Quit the application."""
        self.tray_icon.hide()
        self.app.quit()
