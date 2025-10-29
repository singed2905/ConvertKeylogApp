"""Geometry View Components - UI Manager"""
import tkinter as tk
from tkinter import ttk
import psutil

class GeometryUIManager:
    """Quản lý layout và giao diện cho Geometry View"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
        self.window = parent_view.window
        self.config = parent_view.config
        
        # Header colors
        self.HEADER_COLORS = {
            "primary": "#2E86AB", "secondary": "#1B5299", "text": "#FFFFFF",
            "accent": "#F18F01", "success": "#4CAF50", "warning": "#FF9800", "danger": "#F44336"
        }
    
    def setup_main_layout(self):
        """Thiết lập layout chính"""
        # Tạo header
        self._create_header()
        
        # Container chính
        self.main_container = tk.Frame(self.window, bg="#F8F9FA")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Top frame với dropdown
        top_frame = tk.Frame(self.main_container, bg="#F8F9FA")
        top_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        self._setup_dropdowns(top_frame)
        
        return {
            'main_container': self.main_container,
            'top_frame': top_frame
        }
    
    def _create_header(self):
        """Tạo header với memory monitoring"""
        # Main header frame
        self.header_frame = tk.Frame(self.window, bg=self.HEADER_COLORS["primary"], height=90)
        self.header_frame.pack(fill="x", padx=10, pady=5)
        self.header_frame.pack_propagate(False)
        
        header_content = tk.Frame(self.header_frame, bg=self.HEADER_COLORS["primary"])
        header_content.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Logo và title
        left_section = tk.Frame(header_content, bg=self.HEADER_COLORS["primary"])
        left_section.pack(side="left", fill="y")
        
        logo_frame = tk.Frame(left_section, bg=self.HEADER_COLORS["primary"])
        logo_frame.pack(side="top", fill="x")
        tk.Label(logo_frame, text="🧮", font=("Arial", 20),
                 bg=self.HEADER_COLORS["primary"], fg=self.HEADER_COLORS["text"]).pack(side="left")
        tk.Label(logo_frame, text="Geometry v2.1 - Anti-Crash! 💪", font=("Arial", 16, "bold"),
                 bg=self.HEADER_COLORS["primary"], fg=self.HEADER_COLORS["text"]).pack(side="left", padx=(5, 20))
        
        # Operation selector
        operation_frame = tk.Frame(left_section, bg=self.HEADER_COLORS["primary"])
        operation_frame.pack(side="top", fill="x", pady=(5, 0))
        tk.Label(operation_frame, text="Phép toán:", font=("Arial", 10),
                 bg=self.HEADER_COLORS["primary"], fg=self.HEADER_COLORS["text"]).pack(side="left")
        
        # Tạo operation menu (sẽ được cập nhật bởi OperationManager)
        self.operation_menu = tk.OptionMenu(operation_frame, self.parent.pheptoan_var, "")
        self.operation_menu.config(
            bg=self.HEADER_COLORS["secondary"], fg=self.HEADER_COLORS["text"],
            font=("Arial", 10, "bold"), width=15, relief="flat", borderwidth=0
        )
        self.operation_menu.pack(side="left", padx=(5, 0))
        
        # Center section
        center_section = tk.Frame(header_content, bg=self.HEADER_COLORS["primary"])
        center_section.pack(side="left", fill="both", expand=True, padx=20)
        
        version_frame = tk.Frame(center_section, bg=self.HEADER_COLORS["primary"])
        version_frame.pack(side="top", fill="x")
        tk.Label(version_frame, text="Phiên bản:", font=("Arial", 9),
                 bg=self.HEADER_COLORS["primary"], fg=self.HEADER_COLORS["text"]).pack(side="left")
        
        self.version_menu = tk.OptionMenu(version_frame, self.parent.phien_ban_var, *self.parent.phien_ban_list)
        self.version_menu.config(
            bg=self.HEADER_COLORS["accent"], fg="white", font=("Arial", 9),
            width=15, relief="flat", borderwidth=0
        )
        self.version_menu.pack(side="left", padx=(5, 0))
        
        # Excel status indicator
        self.excel_status_label = tk.Label(
            center_section, text="📊 Excel: ✅ Ready", font=("Arial", 8),
            bg=self.HEADER_COLORS["primary"], fg=self.HEADER_COLORS["success"]
        )
        self.excel_status_label.pack(side="bottom")
        
        # Memory status indicator (sẽ được cập nhật bởi MemoryMonitor)
        self.memory_status_label = tk.Label(
            center_section, text=f"💾 Memory: {self._get_memory_usage():.1f}MB", font=("Arial", 8),
            bg=self.HEADER_COLORS["primary"], fg=self.HEADER_COLORS["text"]
        )
        self.memory_status_label.pack(side="bottom")
        
        # Service status indicator
        status_text = "Service: ✅ Ready" if self.parent.geometry_service else "Service: ⚠️ Error"
        tk.Label(center_section, text=status_text, font=("Arial", 8),
                bg=self.HEADER_COLORS["primary"], fg=self.HEADER_COLORS["text"]).pack(side="bottom")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def _setup_dropdowns(self, parent):
        """Setup dropdown chọn nhóm"""
        # Lấy shapes từ service hoặc fallback
        shapes = []
        if self.parent.geometry_service:
            shapes = self.parent.geometry_service.get_available_shapes()
        else:
            shapes = ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"]
        
        # Đặt mặc định
        if shapes:
            self.parent.dropdown1_var.set(shapes[0])
            self.parent.dropdown2_var.set(shapes[0])
        
        # Tạo dropdown A
        self.label_A = tk.Label(parent, text="Chọn nhóm A:", bg="#F8F9FA", font=("Arial", 10))
        self.label_A.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.dropdown1_menu = tk.OptionMenu(parent, self.parent.dropdown1_var, *shapes)
        self.dropdown1_menu.config(width=15, font=("Arial", 9))
        self.dropdown1_menu.grid(row=0, column=1, padx=5, pady=5)
        
        # Tạo dropdown B
        self.label_B = tk.Label(parent, text="Chọn nhóm B:", bg="#F8F9FA", font=("Arial", 10))
        self.label_B.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        self.dropdown2_menu = tk.OptionMenu(parent, self.parent.dropdown2_var, *shapes)
        self.dropdown2_menu.config(width=15, font=("Arial", 9))
        self.dropdown2_menu.grid(row=0, column=3, padx=5, pady=5)
    
    def create_control_frame(self):
        """Tạo khung điều khiển và kết quả"""
        self.frame_tong = tk.LabelFrame(
            self.main_container, text="🎉 KẾT QUẢ & ĐIỀU KHIỂN",
            bg="#FFFFFF", font=("Arial", 10, "bold")
        )
        self.frame_tong.grid(row=8, column=0, columnspan=4, padx=10, pady=10, sticky="we")
        
        # Text widget hiển thị kết quả (chỉ 1-2 dòng)
        self.entry_tong = tk.Text(
            self.main_container,
            width=80, height=2,
            font=("Courier New", 9), wrap=tk.NONE,
            bg="#F8F9FA", fg="black",
            relief="solid", bd=1, padx=5, pady=5
        )
        self.entry_tong.grid(row=9, column=0, columnspan=4, padx=5, pady=5, sticky="we")
        
        return self.frame_tong, self.entry_tong
    
    def create_button_frames(self, control_frame):
        """Tạo các frame cho buttons"""
        # Nút Import Excel
        btn_import_excel = tk.Button(
            control_frame, text="📁 Import Excel (Fast Select - 250k limit!)",
            bg="#FF9800", fg="white", font=("Arial", 9, "bold")
        )
        btn_import_excel.grid(row=0, column=0, columnspan=4, pady=5, sticky="we")
        
        # Frame cho nút thủ công
        frame_buttons_manual = tk.Frame(control_frame, bg="#FFFFFF")
        frame_buttons_manual.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        
        # Frame cho nút import mode
        frame_buttons_import = tk.Frame(control_frame, bg="#FFFFFF")
        frame_buttons_import.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        
        return {
            'btn_import_excel': btn_import_excel,
            'frame_buttons_manual': frame_buttons_manual,
            'frame_buttons_import': frame_buttons_import
        }
    
    def create_copy_button(self):
        """Tạo nút copy kết quả"""
        btn_copy_result = tk.Button(
            self.main_container, text="📋 Copy Kết Quả",
            bg="#9C27B0", fg="white", font=("Arial", 9, "bold"),
            width=20
        )
        btn_copy_result.grid(row=10, column=0, sticky="w", padx=0, pady=5)
        btn_copy_result.grid_remove()  # Ẩn ban đầu
        
        return btn_copy_result
    
    def update_operation_menu(self, operations):
        """Cập nhật menu phép toán"""
        try:
            menu = self.operation_menu['menu']
            menu.delete(0, 'end')
            for operation in operations:
                menu.add_command(label=operation, command=tk._setit(self.parent.pheptoan_var, operation))
        except Exception as e:
            print(f"Warning: Could not update operation menu: {e}")
    
    def update_shape_dropdowns(self, available_shapes):
        """Cập nhật các dropdown hình dạng"""
        if not available_shapes:
            return
        try:
            # Cập nhật dropdown A
            menu_A = self.dropdown1_menu['menu']
            menu_A.delete(0, 'end')
            for shape in available_shapes:
                menu_A.add_command(label=shape, command=tk._setit(self.parent.dropdown1_var, shape))
            
            # Đặt mặc định nếu giá trị hiện tại không hợp lệ
            if self.parent.dropdown1_var.get() not in available_shapes:
                self.parent.dropdown1_var.set(available_shapes[0])
            
            # Cập nhật dropdown B
            menu_B = self.dropdown2_menu['menu']
            menu_B.delete(0, 'end')
            for shape in available_shapes:
                menu_B.add_command(label=shape, command=tk._setit(self.parent.dropdown2_var, shape))
            if self.parent.dropdown2_var.get() not in available_shapes:
                self.parent.dropdown2_var.set(available_shapes[0])
                
        except Exception as e:
            print(f"Warning: Could not update dropdowns: {e}")
    
    def show_hide_dropdown_B(self, show=True):
        """Hiện/ẩn dropdown B theo phép toán"""
        try:
            if show:
                self.label_B.grid()
                self.dropdown2_menu.grid()
            else:
                self.label_B.grid_remove()
                self.dropdown2_menu.grid_remove()
        except Exception as e:
            print(f"Warning: Could not show/hide dropdown B: {e}")