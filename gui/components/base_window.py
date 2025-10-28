"""Base window class - foundation cho tất cả windows."""

import tkinter as tk
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseWindow(ABC):
    """Base window class với common functionality - giống TL patterns."""
    
    def __init__(self, window=None, title: str = "ConvertKeylogApp", geometry: str = "800x600"):
        if window is None:
            self.window = tk.Tk()
        else:
            self.window = window
            
        self.window.title(title)
        self.window.geometry(geometry)
        self.setup_common_styles()
    
    def setup_common_styles(self):
        """Setup common styles cho tất cả windows - giống TL theme."""
        # Common TL colors
        self.colors = {
            "bg_primary": "#F8F9FA",
            "bg_secondary": "#FFFFFF", 
            "header_primary": "#2E86AB",
            "header_secondary": "#1B5299",
            "accent": "#F18F01",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "error": "#F44336",
            "text_primary": "#333333",
            "text_light": "#666666",
            "text_white": "#FFFFFF"
        }
        
        # Set window background giống TL
        self.window.configure(bg=self.colors["bg_primary"])
        
        # Common font styles giống TL
        self.fonts = {
            "default": ("Arial", 10),
            "header": ("Arial", 14, "bold"),
            "title": ("Arial", 18, "bold"),
            "small": ("Arial", 8),
            "button": ("Arial", 9, "bold")
        }
    
    def create_label_frame(self, parent, title: str, color_scheme: str = "primary") -> tk.LabelFrame:
        """Tạo LabelFrame với styling giống TL."""
        color_map = {
            "primary": self.colors["header_primary"],
            "secondary": self.colors["header_secondary"],
            "accent": self.colors["accent"]
        }
        
        frame = tk.LabelFrame(
            parent, text=title,
            bg=self.colors["bg_secondary"],
            fg=color_map.get(color_scheme, self.colors["header_primary"]),
            font=self.fonts["default"] + ("bold",)
        )
        return frame
    
    def create_button(self, parent, text: str, command, bg_color: str = "primary", **kwargs) -> tk.Button:
        """Tạo button với styling giống TL."""
        color_map = {
            "primary": self.colors["header_primary"],
            "success": self.colors["success"],
            "warning": self.colors["warning"],
            "error": self.colors["error"]
        }
        
        button = tk.Button(
            parent, text=text, command=command,
            bg=color_map.get(bg_color, self.colors["header_primary"]),
            fg=self.colors["text_white"],
            font=self.fonts["button"],
            relief="flat",
            **kwargs
        )
        return button
    
    def show_info(self, title: str, message: str):
        """Hiển thị thông báo - giống TL."""
        messagebox.showinfo(title, message)
    
    def show_warning(self, title: str, message: str):
        """Hiển thị cảnh báo - giống TL."""
        messagebox.showwarning(title, message)
    
    def show_error(self, title: str, message: str):
        """Hiển thị lỗi - giống TL."""
        messagebox.showerror(title, message)
    
    @abstractmethod
    def setup_ui(self):
        """Setup user interface elements - implement trong subclass."""
        pass
    
    def run(self):
        """Start main event loop - giống TL."""
        self.window.mainloop()
    
    def close(self):
        """Close window - giống TL."""
        self.window.destroy()
    
    def center_window(self):
        """Center window on screen - giống TL."""
        self.window.eval('tk::PlaceWindow . center')
