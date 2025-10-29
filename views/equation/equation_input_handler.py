"""Equation View Components - UI Components for input fields"""
import tkinter as tk
from tkinter import ttk

class EquationInputHandler:
    """Xử lý các ô nhập liệu cho phương trình"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
        self.input_entries = []
    
    def create_input_fields(self, container, so_an):
        """Tạo các ô nhập liệu dựa trên số ẩn"""
        try:
            # Xóa các widget cũ
            for widget in container.winfo_children():
                widget.destroy()
            
            self.input_entries = []
            
            # Tạo label hướng dẫn
            tk.Label(
                container,
                text=f"Nhập {so_an + 1} hệ số cho mỗi phương trình (cách nhau bằng dấu phẩy):",
                font=("Arial", 9, "bold"),
                bg="#FFFFFF",
                fg="#333333"
            ).pack(anchor="w", padx=15, pady=8)
            
            # Tạo các ô nhập liệu
            labels = self._get_input_labels(so_an)
            for i, label_text in enumerate(labels):
                row_frame = tk.Frame(container, bg="#FFFFFF")
                row_frame.pack(fill="x", padx=15, pady=6)
                
                tk.Label(
                    row_frame,
                    text=label_text,
                    font=("Arial", 9),
                    bg="#FFFFFF",
                    fg="#333333",
                    width=35
                ).pack(side="left")
                
                entry = tk.Entry(row_frame, width=45, font=("Arial", 9))
                entry.pack(side="left", padx=5, fill="x", expand=True)
                entry.bind('<KeyRelease>', self.parent._on_manual_input)
                self.input_entries.append(entry)
        
        except Exception as e:
            print(f"Lỗi khi tạo các ô nhập liệu: {e}")
    
    def _get_input_labels(self, so_an):
        """Lấy danh sách label cho các ô nhập liệu"""
        config = {
            2: [
                "Phương trình 1 (a₁₁, a₁₂, c₁):",
                "Phương trình 2 (a₂₁, a₂₂, c₂):"
            ],
            3: [
                "Phương trình 1 (a₁₁, a₁₂, a₁₃, c₁):",
                "Phương trình 2 (a₂₁, a₂₂, a₂₃, c₂):",
                "Phương trình 3 (a₃₁, a₃₂, a₃₃, c₃):"
            ],
            4: [
                "Phương trình 1 (a₁₁, a₁₂, a₁₃, a₁₄, c₁):",
                "Phương trình 2 (a₂₁, a₂₂, a₂₃, a₂₄, c₂):",
                "Phương trình 3 (a₃₁, a₃₂, a₃₃, a₃₄, c₃):",
                "Phương trình 4 (a₄₁, a₄₂, a₄₃, a₄₄, c₄):"
            ]
        }
        return config.get(so_an, config[2])
    
    def get_input_data(self):
        """Lấy dữ liệu từ các ô nhập liệu"""
        data = []
        for entry in self.input_entries:
            data.append(entry.get().strip())
        return data
    
    def clear_inputs(self):
        """Xóa toàn bộ dữ liệu nhập"""
        for entry in self.input_entries:
            entry.delete(0, tk.END)
    
    def set_inputs(self, data_list):
        """Thiết lập dữ liệu cho các ô nhập liệu"""
        for i, entry in enumerate(self.input_entries):
            if i < len(data_list):
                entry.delete(0, tk.END)
                entry.insert(0, str(data_list[i]))
    
    def lock_inputs(self):
        """Khóa các ô nhập liệu"""
        for entry in self.input_entries:
            entry.config(state='disabled', bg='#E0E0E0')
    
    def unlock_inputs(self):
        """Mở khóa các ô nhập liệu"""
        for entry in self.input_entries:
            entry.config(state='normal', bg='white')