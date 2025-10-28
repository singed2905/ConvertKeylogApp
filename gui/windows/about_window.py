"""About dialog window."""

import tkinter as tk
from gui.components.base_window import BaseWindow


class AboutWindow(BaseWindow):
    """About dialog window implementation."""
    
    def __init__(self):
        super().__init__(title="About ConvertKeylogApp", geometry="400x300")
    
    def setup_ui(self):
        """Setup about window UI."""
        # TODO: Implement about window UI
        # Will include:
        # - Application info
        # - Version information
        # - Author details
        # - License information
        pass
