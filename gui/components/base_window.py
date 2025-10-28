"""Base window class with common features."""

import tkinter as tk
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseWindow(ABC):
    """Base window class with common functionality."""
    
    def __init__(self, title: str = "ConvertKeylogApp", geometry: str = "800x600"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(geometry)
        self.setup_styles()
        self.setup_ui()
    
    def setup_styles(self):
        """Setup window styles and themes."""
        # TODO: Implement styling
        pass
    
    @abstractmethod
    def setup_ui(self):
        """Setup user interface elements."""
        pass
    
    def run(self):
        """Start the main event loop."""
        self.root.mainloop()
    
    def close(self):
        """Close the window."""
        self.root.destroy()
