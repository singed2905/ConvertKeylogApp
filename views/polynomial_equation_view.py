import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

from services.polynomial.polynomial_service import PolynomialService
from services.polynomial.polynomial_template_generator import PolynomialTemplateGenerator
from views.polynomial_excel_ui import PolynomialExcelUI

class PolynomialEquationView:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Polynomial Equation Mode v2.1 - Fully Functional! 💪")
        self.window.geometry("900x1200")
        self.window.configure(bg="#F0F8FF")
        
        # Make window resizable
        self.window.resizable(True, True)
        self.window.minsize(800, 600)

        # Configure grid weights for responsive behavior
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Config và state management
        self.config = config or {}
        self.manual_data_entered = False
        self.has_result = False
        self.is_imported_mode = False

        # Variables
        self.bac_phuong_trinh_var = tk.StringVar(value="2")
        self.phien_ban_var = tk.StringVar()
        self.coefficient_entries = []
        self.root_entries = []

        # Load configuration
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var.set(self.phien_ban_list[0] if self.phien_ban_list else "fx799")
        
        # Initialize polynomial service
        self.polynomial_service = None
        self._initialize_service()

        # Setup UI
        self._setup_ui()
        self._update_input_fields()
        self._update_button_visibility()
        
        # Bind input detection
        self.window.after(1000, self._setup_input_bindings)

    # ... keep rest of original content unchanged ...

    def _create_quick_actions(self, parent):
        """Tạo thanh hành động nhanh"""
        quick_frame = tk.Frame(parent, bg="#F0F8FF")
        quick_frame.pack(fill="x", pady=5)
        
        tk.Button(quick_frame, text="📝 Tạo Template", 
                 command=self._create_template,
                 bg="#1565C0", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Button(quick_frame, text="📁 Import Excel", 
                 command=self._import_excel,
                 bg="#FF9800", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Button(quick_frame, text="🔥 Xử lý File Excel", 
                 command=lambda: PolynomialExcelUI.run_batch(self.window, lambda: self.bac_phuong_trinh_var.get(), lambda: self.phien_ban_var.get()),
                 bg="#2E7D32", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)

    def _import_excel(self):
        """Import file Excel"""
        # Chuyển sang batch helper để xử lý trực tiếp - giữ lại thông báo hướng dẫn
        messagebox.showinfo("Import Excel", "Dùng nút '🔥 Xử lý File Excel' để chọn file Input và xuất kết quả.")
