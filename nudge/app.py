"""Application initialization and setup."""
import sys

from PyQt6.QtWidgets import QApplication

from nudge.core.database import get_database
from nudge.services.tray_service import TrayService
from nudge.ui.windows.main_window import MainWindow


class NudgeApp:
    """Main application class."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Nudge")
        self.app.setOrganizationName("Nudge")
        
        # Keep app running when windows are closed
        self.app.setQuitOnLastWindowClosed(False)
        
        # Initialize database
        self.db = get_database()
        self.session = self.db.get_session()
        
        # Create main window
        self.main_window = MainWindow()
        
        # Create system tray
        self.tray = TrayService(self.app, self.main_window, self.session)
        
        # Show main window on first launch
        self.main_window.show()
    
    def run(self):
        """Run the application."""
        return self.app.exec()
