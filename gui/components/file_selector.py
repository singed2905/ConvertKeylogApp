"""File selection component - giống TL file dialogs."""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Callable, Optional, List


class FileSelector:
    """File selection widget component - giống TL."""
    
    def __init__(self, parent, on_file_selected: Optional[Callable] = None, **kwargs):
        self.parent = parent
        self.on_file_selected = on_file_selected
        self.selected_file: Optional[Path] = None
        
        # Default file types giống TL
        self.default_file_types = [
            ("Excel files", "*.xlsx"),
            ("Excel files (old)", "*.xls"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        
        self.setup_ui(**kwargs)
    
    def setup_ui(self, **kwargs):
        """Setup file selector UI - giống TL."""
        self.frame = tk.Frame(self.parent, bg="#FFFFFF")
        
        # File path display giống TL
        self.file_var = tk.StringVar(value="Chưa chọn file")
        self.file_label = tk.Label(
            self.frame, textvariable=self.file_var,
            bg="#FFFFFF", fg="#666", font=("Arial", 9),
            anchor="w", relief="sunken", bd=1
        )
        self.file_label.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Browse button giống TL
        self.browse_btn = tk.Button(
            self.frame, text="📁 Chọn...",
            command=self.select_file,
            bg="#2196F3", fg="white", font=("Arial", 9),
            relief="flat"
        )
        self.browse_btn.pack(side="right")
    
    def select_file(self, file_types: List[tuple] = None):
        """Mở file selection dialog - giống TL."""
        if file_types is None:
            file_types = self.default_file_types
        
        try:
            file_path = filedialog.askopenfilename(
                title="Chọn file dữ liệu",
                filetypes=file_types,
                initialdir="."
            )
            
            if file_path:
                self.selected_file = Path(file_path)
                self.file_var.set(self.selected_file.name)
                
                if self.on_file_selected:
                    self.on_file_selected(self.selected_file)
                    
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi chọn file:\n{str(e)}")
    
    def clear_selection(self):
        """Xóa lựa chọn file - giống TL."""
        self.selected_file = None
        self.file_var.set("Chưa chọn file")
    
    def get_file_path(self) -> Optional[Path]:
        """Lấy đường dẫn file đã chọn."""
        return self.selected_file
    
    def pack(self, **kwargs):
        """Pack the file selector frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the file selector frame."""
        self.frame.grid(**kwargs)
