"""Equation View Components - UI Layout Manager"""
import tkinter as tk
from tkinter import ttk

class EquationUIManager:
    """Quản lý layout và giao diện cho Equation View"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
        self.window = parent_view.window
        self.config = parent_view.config
    
    def setup_main_layout(self):
        """Thiết lập layout chính"""
        # Frame chính
        main_frame = tk.Frame(self.window, bg="#F5F5F5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Tiêu đề
        self._create_title(main_frame)
        
        # Khung thiết lập tham số
        control_frame = self._create_control_frame(main_frame)
        
        # Khung hướng dẫn
        guide_frame = self._create_guide_frame(main_frame)
        
        # Khung nhập liệu
        input_frame = self._create_input_frame(main_frame)
        
        # Khung kết quả mã hóa
        result_frame = self._create_result_frame(main_frame)
        
        # Khung kết quả nghiệm
        solution_frame = self._create_solution_frame(main_frame)
        
        # Khung kết quả tổng
        final_frame = self._create_final_frame(main_frame)
        
        # Khung nút chức năng
        button_frame = self._create_button_frame(main_frame)
        
        # Thông báo trạng thái
        status_label = self._create_status_label(main_frame)
        
        # Nút đóng và footer
        self._create_footer(main_frame)
        
        return {
            'main_frame': main_frame,
            'control_frame': control_frame,
            'guide_frame': guide_frame,
            'input_frame': input_frame,
            'result_frame': result_frame,
            'solution_frame': solution_frame,
            'final_frame': final_frame,
            'button_frame': button_frame,
            'status_label': status_label
        }
    
    def _create_title(self, parent):
        """Tạo tiêu đề"""
        title_label = tk.Label(
            parent,
            text="🧠 EQUATION MODE v2.0 - GIẢI HỆ PHƯƠNG TRÌNH",
            font=("Arial", 18, "bold"),
            bg="#F5F5F5",
            fg="#2E7D32"
        )
        title_label.pack(pady=(0, 15))
        return title_label
    
    def _create_control_frame(self, parent):
        """Tạo khung điều khiển tham số"""
        control_frame = tk.LabelFrame(
            parent,
            text="⚙️ THIẾ4T LẬP PHƯƠNG TRÌNH",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#1B5299",
            bd=2,
            relief="groove"
        )
        control_frame.pack(fill="x", pady=10, padx=10)
        
        self._setup_control_widgets(control_frame)
        return control_frame
    
    def _setup_control_widgets(self, control_frame):
        """Thiết lập các widget trong khung điều khiển"""
        # Dòng 1: Chọn số ẩn
        row1 = tk.Frame(control_frame, bg="#FFFFFF")
        row1.pack(fill="x", padx=15, pady=10)
        
        tk.Label(
            row1,
            text="Số ẩn:",
            font=("Arial", 10, "bold"),
            bg="#FFFFFF",
            fg="#333333",
            width=12
        ).pack(side="left")
        
        so_an_menu = ttk.Combobox(
            row1,
            textvariable=self.parent.so_an_var,
            values=["2", "3", "4"],
            state="readonly",
            width=15,
            font=("Arial", 10)
        )
        so_an_menu.pack(side="left", padx=5)
        so_an_menu.bind("<<ComboboxSelected>>", self.parent._on_so_an_changed)
        
        # Dòng 2: Chọn phiên bản
        row2 = tk.Frame(control_frame, bg="#FFFFFF")
        row2.pack(fill="x", padx=15, pady=10)
        
        tk.Label(
            row2,
            text="Phiên bản máy:",
            font=("Arial", 10, "bold"),
            bg="#FFFFFF",
            fg="#333333",
            width=12
        ).pack(side="left")
        
        phien_ban_menu = ttk.Combobox(
            row2,
            textvariable=self.parent.phien_ban_var,
            values=self.parent.phien_ban_list,
            state="readonly",
            width=15,
            font=("Arial", 10)
        )
        phien_ban_menu.pack(side="left", padx=5)
        phien_ban_menu.bind("<<ComboboxSelected>>", self.parent._on_phien_ban_changed)
        
        # Config status
        config_status = "Config: ✅ Loaded" if self.config else "Config: ⚠️ Fallback"
        tk.Label(
            row2,
            text=config_status,
            font=("Arial", 8),
            bg="#FFFFFF",
            fg="#666666"
        ).pack(side="right", padx=20)
    
    def _create_guide_frame(self, parent):
        """Tạo khung hướng dẫn"""
        guide_frame = tk.LabelFrame(
            parent,
            text="💡 HƯỚNG DẮN NHẬP LIỆU",
            font=("Arial", 10, "bold"),
            bg="#E3F2FD",
            fg="#1565C0",
            bd=1,
            relief="solid"
        )
        guide_frame.pack(fill="x", pady=5, padx=10)
        
        guide_text = (
            "• Hỗ trợ biểu thức: sqrt(5), sin(pi/2), 1/2, 2^3, log(10), v.v.\n"
            "• Nhập hệ số cách nhau bằng dấu phẩy\n"
            "• Ô trống sẽ tự động điền số 0"
        )
        
        guide_label = tk.Label(
            guide_frame,
            text=guide_text,
            font=("Arial", 9),
            bg="#E3F2FD",
            fg="#333333",
            justify="left"
        )
        guide_label.pack(padx=10, pady=8)
        
        return guide_frame
    
    def _create_input_frame(self, parent):
        """Tạo khung nhập liệu"""
        input_frame = tk.LabelFrame(
            parent,
            text="📝 NHẬP HỆ SỐ PHƯƠNG TRÌNH",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#1B5299",
            bd=2,
            relief="groove"
        )
        input_frame.pack(fill="x", pady=10, padx=10)
        return input_frame
    
    def _create_result_frame(self, parent):
        """Tạo khung kết quả mã hóa"""
        result_frame = tk.LabelFrame(
            parent,
            text="🔐 KẾT QUẢ MÃ HÓA",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#7B1FA2",
            bd=2,
            relief="groove"
        )
        result_frame.pack(fill="x", pady=10, padx=10)
        return result_frame
    
    def _create_solution_frame(self, parent):
        """Tạo khung kết quả nghiệm"""
        solution_frame = tk.LabelFrame(
            parent,
            text="🎯 KẾT QUẢ NGHIỆM",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#D35400",
            bd=2,
            relief="groove"
        )
        solution_frame.pack(fill="x", pady=10, padx=10)
        
        solution_entry = tk.Entry(
            solution_frame,
            width=80,
            font=("Arial", 10),
            justify="center"
        )
        solution_entry.pack(padx=15, pady=12, fill="x")
        solution_entry.insert(0, "Chưa có kết quả nghiệm")
        solution_entry.config(bg="#FFF9E6", fg="#FF6F00")
        
        return solution_frame, solution_entry
    
    def _create_final_frame(self, parent):
        """Tạo khung kết quả tổng"""
        final_frame = tk.LabelFrame(
            parent,
            text="📦 KẾT QUẢ TỔNG (CHO MÁY TÍNH)",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#2E7D32",
            bd=2,
            relief="groove"
        )
        final_frame.pack(fill="x", pady=10, padx=10)
        
        final_entry = tk.Entry(
            final_frame,
            width=80,
            font=("Courier New", 9),
            justify="center"
        )
        final_entry.pack(padx=15, pady=12, fill="x")
        
        # Hiển thị config info trong kết quả tổng
        config_info = "Config loaded successfully" if self.config else "Using fallback config"
        final_entry.insert(0, f"Equation Mode v2.0 - {config_info}")
        final_entry.config(bg="#F1F8E9")
        
        return final_frame, final_entry
    
    def _create_button_frame(self, parent):
        """Tạo khung nút chức năng"""
        button_frame = tk.Frame(parent, bg="#F5F5F5")
        button_frame.pack(fill="x", pady=20)
        return button_frame
    
    def _create_status_label(self, parent):
        """Tạo label trạng thái"""
        status_label = tk.Label(
            parent,
            text="🟢 Sẵn sàng nhập liệu và giải hệ phương trình",
            font=("Arial", 10, "bold"),
            bg="#F5F5F5",
            fg="#2E7D32"
        )
        status_label.pack(pady=10)
        return status_label
    
    def _create_footer(self, parent):
        """Tạo footer và nút đóng"""
        # Nút đóng
        close_btn = tk.Button(
            parent,
            text="Đóng",
            command=self.window.destroy,
            bg="#F44336",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            height=1
        )
        close_btn.pack(pady=10)
        
        # Footer
        footer_label = tk.Label(
            parent,
            text="Phiên bản: v2.0 Giải nghiệm thực • Hỗ trợ biểu thức phức tạp • Config-driven",
            font=("Arial", 8),
            bg="#F5F5F5",
            fg="#666666"
        )
        footer_label.pack(side="bottom", pady=5)
        
        return close_btn, footer_label