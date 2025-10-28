"""Conversion interface window."""

import tkinter as tk
from gui.components.base_window import BaseWindow


class ConverterWindow(BaseWindow):
    """Conversion interface window implementation."""
    
    def __init__(self, conversion_type: str = "keylog"):
        self.conversion_type = conversion_type
        super().__init__(title=f"ConvertKeylogApp - {conversion_type.title()} Converter", geometry="800x600")
    
    def setup_ui(self):
        """Setup converter window UI."""
        # TODO: Implement converter-specific UI
        pass
