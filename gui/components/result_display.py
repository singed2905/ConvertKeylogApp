"""Result display component - giống TL result areas."""

import tkinter as tk
from tkinter import scrolledtext
from typing import Any, Dict, List


class ResultDisplay:
    """Result display widget component - giống TL."""
    
    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.setup_ui(**kwargs)
    
    def setup_ui(self, **kwargs):
        """Setup result display UI - giống TL."""
        # Main result frame giống TL
        self.frame = tk.LabelFrame(
            self.parent, text="🎉 Kết quả xử lý",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        
        # Result text area giống TL
        self.result_text = tk.Text(
            self.frame,
            height=kwargs.get('height', 8),
            width=kwargs.get('width', 80),
            font=("Consolas", 10),
            wrap=tk.WORD,
            bg="#F0F8FF",
            fg="#333",
            relief="solid",
            bd=1,
            padx=5, pady=5
        )
        
        # Scrollbar giống TL
        scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.result_text.yview)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # Pack elements
        self.result_text.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        # Status bar giống TL
        self.status_frame = tk.Frame(self.frame, bg="#FFFFFF")
        self.status_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Chưa có kết quả")
        self.status_label = tk.Label(
            self.status_frame, textvariable=self.status_var,
            bg="#FFFFFF", fg="#666", font=("Arial", 9)
        )
        self.status_label.pack(side="left")
    
    def display_result(self, result: Any, clear_previous: bool = True):
        """Hiển thị kết quả - giống TL."""
        if clear_previous:
            self.clear_results()
        
        # Enable editing to insert text
        self.result_text.config(state='normal')
        
        if isinstance(result, str):
            self.result_text.insert(tk.END, result)
        elif isinstance(result, (list, dict)):
            self.result_text.insert(tk.END, str(result))
        else:
            self.result_text.insert(tk.END, str(result))
        
        # Disable editing
        self.result_text.config(state='disabled')
        
        # Cập nhật status
        self.status_var.set(f"Kết quả đã cập nhật - {len(str(result))} ký tự")
    
    def clear_results(self):
        """Xóa kết quả - giống TL."""
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state='disabled')
        self.status_var.set("Kết quả đã được xóa")
    
    def append_result(self, result: Any):
        """Thêm kết quả - giống TL."""
        self.display_result("\n" + str(result), clear_previous=False)
    
    def get_results(self) -> str:
        """Lấy nội dung kết quả."""
        return self.result_text.get(1.0, tk.END)
    
    def pack(self, **kwargs):
        """Pack the result frame."""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the result frame."""
        self.frame.grid(**kwargs)
