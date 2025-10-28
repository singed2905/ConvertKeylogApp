"""File selection component."""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Callable, Optional, List


class FileSelector:
    """File selection widget component."""
    
    def __init__(self, parent, on_file_selected: Optional[Callable] = None):
        self.parent = parent
        self.on_file_selected = on_file_selected
        self.selected_file: Optional[Path] = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup file selector UI."""
        # TODO: Implement file selector UI
        pass
    
    def select_file(self, file_types: List[tuple] = None):
        """Open file selection dialog."""
        # TODO: Implement file selection logic
        pass
