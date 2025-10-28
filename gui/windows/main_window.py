"""Main application window."""

import tkinter as tk
from tkinter import messagebox
from gui.components.base_window import BaseWindow
from gui.components.file_selector import FileSelector
from gui.components.progress_bar import ProgressBar
from gui.components.result_display import ResultDisplay
from gui.components.status_bar import StatusBar


class MainWindow(BaseWindow):
    """Main application window implementation."""
    
    def __init__(self):
        super().__init__(title="ConvertKeylogApp - Main", geometry="1000x700")
    
    def setup_ui(self):
        """Setup main window UI components."""
        # TODO: Implement main window UI
        # Will include:
        # - Menu bar
        # - File selector
        # - Conversion options
        # - Progress tracking
        # - Result display
        # - Status bar
        pass
    
    def on_convert_clicked(self):
        """Handle convert button click."""
        # TODO: Implement conversion logic integration
        pass
    
    def on_file_selected(self, file_path):
        """Handle file selection."""
        # TODO: Implement file selection handling
        pass
