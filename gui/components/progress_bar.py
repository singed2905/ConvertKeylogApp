"""Progress tracking component - giống TL progress displays."""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class ProgressBar:
    """Progress bar widget component - giống TL."""
    
    def __init__(self, parent, maximum: int = 100, **kwargs):
        self.parent = parent
        self.maximum = maximum
        self.current_value = 0
        self.setup_ui(**kwargs)
    
    def setup_ui(self, **kwargs):
        """Setup progress bar UI - giống TL."""
        self.frame = tk.Frame(self.parent, bg="#FFFFFF")
        
        # Progress bar giống TL
        self.progress = ttk.Progressbar(
            self.frame, maximum=self.maximum, mode='determinate',
            style="TProgressbar"
        )
        self.progress.pack(fill="x", padx=5, pady=5)
        
        # Status text giống TL
        self.status_var = tk.StringVar(value="Sẵn sàng...")
        self.status_label = tk.Label(
            self.frame, textvariable=self.status_var,
            bg="#FFFFFF", fg="#666", font=("Arial", 9)
        )
        self.status_label.pack(pady=(0, 5))
    
    def update_progress(self, value: int, message: str = ""):
        """Cập nhật progress bar - giống TL."""
        self.current_value = min(value, self.maximum)
        self.progress['value'] = self.current_value
        
        if message:
            self.status_var.set(message)
            
        # Force update giống TL
        self.parent.update_idletasks()
    
    def reset(self):
        """Reset progress bar - giống TL."""
        self.current_value = 0
        self.progress['value'] = 0
        self.status_var.set("Sẵn sàng...")
    
    def set_indeterminate(self):
        """Set to indeterminate mode - giống TL."""
        self.progress.config(mode='indeterminate')
        self.progress.start()
    
    def stop_indeterminate(self):
        """Stop indeterminate mode - giống TL."""
        self.progress.stop()
        self.progress.config(mode='determinate')
    
    def pack(self, **kwargs):
        """Pack the progress frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the progress frame."""
        self.frame.grid(**kwargs)
