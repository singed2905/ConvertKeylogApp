"""Equation window - tương tự EquationView của TL."""

import tkinter as tk
from tkinter import messagebox, ttk
import json
import os


class EquationWindow:
    """Equation Mode window implementation - giống TL EquationView."""
    
    def __init__(self, window):
        self.window = window
        
        # Khởi tạo cửa sổ giống TL
        self.window.title("Equation Mode")
        self.window.geometry("900x600")
        self.window.configure(bg="#F5F5F5")

        # Biến giống TL
        self._initialize_variables()
        
        # Tạo giao diện giống TL
        self._create_header()
        self._setup_ui()
        self._setup_bindings()
        
        # Khởi động
        self._update_equation_options()

    def _initialize_variables(self):
        """Khởi tạo biến - giống TL"""
        self.so_an_var = tk.StringVar(value="2")
        self.phien_ban_var = tk.StringVar(value="fx799")
        self.phuong_phap_var = tk.StringVar(value="Theo phương trình")
        
        # Load phiên bản
        self.phien_ban_list = ["fx799", "fx880"]
        
        # Trạng thái
        self.imported_data = False
        self.manual_data_entered = False

    def _create_header(self):
        """Tạo header giống TL"""
        COLORS = {"primary": "#3F51B5", "accent": "#FF9800", "text": "#FFFFFF"}
        
        # Header frame
        header_frame = tk.Frame(self.window, bg=COLORS["primary"], height=70)
        header_frame.pack(fill="x", padx=10, pady=5)
        header_frame.pack_propagate(False)
        
        # Logo và title
        title_frame = tk.Frame(header_frame, bg=COLORS["primary"])
        title_frame.pack(side="left", fill="y", padx=15, pady=10)
        
        tk.Label(title_frame, text="🗺", font=("Arial", 18),
                bg=COLORS["primary"], fg=COLORS["text"]).pack(side="left")
        tk.Label(title_frame, text="Equation Mode", font=("Arial", 16, "bold"),
                bg=COLORS["primary"], fg=COLORS["text"]).pack(side="left", padx=(5, 0))
        
        # Controls frame
        controls_frame = tk.Frame(header_frame, bg=COLORS["primary"])
        controls_frame.pack(side="right", fill="y", padx=15, pady=10)
        
        tk.Label(controls_frame, text="Số ẩn:", bg=COLORS["primary"], 
                fg=COLORS["text"], font=("Arial", 9)).pack(side="left")
        tk.OptionMenu(controls_frame, self.so_an_var, "2", "3", "4").pack(side="left", padx=5)
        
        tk.Label(controls_frame, text="Phiên bản:", bg=COLORS["primary"],
                fg=COLORS["text"], font=("Arial", 9)).pack(side="left", padx=(10, 0))
        tk.OptionMenu(controls_frame, self.phien_ban_var, *self.phien_ban_list).pack(side="left", padx=5)

    def _setup_ui(self):
        """Setup giao diện chính - giống TL"""
        self.main_frame = tk.Frame(self.window, bg="#F5F5F5")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Notebook for tabs giống TL
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab manual input giống TL
        self.manual_frame = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.manual_frame, text="✍️ Nhập thủ công")
        
        # Tab import Excel giống TL
        self.import_frame = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.import_frame, text="📁 Import Excel")
        
        self._setup_manual_tab()
        self._setup_import_tab()
        self._setup_result_area()

    def _setup_manual_tab(self):
        """Setup tab nhập thủ công - giống TL"""
        # Phương pháp nhập giống TL
        method_frame = tk.LabelFrame(self.manual_frame, text="Phương pháp nhập", bg="#FFFFFF")
        method_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Radiobutton(method_frame, text="Theo phương trình", variable=self.phuong_phap_var,
                      value="Theo phương trình", bg="#FFFFFF").pack(side="left", padx=10)
        tk.Radiobutton(method_frame, text="Theo hệ số", variable=self.phuong_phap_var,
                      value="Theo hệ số", bg="#FFFFFF").pack(side="left", padx=10)
        
        # Nhập phương trình giống TL
        input_frame = tk.LabelFrame(self.manual_frame, text="Nhập hệ phương trình", bg="#FFFFFF")
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Entry boxes cho hệ 2, 3, 4 ẩn
        self.equation_entries = {}
        for i in range(1, 5):
            tk.Label(input_frame, text=f"Phương trình {i}:", bg="#FFFFFF").grid(row=i-1, column=0, sticky="w", padx=5, pady=2)
            entry = tk.Entry(input_frame, width=50, font=("Arial", 10))
            entry.grid(row=i-1, column=1, padx=5, pady=2, sticky="ew")
            self.equation_entries[f"pt{i}"] = entry
        
        input_frame.columnconfigure(1, weight=1)

    def _setup_import_tab(self):
        """Setup tab import Excel - giống TL"""
        # File selection giống TL
        file_frame = tk.LabelFrame(self.import_frame, text="Chọn file Excel", bg="#FFFFFF")
        file_frame.pack(fill="x", padx=10, pady=10)
        
        self.file_path_var = tk.StringVar(value="Chưa chọn file")
        tk.Label(file_frame, textvariable=self.file_path_var, bg="#FFFFFF",
                font=("Arial", 9), fg="#666").pack(side="left", padx=10, pady=5)
        
        tk.Button(file_frame, text="📁 Chọn file", command=self._select_file,
                 bg="#2196F3", fg="white", font=("Arial", 9)).pack(side="right", padx=10, pady=5)
        
        # Preview data giống TL
        preview_frame = tk.LabelFrame(self.import_frame, text="Xem trước dữ liệu", bg="#FFFFFF")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.preview_text = tk.Text(preview_frame, height=10, bg="#F8F9FA", 
                                   font=("Consolas", 9), state="disabled")
        self.preview_text.pack(fill="both", expand=True, padx=5, pady=5)

    def _setup_result_area(self):
        """Setup vùng kết quả - giống TL"""
        result_frame = tk.LabelFrame(self.main_frame, text="🎉 Kết quả xử lý", bg="#FFFFFF")
        result_frame.pack(fill="x", padx=0, pady=(10, 0))
        
        # Text area cho kết quả giống TL
        self.result_text = tk.Text(result_frame, height=5, bg="#F0F8FF",
                                  font=("Consolas", 10), wrap=tk.WORD)
        self.result_text.pack(fill="x", padx=10, pady=10)
        
        # Buttons giống TL
        button_frame = tk.Frame(result_frame, bg="#FFFFFF")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Button(button_frame, text="🚀 Thực thi", command=self._execute,
                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(button_frame, text="💾 Xuất kết quả", command=self._export_result,
                 bg="#FF9800", fg="white", font=("Arial", 10)).pack(side="left", padx=5)
        tk.Button(button_frame, text="🗑️ Xóa kết quả", command=self._clear_result,
                 bg="#F44336", fg="white", font=("Arial", 10)).pack(side="left", padx=5)

    def _setup_bindings(self):
        """Setup event bindings - giống TL"""
        self.so_an_var.trace_add("write", self._on_so_an_changed)
        self.phien_ban_var.trace_add("write", self._on_version_changed)
        self.phuong_phap_var.trace_add("write", self._on_method_changed)

    def _update_equation_options(self):
        """Cập nhật tùy chọn phương trình - giống TL"""
        pass

    # Placeholder methods - giống TL structure
    def _on_so_an_changed(self, *args): pass
    def _on_version_changed(self, *args): pass
    def _on_method_changed(self, *args): pass
    def _select_file(self): messagebox.showinfo("File", "Chọn file Excel sẽ được implement")
    def _execute(self): messagebox.showinfo("Thực thi", "Giải hệ phương trình sẽ được implement")
    def _export_result(self): messagebox.showinfo("Xuất", "Xuất kết quả sẽ được implement")
    def _clear_result(self): 
        self.result_text.delete(1.0, tk.END)
        messagebox.showinfo("Xóa", "Kết quả đã bị xóa")