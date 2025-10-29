import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
import threading
import os
from datetime import datetime
import psutil

class GeometryView:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Geometry Mode - Anti-Crash Excel! 💪")
        self.window.geometry("900x900")
        self.window.configure(bg="#F8F9FA")

        # Lưu config được truyền vào
        self.config = config or {}
        
        # Import và khởi tạo GeometryService (lazy loading)
        self.geometry_service = None
        self._initialize_service()
        
        # Excel processing state
        self.imported_data = False
        self.imported_file_path = ""
        self.imported_file_name = ""  # NEW: store only file name after import
        self.manual_data_entered = False
        self.processing_cancelled = False
        self.is_large_file = False  # Track if current file is large
        
        # Biến và trạng thái
        self._initialize_variables()
        self._setup_ui()
        
        # Đảm bảo hiển thị đúng ngay lần đầu
        self._on_operation_changed()
        self._on_shape_changed()

    def _initialize_service(self):
        """Khởi tạo GeometryService"""
        try:
            from services.geometry.geometry_service import GeometryService
            self.geometry_service = GeometryService(self.config)
        except Exception as e:
            print(f"Warning: Could not initialize GeometryService: {e}")
            self.geometry_service = None

    def _initialize_variables(self):
        """Khởi tạo tất cả biến"""
        self.dropdown1_var = tk.StringVar(value="")
        self.dropdown2_var = tk.StringVar(value="")
        self.kich_thuoc_A_var = tk.StringVar(value="3")
        self.kich_thuoc_B_var = tk.StringVar(value="3")
        # Đặt phép toán mặc định để menu hiển thị ngay
        self.pheptoan_var = tk.StringVar(value="Khoảng cách")

        # Phiên bản mặc định - lấy từ config hoặc fallback
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var = tk.StringVar(value=self.phien_ban_list[0])
        
        # Bind các thay đổi để cập nhật service
        self.dropdown1_var.trace('w', self._on_shape_changed)
        self.dropdown2_var.trace('w', self._on_shape_changed)
        self.pheptoan_var.trace('w', self._on_operation_changed)
        self.kich_thuoc_A_var.trace('w', self._on_dimension_changed)
        self.kich_thuoc_B_var.trace('w', self._on_dimension_changed)
        
        # Bind input events to detect manual data entry
        self.window.after(1000, self._setup_input_bindings)
        
        # Cập nhật state ban đầu cho service
        if self.geometry_service:
            self.geometry_service.set_kich_thuoc(self.kich_thuoc_A_var.get(), self.kich_thuoc_B_var.get())
    
    def _setup_input_bindings(self):
        """Setup bindings for input change detection"""
        entries = self._get_all_input_entries()
        for entry in entries:
            if hasattr(entry, 'bind'):
                entry.bind('<KeyRelease>', self._on_input_data_changed)
    
    def _get_all_input_entries(self):
        """Get all input entry widgets"""
        entries = []
        
        # Collect all entry widgets
        for attr_name in dir(self):
            if attr_name.startswith('entry_') and hasattr(self, attr_name):
                entry = getattr(self, attr_name)
                if hasattr(entry, 'get'):  # It's an Entry widget
                    entries.append(entry)
        
        return entries
    
    def _on_input_data_changed(self, event):
        """Handle manual data input changes"""
        if self.imported_data:
            messagebox.showerror("Lỗi", "Đã import Excel, không thể nhập dữ liệu thủ công!")
            event.widget.delete(0, tk.END)
            return

        has_data = self._check_manual_data()
        
        if has_data and not self.manual_data_entered:
            self.manual_data_entered = True
            self._show_manual_buttons()
        elif not has_data and self.manual_data_entered:
            self.manual_data_entered = False
            self._hide_action_buttons()
    
    def _check_manual_data(self):
        """Check if manual data has been entered"""
        entries = self._get_all_input_entries()
        for entry in entries:
            try:
                if entry.get().strip():
                    return True
            except:
                pass
        return False
    
    def _show_manual_buttons(self):
        """Show buttons for manual mode"""
        self.frame_buttons_manual.grid()
        if hasattr(self, 'frame_buttons_import'):
            self.frame_buttons_import.grid_remove()
    
    def _show_import_buttons(self):
        """Show buttons for import mode"""
        if hasattr(self, 'frame_buttons_import'):
            self.frame_buttons_import.grid()
        self.frame_buttons_manual.grid_remove()
    
    def _hide_action_buttons(self):
        """Hide all action buttons"""
        self.frame_buttons_manual.grid_remove()
        if hasattr(self, 'frame_buttons_import'):
            self.frame_buttons_import.grid_remove()

    def _get_available_versions(self):
        """Lấy danh sách phiên bản từ config hoặc sử dụng mặc định"""
        try:
            if self.config and 'common' in self.config and 'versions' in self.config['common']:
                versions_data = self.config['common']['versions']
                if 'versions' in versions_data:
                    return [f"Phiên bản {v}" for v in versions_data['versions']]
        except Exception as e:
            print(f"Warning: Không thể load versions từ config: {e}")
        
        # Fallback nếu không có config
        return ["Phiên bản fx799", "Phiên bản fx880", "Phiên bản fx801"]
    
    def _get_available_operations(self):
        """Lấy danh sách phép toán"""
        if self.geometry_service:
            return self.geometry_service.get_available_operations()
        else:
            return ["Tương giao", "Khoảng cách", "Diện tích", "Thể tích", "PT đường thẳng"]
    
    def _on_shape_changed(self, *args):
        """Xử lý khi thay đổi hình dạng"""
        if self.geometry_service:
            self.geometry_service.set_current_shapes(self.dropdown1_var.get(), self.dropdown2_var.get())
        self._update_input_frames()
    
    def _on_operation_changed(self, *args):
        """Xử lý khi thay đổi phép toán"""
        operation = self.pheptoan_var.get()
        if operation and self.geometry_service:
            self.geometry_service.set_current_operation(operation)
            # Cập nhật dropdown options theo phép toán
            available_shapes = self.geometry_service.update_dropdown_options(operation)
            self._update_shape_dropdowns(available_shapes)
        self._update_input_frames()
    
    def _on_dimension_changed(self, *args):
        """Xử lý khi thay đổi kích thước"""
        if self.geometry_service:
            self.geometry_service.set_kich_thuoc(self.kich_thuoc_A_var.get(), self.kich_thuoc_B_var.get())
    
    def _update_shape_dropdowns(self, available_shapes):
        """Cập nhật các dropdown theo phép toán với giá trị mặc định an toàn"""
        if not available_shapes:
            return
        try:
            # Cập nhật dropdown A
            menu_A = self.dropdown1_menu['menu']
            menu_A.delete(0, 'end')
            for shape in available_shapes:
                menu_A.add_command(label=shape, command=tk._setit(self.dropdown1_var, shape))
            # Đặt mặc định nếu giá trị hiện tại không hợp lệ
            if self.dropdown1_var.get() not in available_shapes:
                self.dropdown1_var.set(available_shapes[0])
            
            # Cập nhật dropdown B khi phép toán cần B
            if self.pheptoan_var.get() not in ["Diện tích", "Thể tích"]:
                menu_B = self.dropdown2_menu['menu']
                menu_B.delete(0, 'end')
                for shape in available_shapes:
                    menu_B.add_command(label=shape, command=tk._setit(self.dropdown2_var, shape))
                if self.dropdown2_var.get() not in available_shapes:
                    self.dropdown2_var.set(available_shapes[0])
                # Đảm bảo hiển thị B
                self.label_B.grid()
                self.dropdown2_menu.grid()
            else:
                # Ẩn dropdown B khi không cần
                self.label_B.grid_remove()
                self.dropdown2_menu.grid_remove()
        except Exception as e:
            print(f"Warning: Could not update dropdowns: {e}")
    
    def _update_input_frames(self):
        """Cập nhật hiển thị các frame nhập liệu"""
        # Ẩn các frame cũ trước
        all_frames = ['frame_A_diem', 'frame_A_duong', 'frame_A_plane', 'frame_A_circle', 'frame_A_sphere',
                     'frame_B_diem', 'frame_B_duong', 'frame_B_plane', 'frame_B_circle', 'frame_B_sphere']
        for frame_name in all_frames:
            frame = getattr(self, frame_name, None)
            if frame and hasattr(frame, 'grid_remove'):
                try:
                    frame.grid_remove()
                except:
                    pass
        
        # Hiển thị frame cho nhóm A
        shape_A = self.dropdown1_var.get()
        if shape_A:
            self._show_input_frame_A(shape_A)
        
        # Hiển thị frame cho nhóm B (nếu cần)
        if self.pheptoan_var.get() not in ["Diện tích", "Thể tích"]:
            shape_B = self.dropdown2_var.get()
            if shape_B:
                self._show_input_frame_B(shape_B)
    
    def _show_input_frame_A(self, shape):
        """Hiển thị frame nhập liệu cho nhóm A"""
        try:
            if shape == "Điểm" and hasattr(self, 'frame_A_diem'):
                self.frame_A_diem.grid()
            elif shape == "Đường thẳng" and hasattr(self, 'frame_A_duong'):
                self.frame_A_duong.grid()
            elif shape == "Mặt phẳng" and hasattr(self, 'frame_A_plane'):
                self.frame_A_plane.grid()
            elif shape == "Đường tròn" and hasattr(self, 'frame_A_circle'):
                self.frame_A_circle.grid()
            elif shape == "Mặt cầu" and hasattr(self, 'frame_A_sphere'):
                self.frame_A_sphere.grid()
        except Exception as e:
            print(f"Warning: Could not show frame A for {shape}: {e}")
    
    def _show_input_frame_B(self, shape):
        """Hiển thị frame nhập liệu cho nhóm B"""
        try:
            if shape == "Điểm" and hasattr(self, 'frame_B_diem'):
                self.frame_B_diem.grid()
            elif shape == "Đường thẳng" and hasattr(self, 'frame_B_duong'):
                self.frame_B_duong.grid()
            elif shape == "Mặt phẳng" and hasattr(self, 'frame_B_plane'):
                self.frame_B_plane.grid()
            elif shape == "Đường tròn" and hasattr(self, 'frame_B_circle'):
                self.frame_B_circle.grid()
            elif shape == "Mặt cầu" and hasattr(self, 'frame_B_sphere'):
                self.frame_B_sphere.grid()
        except Exception as e:
            print(f"Warning: Could not show frame B for {shape}: {e}")

    def _setup_ui(self):
        """Setup giao diện chính"""
        # Header
        self._create_header()
        
        self.main_container = tk.Frame(self.window, bg="#F8F9FA")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Top frame với dropdown
        top_frame = tk.Frame(self.main_container, bg="#F8F9FA")
        top_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        self._setup_dropdowns(top_frame)
        self._setup_all_input_frames()  # Tạo tất cả frame
        self._setup_control_frame()
        
        # Hiển thông báo ban đầu
        self._show_ready_message()

    def _create_header(self):
        """Tạo header với memory monitoring"""
        HEADER_COLORS = {
            "primary": "#2E86AB", "secondary": "#1B5299", "text": "#FFFFFF",
            "accent": "#F18F01", "success": "#4CAF50", "warning": "#FF9800", "danger": "#F44336"
        }

        # Main header frame
        self.header_frame = tk.Frame(self.window, bg=HEADER_COLORS["primary"], height=90)
        self.header_frame.pack(fill="x", padx=10, pady=5)
        self.header_frame.pack_propagate(False)

        header_content = tk.Frame(self.header_frame, bg=HEADER_COLORS["primary"])
        header_content.pack(fill="both", expand=True, padx=15, pady=10)

        # Logo và title
        left_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        left_section.pack(side="left", fill="y")

        logo_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        logo_frame.pack(side="top", fill="x")
        tk.Label(logo_frame, text="🧮", font=("Arial", 20),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        tk.Label(logo_frame, text="Geometry v2.1 - Anti-Crash! 💪", font=("Arial", 16, "bold"),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left", padx=(5, 20))

        # Operation selector
        operation_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        operation_frame.pack(side="top", fill="x", pady=(5, 0))
        tk.Label(operation_frame, text="Phép toán:", font=("Arial", 10),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")

        operations = self._get_available_operations()
        self.operation_menu = tk.OptionMenu(operation_frame, self.pheptoan_var, *operations)
        self.operation_menu.config(
            bg=HEADER_COLORS["secondary"], fg=HEADER_COLORS["text"],
            font=("Arial", 10, "bold"), width=15, relief="flat", borderwidth=0
        )
        self.operation_menu.pack(side="left", padx=(5, 0))

        # Center section
        center_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        center_section.pack(side="left", fill="both", expand=True, padx=20)

        version_frame = tk.Frame(center_section, bg=HEADER_COLORS["primary"])
        version_frame.pack(side="top", fill="x")
        tk.Label(version_frame, text="Phiên bản:", font=("Arial", 9),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")

        self.version_menu = tk.OptionMenu(version_frame, self.phien_ban_var, *self.phien_ban_list)
        self.version_menu.config(
            bg=HEADER_COLORS["accent"], fg="white", font=("Arial", 9),
            width=15, relief="flat", borderwidth=0
        )
        self.version_menu.pack(side="left", padx=(5, 0))
        
        # Excel status indicator
        self.excel_status_label = tk.Label(
            center_section, text="📊 Excel: ✅ Ready", font=("Arial", 8),
            bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["success"]
        )
        self.excel_status_label.pack(side="bottom")
        
        # Memory status indicator
        self.memory_status_label = tk.Label(
            center_section, text=f"💾 Memory: {self._get_memory_usage():.1f}MB", font=("Arial", 8),
            bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]
        )
        self.memory_status_label.pack(side="bottom")
        
        # Service status indicator
        status_text = "Service: ✅ Ready" if self.geometry_service else "Service: ⚠️ Error"
        tk.Label(center_section, text=status_text, font=("Arial", 8),
                bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="bottom")
        
        # Start memory monitoring
        self._start_memory_monitoring()
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def _start_memory_monitoring(self):
        """Start periodic memory monitoring"""
        def update_memory():
            try:
                memory_mb = self._get_memory_usage()
                
                # Color coding for memory usage
                if memory_mb > 800:
                    color = "#F44336"  # Red
                    status = "🔥 High"
                elif memory_mb > 500:
                    color = "#FF9800"  # Orange
                    status = "⚠️ Medium"
                else:
                    color = "#4CAF50"  # Green
                    status = "✅ OK"
                
                self.memory_status_label.config(
                    text=f"💾 Memory: {memory_mb:.1f}MB ({status})",
                    fg=color
                )
                
            except Exception:
                pass
            
            # Schedule next update
            self.window.after(5000, update_memory)  # Update every 5 seconds
        
        update_memory()

    def _setup_dropdowns(self, parent):
        """Setup dropdown chọn nhóm với giá trị mặc định"""
        shapes = []
        if self.geometry_service:
            shapes = self.geometry_service.get_available_shapes()
        else:
            shapes = ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"]

        # Đặt mặc định ngay để hiển thị nhãn
        if shapes:
            self.dropdown1_var.set(shapes[0])
            self.dropdown2_var.set(shapes[0])

        self.label_A = tk.Label(parent, text="Chọn nhóm A:", bg="#F8F9FA", font=("Arial", 10))
        self.label_A.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.dropdown1_menu = tk.OptionMenu(parent, self.dropdown1_var, *shapes)
        self.dropdown1_menu.config(width=15, font=("Arial", 9))
        self.dropdown1_menu.grid(row=0, column=1, padx=5, pady=5)

        self.label_B = tk.Label(parent, text="Chọn nhóm B:", bg="#F8F9FA", font=("Arial", 10))
        self.label_B.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.dropdown2_menu = tk.OptionMenu(parent, self.dropdown2_var, *shapes)
        self.dropdown2_menu.config(width=15, font=("Arial", 9))
        self.dropdown2_menu.grid(row=0, column=3, padx=5, pady=5)

    def _setup_all_input_frames(self):
        """Tạo tất cả các frame nhập liệu cho đầy đủ 5 hình"""
        # NHÓM A
        self._create_point_frame_A()
        self._create_line_frame_A()
        self._create_plane_frame_A()
        self._create_circle_frame_A()
        self._create_sphere_frame_A()
        
        # NHÓM B
        self._create_point_frame_B()
        self._create_line_frame_B()
        self._create_plane_frame_B()
        self._create_circle_frame_B()
        self._create_sphere_frame_B()
    
    # ========== NHÓM A FRAMES ==========
    def _create_point_frame_A(self):
        """Tạo frame điểm A"""
        self.frame_A_diem = tk.LabelFrame(
            self.main_container, text="🎯 NHÓM A - Điểm",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_diem.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_diem, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(self.frame_A_diem, self.kich_thuoc_A_var, "2", "3").grid(row=0, column=1)

        tk.Label(self.frame_A_diem, text="Nhập tọa độ (x,y,z):", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_diem_A = tk.Entry(self.frame_A_diem, width=40)
        self.entry_diem_A.grid(row=1, column=1, columnspan=2, sticky="we")
        
        self.frame_A_diem.grid_remove()
    
    def _create_line_frame_A(self):
        """Tạo frame đường thẳng A"""
        self.frame_A_duong = tk.LabelFrame(
            self.main_container, text="📏 NHÓM A - Đường thẳng",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_duong.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_duong, text="Điểm (A,B,C):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_point_A = tk.Entry(self.frame_A_duong, width=30)
        self.entry_point_A.grid(row=0, column=1)
        
        tk.Label(self.frame_A_duong, text="Vector (X,Y,Z):", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_vector_A = tk.Entry(self.frame_A_duong, width=30)
        self.entry_vector_A.grid(row=1, column=1)
        
        self.frame_A_duong.grid_remove()
    
    def _create_plane_frame_A(self):
        """Tạo frame mặt phẳng A"""
        self.frame_A_plane = tk.LabelFrame(
            self.main_container, text="📐 NHÓM A - Mặt phẳng",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_plane.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_plane, text="Phương trình ax+by+cz+d=0:", bg="#FFFFFF").grid(row=0, column=0, columnspan=4)
        
        tk.Label(self.frame_A_plane, text="a:", bg="#FFFFFF", width=3).grid(row=1, column=0, sticky="e")
        self.entry_a_A = tk.Entry(self.frame_A_plane, width=15)
        self.entry_a_A.grid(row=1, column=1, padx=5)
        
        tk.Label(self.frame_A_plane, text="b:", bg="#FFFFFF", width=3).grid(row=1, column=2, sticky="e")
        self.entry_b_A = tk.Entry(self.frame_A_plane, width=15)
        self.entry_b_A.grid(row=1, column=3, padx=5)
        
        tk.Label(self.frame_A_plane, text="c:", bg="#FFFFFF", width=3).grid(row=2, column=0, sticky="e")
        self.entry_c_A = tk.Entry(self.frame_A_plane, width=15)
        self.entry_c_A.grid(row=2, column=1, padx=5)
        
        tk.Label(self.frame_A_plane, text="d:", bg="#FFFFFF", width=3).grid(row=2, column=2, sticky="e")
        self.entry_d_A = tk.Entry(self.frame_A_plane, width=15)
        self.entry_d_A.grid(row=2, column=3, padx=5)
        
        self.frame_A_plane.grid_remove()
    
    def _create_circle_frame_A(self):
        """Tạo frame đường tròn A"""
        self.frame_A_circle = tk.LabelFrame(
            self.main_container, text="⭕ NHÓM A - Đường tròn",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_circle.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_circle, text="Tâm đường tròn (x,y):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_center_A = tk.Entry(self.frame_A_circle, width=25)
        self.entry_center_A.grid(row=0, column=1, padx=5)
        
        tk.Label(self.frame_A_circle, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.entry_radius_A = tk.Entry(self.frame_A_circle, width=20)
        self.entry_radius_A.grid(row=0, column=3, padx=5)
        
        self.frame_A_circle.grid_remove()
    
    def _create_sphere_frame_A(self):
        """Tạo frame mặt cầu A"""
        self.frame_A_sphere = tk.LabelFrame(
            self.main_container, text="🌍 NHÓM A - Mặt cầu",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_sphere.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_sphere, text="Tâm mặt cầu (x,y,z):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_sphere_center_A = tk.Entry(self.frame_A_sphere, width=25)
        self.entry_sphere_center_A.grid(row=0, column=1, padx=5)
        
        tk.Label(self.frame_A_sphere, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.entry_sphere_radius_A = tk.Entry(self.frame_A_sphere, width=20)
        self.entry_sphere_radius_A.grid(row=0, column=3, padx=5)
        
        self.frame_A_sphere.grid_remove()
    
    # ========== NHÓM B FRAMES ==========
    def _create_point_frame_B(self):
        """Tạo frame điểm B"""
        self.frame_B_diem = tk.LabelFrame(
            self.main_container, text="🎯 NHÓM B - Điểm",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        self.frame_B_diem.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_B_diem, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(self.frame_B_diem, self.kich_thuoc_B_var, "2", "3").grid(row=0, column=1)

        tk.Label(self.frame_B_diem, text="Nhập tọa độ (x,y,z):", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_diem_B = tk.Entry(self.frame_B_diem, width=40)
        self.entry_diem_B.grid(row=1, column=1, columnspan=2, sticky="we")
        
        self.frame_B_diem.grid_remove()
    
    def _create_line_frame_B(self):
        """Tạo frame đường thẳng B"""
        self.frame_B_duong = tk.LabelFrame(
            self.main_container, text="📏 NHÓM B - Đường thẳng",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        self.frame_B_duong.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(self.frame_B_duong, text="Điểm (A,B,C):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_point_B = tk.Entry(self.frame_B_duong, width=30)
        self.entry_point_B.grid(row=0, column=1)
        
        tk.Label(self.frame_B_duong, text="Vector (X,Y,Z):", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_vector_B = tk.Entry(self.frame_B_duong, width=30)
        self.entry_vector_B.grid(row=1, column=1)
        
        self.frame_B_duong.grid_remove()
    
    def _create_plane_frame_B(self):
        """Tạo frame mặt phẳng B"""
        self.frame_B_plane = tk.LabelFrame(
            self.main_container, text="📐 NHÓM B - Mặt phẳng",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        self.frame_B_plane.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_B_plane, text="Phương trình ax+by+cz+d=0:", bg="#FFFFFF").grid(row=0, column=0, columnspan=4)
        
        tk.Label(self.frame_B_plane, text="a:", bg="#FFFFFF", width=3).grid(row=1, column=0, sticky="e")
        self.entry_a_B = tk.Entry(self.frame_B_plane, width=15)
        self.entry_a_B.grid(row=1, column=1, padx=5)
        
        tk.Label(self.frame_B_plane, text="b:", bg="#FFFFFF", width=3).grid(row=1, column=2, sticky="e")
        self.entry_b_B = tk.Entry(self.frame_B_plane, width=15)
        self.entry_b_B.grid(row=1, column=3, padx=5)
        
        tk.Label(self.frame_B_plane, text="c:", bg="#FFFFFF", width=3).grid(row=2, column=0, sticky="e")
        self.entry_c_B = tk.Entry(self.frame_B_plane, width=15)
        self.entry_c_B.grid(row=2, column=1, padx=5)
        
        tk.Label(self.frame_B_plane, text="d:", bg="#FFFFFF", width=3).grid(row=2, column=2, sticky="e")
        self.entry_d_B = tk.Entry(self.frame_B_plane, width=15)
        self.entry_d_B.grid(row=2, column=3, padx=5)
        
        self.frame_B_plane.grid_remove()
    
    def _create_circle_frame_B(self):
        """Tạo frame đường tròn B"""
        self.frame_B_circle = tk.LabelFrame(
            self.main_container, text="⭕ NHÓM B - Đường tròn",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        self.frame_B_circle.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(self.frame_B_circle, text="Tâm đường tròn (x,y):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_center_B = tk.Entry(self.frame_B_circle, width=25)
        self.entry_center_B.grid(row=0, column=1, padx=5)
        
        tk.Label(self.frame_B_circle, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.entry_radius_B = tk.Entry(self.frame_B_circle, width=20)
        self.entry_radius_B.grid(row=0, column=3, padx=5)
        
        self.frame_B_circle.grid_remove()
    
    def _create_sphere_frame_B(self):
        """Tạo frame mặt cầu B"""
        self.frame_B_sphere = tk.LabelFrame(
            self.main_container, text="🌍 NHÓM B - Mặt cầu",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        self.frame_B_sphere.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(self.frame_B_sphere, text="Tâm mặt cầu (x,y,z):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_sphere_center_B = tk.Entry(self.frame_B_sphere, width=25)
        self.entry_sphere_center_B.grid(row=0, column=1, padx=5)
        
        tk.Label(self.frame_B_sphere, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.entry_sphere_radius_B = tk.Entry(self.frame_B_sphere, width=20)
        self.entry_sphere_radius_B.grid(row=0, column=3, padx=5)
        
        self.frame_B_sphere.grid_remove()
    
    # ========== DATA EXTRACTION ==========
    def _get_input_data_A(self):
        \"\"\"L\u1ea5y d\u1eef li\u1ec7u nh\u1eadp cho nh\u00f3m A\"\"\"\n        shape = self.dropdown1_var.get()\n        data = {}\n        \n        if shape == \"\u0110i\u1ec3m\":\n            data['point_input'] = self.entry_diem_A.get() if hasattr(self, 'entry_diem_A') else ''\n        elif shape == \"\u0110\u01b0\u1eddng th\u1eb3ng\":\n            data['line_A1'] = self.entry_point_A.get() if hasattr(self, 'entry_point_A') else ''\n            data['line_X1'] = self.entry_vector_A.get() if hasattr(self, 'entry_vector_A') else ''\n        elif shape == \"M\u1eb7t ph\u1eb3ng\":\n            data['plane_a'] = self.entry_a_A.get() if hasattr(self, 'entry_a_A') else ''\n            data['plane_b'] = self.entry_b_A.get() if hasattr(self, 'entry_b_A') else ''\n            data['plane_c'] = self.entry_c_A.get() if hasattr(self, 'entry_c_A') else ''\n            data['plane_d'] = self.entry_d_A.get() if hasattr(self, 'entry_d_A') else ''\n        elif shape == \"\u0110\u01b0\u1eddng tr\u00f2n\":\n            data['circle_center'] = self.entry_center_A.get() if hasattr(self, 'entry_center_A') else ''\n            data['circle_radius'] = self.entry_radius_A.get() if hasattr(self, 'entry_radius_A') else ''\n        elif shape == \"M\u1eb7t c\u1ea7u\":\n            data['sphere_center'] = self.entry_sphere_center_A.get() if hasattr(self, 'entry_sphere_center_A') else ''\n            data['sphere_radius'] = self.entry_sphere_radius_A.get() if hasattr(self, 'entry_sphere_radius_A') else ''\n        \n        return data\n    \n    def _get_input_data_B(self):\n        \"\"\"L\u1ea5y d\u1eef li\u1ec7u nh\u1eadp cho nh\u00f3m B\"\"\"\n        shape = self.dropdown2_var.get()\n        data = {}\n        \n        if shape == \"\u0110i\u1ec3m\":\n            data['point_input'] = self.entry_diem_B.get() if hasattr(self, 'entry_diem_B') else ''\n        elif shape == \"\u0110\u01b0\u1eddng th\u1eb3ng\":\n            data['line_A2'] = self.entry_point_B.get() if hasattr(self, 'entry_point_B') else ''\n            data['line_X2'] = self.entry_vector_B.get() if hasattr(self, 'entry_vector_B') else ''\n        elif shape == \"M\u1eb7t ph\u1eb3ng\":\n            data['plane_a'] = self.entry_a_B.get() if hasattr(self, 'entry_a_B') else ''\n            data['plane_b'] = self.entry_b_B.get() if hasattr(self, 'entry_b_B') else ''\n            data['plane_c'] = self.entry_c_B.get() if hasattr(self, 'entry_c_B') else ''\n            data['plane_d'] = self.entry_d_B.get() if hasattr(self, 'entry_d_B') else ''\n        elif shape == \"\u0110\u01b0\u1eddng tr\u00f2n\":\n            data['circle_center'] = self.entry_center_B.get() if hasattr(self, 'entry_center_B') else ''\n            data['circle_radius'] = self.entry_radius_B.get() if hasattr(self, 'entry_radius_B') else ''\n        elif shape == \"M\u1eb7t c\u1ea7u\":\n            data['sphere_center'] = self.entry_sphere_center_B.get() if hasattr(self, 'entry_sphere_center_B') else ''\n            data['sphere_radius'] = self.entry_sphere_radius_B.get() if hasattr(self, 'entry_sphere_radius_B') else ''\n        \n        return data\n    \n    # ========== PROCESSING METHODS ==========\n    def _process_group_A(self):\n        \"\"\"X\u1eed l\u00fd nh\u00f3m A\"\"\"\n        try:\n            if not self.geometry_service:\n                messagebox.showerror(\"L\u1ed7i\", \"GeometryService ch\u01b0a \u0111\u01b0\u1ee3c kh\u1edfi t\u1ea1o!\")\n                return\n            \n            data_A = self._get_input_data_A()\n            result = self.geometry_service.thuc_thi_A(data_A)\n            self._update_result_display(f\"Nh\u00f3m A \u0111\u00e3 x\u1eed l\u00fd: {result}\")\n        except Exception as e:\n            messagebox.showerror(\"L\u1ed7i\", f\"L\u1ed7i x\u1eed l\u00fd nh\u00f3m A: {str(e)}\")\n    \n    def _process_group_B(self):\n        \"\"\"X\u1eed l\u00fd nh\u00f3m B\"\"\"\n        try:\n            if not self.geometry_service:\n                messagebox.showerror(\"L\u1ed7i\", \"GeometryService ch\u01b0a \u0111\u01b0\u1ee3c kh\u1edfi t\u1ea1o!\")\n                return\n                \n            data_B = self._get_input_data_B()\n            result = self.geometry_service.thuc_thi_B(data_B)\n            self._update_result_display(f\"Nh\u00f3m B \u0111\u00e3 x\u1eed l\u00fd: {result}\")\n        except Exception as e:\n            messagebox.showerror(\"L\u1ed7i\", f\"L\u1ed7i x\u1eed l\u00fd nh\u00f3m B: {str(e)}\")\n    \n    def _process_all(self):\n        \"\"\"Th\u1ef1c thi t\u1ea5t c\u1ea3 - Core function!\"\"\"\n        try:\n            if not self.geometry_service:\n                messagebox.showerror(\"L\u1ed7i\", \"GeometryService ch\u01b0a \u0111\u01b0\u1ee3c kh\u1edfi t\u1ea1o!\")\n                return\n            \n            # Ki\u1ec3m tra xem \u0111\u00e3 ch\u1ecdn ph\u00e9p to\u00e1n v\u00e0 h\u00ecnh d\u1ea1ng ch\u01b0a\n            if not self.pheptoan_var.get():\n                messagebox.showwarning(\"C\u1ea3nh b\u00e1o\", \"Vui l\u00f2ng ch\u1ecdn ph\u00e9p to\u00e1n!\")\n                return\n            \n            if not self.dropdown1_var.get():\n                messagebox.showwarning(\"C\u1ea3nh b\u00e1o\", \"Vui l\u00f2ng ch\u1ecdn h\u00ecnh d\u1ea1ng cho nh\u00f3m A!\")\n                return\n            \n            # L\u1ea5y d\u1eef li\u1ec7u\n            data_A = self._get_input_data_A()\n            data_B = self._get_input_data_B()\n            \n            # X\u1eed l\u00fd\n            result_A, result_B = self.geometry_service.thuc_thi_tat_ca(data_A, data_B)\n            \n            # Sinh k\u1ebft qu\u1ea3 cu\u1ed1i c\u00f9ng\n            final_result = self.geometry_service.generate_final_result()\n            \n            # Hi\u1ec3n th\u1ecb k\u1ebft qu\u1ea3 - matching TL style\n            message = f\"\u2728 K\u1ebft qu\u1ea3 m\u00e3 h\u00f3a (cho m\u00e1y t\u00ednh):\\n{final_result}\\n\\n\"\n            message += f\"\ud83d\udcc8 Chi ti\u1ebft x\u1eed l\u00fd:\\n\"\n            message += f\"Ph\u00e9p to\u00e1n: {self.pheptoan_var.get()}\\n\"\n            message += f\"Nh\u00f3m A ({self.dropdown1_var.get()}): {result_A}\\n\"\n            if self.pheptoan_var.get() not in [\"Di\u1ec7n t\u00edch\", \"Th\u1ec3 t\u00edch\"]:\n                message += f\"Nh\u00f3m B ({self.dropdown2_var.get()}): {result_B}\"\n            \n            self._update_result_display(message)\n            \n        except Exception as e:\n            messagebox.showerror(\"L\u1ed7i\", f\"L\u1ed7i th\u1ef1c thi: {str(e)}\")\n    \n    # ========== SIMPLIFIED EXCEL METHODS - FILENAME ONLY ON IMPORT ==========\n    def _import_excel(self):\n        \"\"\"Ch\u1ec9 ch\u1ecdn file v\u00e0 l\u01b0u l\u1ea1i T\u00caN FILE, KH\u00d4NG \u0111\u1ecdc n\u1ed9i dung\"\"\"\n        try:\n            file_path = filedialog.askopenfilename(\n                title=\"Ch\u1ecdn file Excel\",\n                filetypes=[(\"Excel files\", \"*.xlsx *.xls\")]\n            )\n            \n            if not file_path:\n                return\n            \n            # Ki\u1ec3m tra extension\n            file_ext = os.path.splitext(file_path)[1].lower()\n            if file_ext not in ['.xlsx', '.xls']:\n                messagebox.showerror(\"L\u1ed7i\", \"Ch\u1ec9 h\u1ed7 tr\u1ee3 file Excel (.xlsx, .xls)!\")\n                return\n            \n            # Ki\u1ec3m tra file t\u1ed3n t\u1ea1i\n            if not os.path.exists(file_path):\n                messagebox.showerror(\"L\u1ed7i\", \"File kh\u00f4ng t\u1ed3n t\u1ea1i!\")\n                return\n            \n            # L\u01b0u ch\u1ec9 th\u00f4ng tin t\u00ean file, KH\u00d4NG \u0111\u1ecdc n\u1ed9i dung\n            self.imported_file_path = file_path\n            self.imported_file_name = os.path.basename(file_path)\n            self.imported_data = True\n            self.manual_data_entered = False\n            self.is_large_file = False  # Reset, s\u1ebd detect \u1edf b\u01b0\u1edbc process\n            \n            # Clear v\u00e0 kh\u00f3a c\u00e1c input th\u1ee7 c\u00f4ng\n            self._clear_and_lock_inputs()\n            \n            # Hi\u1ec3n th\u1ecb import buttons\n            self._show_import_buttons()\n            \n            # C\u1eadp nh\u1eadt status \u0111\u01a1n gi\u1ea3n (ch\u1ec9 t\u00ean file)\n            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)\n            status_message = (\n                f\"\ud83d\udcc1 \u0110\u00e3 import file: {self.imported_file_name}\\n\"\n                f\"\ud83d\udccf K\u00edch th\u01b0\u1edbc: {file_size_mb:.1f}MB\\n\\n\"\n                f\"\u26a0\ufe0f L\u01b0u \u00fd: Ch\u01b0a \u0111\u1ecdc n\u1ed9i dung file.\\n\"\n                f\"Vi\u1ec7c \u0111\u1ecdc, ki\u1ec3m tra v\u00e0 x\u1eed l\u00fd s\u1ebd th\u1ef1c hi\u1ec7n khi b\u1ea5m 'X\u1eed l\u00fd File Excel'.\\n\\n\"\n                f\"\ud83d\udcaa Ready for anti-crash processing!\"\n            )\n            \n            self.excel_status_label.config(text=f\"Excel: \ud83d\udcc1 {self.imported_file_name[:15]}...\")\n            self._update_result_display(status_message)\n        \n        except Exception as e:\n            messagebox.showerror(\"L\u1ed7i Import\", f\"L\u1ed7i import Excel: {str(e)}\")\n\n    def _process_excel_batch(self):\n        \"\"\"\u0110\u1ecdc v\u00e0 x\u1eed l\u00fd file Excel (ch\u1ec9 \u0111\u1ecdc \u1edf b\u01b0\u1edbc n\u00e0y)\"\"\"\n        try:\n            if not self.imported_data or not self.imported_file_path:\n                messagebox.showwarning(\"C\u1ea3nh b\u00e1o\", \"Ch\u01b0a import file Excel n\u00e0o!\")\n                return\n            \n            if not self.geometry_service:\n                messagebox.showerror(\"L\u1ed7i\", \"GeometryService ch\u01b0a s\u1eb5n s\u00e0ng!\")\n                return\n            \n            # Ki\u1ec3m tra file v\u1eabn t\u1ed3n t\u1ea1i\n            if not os.path.exists(self.imported_file_path):\n                messagebox.showerror(\"L\u1ed7i\", f\"File kh\u00f4ng t\u1ed3n t\u1ea1i: {self.imported_file_path}\")\n                return\n            \n            # H\u1ecfi l\u01b0u output tr\u01b0\u1edbc khi x\u1eed l\u00fd\n            original_name = os.path.splitext(self.imported_file_name)[0]\n            default_output = f\"{original_name}_encoded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx\"\n            output_path = filedialog.asksaveasfilename(\n                title=\"Ch\u1ecdn n\u01a1i l\u01b0u k\u1ebft qu\u1ea3\",\n                defaultextension=\".xlsx\",\n                filetypes=[(\"Excel files\", \"*.xlsx\")],\n                initialvalue=default_output\n            )\n            if not output_path:\n                return\n            \n            # L\u1ea5y setting hi\u1ec7n t\u1ea1i\n            shape_a = self.dropdown1_var.get()\n            shape_b = self.dropdown2_var.get() if self.pheptoan_var.get() not in [\"Di\u1ec7n t\u00edch\", \"Th\u1ec3 t\u00edch\"] else None\n            operation = self.pheptoan_var.get()\n            dimension_a = self.kich_thuoc_A_var.get()\n            dimension_b = self.kich_thuoc_B_var.get()\n            \n            # T\u1ea1o progress window\n            progress_window = self._create_progress_window(\"\u0110ang x\u1eed l\u00fd file Excel...\")\n            \n            def progress_callback(progress, processed, total, errors):\n                if hasattr(self, 'progress_var') and not self.processing_cancelled:\n                    try:\n                        self.progress_var.set(progress)\n                        memory_usage = self._get_memory_usage()\n                        progress_text = f\"\u0110ang x\u1eed l\u00fd: {processed:,}/{total:,} d\u00f2ng\\nL\u1ed7i: {errors:,}\\nMemory: {memory_usage:.1f}MB\"\n                        self.progress_label.config(text=progress_text)\n                        \n                        # C\u1eadp nh\u1eadt memory status\n                        if memory_usage > 800:\n                            self.memory_status_label.config(text=f\"\ud83d\udcbe Memory: {memory_usage:.1f}MB (\ud83d\udd25 High)\", fg=\"#F44336\")\n                        elif memory_usage > 500:\n                            self.memory_status_label.config(text=f\"\ud83d\udcbe Memory: {memory_usage:.1f}MB (\u26a0\ufe0f Medium)\", fg=\"#FF9800\")\n                        else:\n                            self.memory_status_label.config(text=f\"\ud83d\udcbe Memory: {memory_usage:.1f}MB (\u2705 OK)\", fg=\"#4CAF50\")\n                        \n                        progress_window.update()\n                    except Exception:\n                        pass\n            \n            def process_thread():\n                try:\n                    # CH\u1ec8 T\u1ea0I \u0110\u00c2Y m\u1edbi \u0111\u1ecdc v\u00e0 x\u1eed l\u00fd file (service t\u1ef1 detect large/normal)\n                    results, output_file, success_count, error_count = self.geometry_service.process_excel_batch(\n                        self.imported_file_path, shape_a, shape_b, operation,\n                        dimension_a, dimension_b, output_path, progress_callback\n                    )\n                    \n                    if not self.processing_cancelled:\n                        progress_window.destroy()\n                        \n                        # Hi\u1ec3n th\u1ecb k\u1ebft qu\u1ea3 th\u00e0nh c\u00f4ng\n                        result_message = (\n                            f\"\ud83c\udf89 Ho\u00e0n th\u00e0nh x\u1eed l\u00fd Excel!\\n\\n\"\n                            f\"\ud83d\udcc1 File g\u1ed1c: {self.imported_file_name}\\n\"\n                            f\"\ud83d\udcc1 Output: {os.path.basename(output_file)}\\n\"\n                            f\"\u2705 Success: {success_count:,} rows\\n\"\n                            f\"\u274c Errors: {error_count:,} rows\\n\"\n                            f\"\ud83d\udcbe Peak memory: {self._get_memory_usage():.1f}MB\\n\\n\"\n                        )\n                        \n                        if isinstance(results, list) and len(results) > 0:\n                            result_message += f\"\ud83d\udcdd Sample result:\\n{results[0][:80]}...\"\n                        else:\n                            result_message += \"\ud83d\udcdd Results written directly to file for memory efficiency\"\n                        \n                        self._update_result_display(result_message)\n                        messagebox.showinfo(\"Ho\u00e0n th\u00e0nh\", \n                            f\"\ud83c\udf89 X\u1eed l\u00fd Excel th\u00e0nh c\u00f4ng!\\n\\n\"\n                            f\"\u2705 Processed: {success_count:,} rows\\n\"\n                            f\"\u274c Errors: {error_count:,} rows\\n\\n\"\n                            f\"File \u0111\u00e3 l\u01b0u:\\n{output_file}\")\n                \n                except Exception as e:\n                    if not self.processing_cancelled:\n                        progress_window.destroy()\n                        messagebox.showerror(\"L\u1ed7i X\u1eed l\u00fd\", f\"L\u1ed7i x\u1eed l\u00fd Excel: {str(e)}\")\n            \n            # Start processing thread\n            thread = threading.Thread(target=process_thread)\n            thread.daemon = True\n            thread.start()\n        \n        except Exception as e:\n            messagebox.showerror(\"L\u1ed7i X\u1eed l\u00fd\", f\"L\u1ed7i x\u1eed l\u00fd Excel: {str(e)}\")\n    \n    def _create_progress_window(self, title):\n        \"\"\"Create progress dialog window\"\"\"\n        progress_window = tk.Toplevel(self.window)\n        progress_window.title(title)\n        progress_window.geometry(\"450x180\")\n        progress_window.resizable(False, False)\n        progress_window.grab_set()\n        progress_window.transient(self.window)\n        \n        # Title\n        tk.Label(progress_window, text=title, font=(\"Arial\", 12, \"bold\")).pack(pady=10)\n        \n        # Progress bar\n        self.progress_var = tk.DoubleVar()\n        progress_bar = ttk.Progressbar(\n            progress_window, variable=self.progress_var, \n            maximum=100, length=350, mode='determinate'\n        )\n        progress_bar.pack(pady=10)\n        \n        # Progress label\n        self.progress_label = tk.Label(progress_window, text=\"Chu\u1ea9n b\u1ecb...\", font=(\"Arial\", 10))\n        self.progress_label.pack(pady=5)\n        \n        # Warning\n        warning_label = tk.Label(\n            progress_window, \n            text=\"\u26a0\ufe0f \u0110\u1eebng \u0111\u00f3ng c\u1eeda s\u1ed5! \u0110ang x\u1eed l\u00fd v\u1edbi anti-crash protection.\",\n            font=(\"Arial\", 8), fg=\"#FF9800\"\n        )\n        warning_label.pack(pady=5)\n        \n        # Cancel button\n        def cancel_processing():\n            self.processing_cancelled = True\n            messagebox.showinfo(\"\u0110\u00e3 h\u1ee7y\", \"\u0110\u00e3 y\u00eau c\u1ea7u h\u1ee7y x\u1eed l\u00fd. Vui l\u00f2ng \u0111\u1ee3i...\")\n            progress_window.after(2000, progress_window.destroy)\n        \n        tk.Button(progress_window, text=\"\ud83d\uded1 H\u1ee7y\", command=cancel_processing,\n                 bg=\"#F44336\", fg=\"white\", font=(\"Arial\", 10)).pack(pady=10)\n        \n        return progress_window\n    \n    def _export_excel(self):\n        \"\"\"Xu\u1ea5t k\u1ebft qu\u1ea3 ra Excel\"\"\"\n        try:\n            if not self.geometry_service:\n                messagebox.showerror(\"L\u1ed7i\", \"GeometryService ch\u01b0a s\u1eb5n s\u00e0ng!\")\n                return\n            \n            final_result = self.geometry_service.generate_final_result()\n            if not final_result:\n                messagebox.showwarning(\"C\u1ea3nh b\u00e1o\", \"Ch\u01b0a c\u00f3 k\u1ebft qu\u1ea3 n\u00e0o \u0111\u1ec3 xu\u1ea5t!\\n\\nVui l\u00f2ng th\u1ef1c thi t\u00ednh to\u00e1n tr\u01b0\u1edbc.\")\n                return\n            \n            default_name = f\"geometry_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx\"\n            output_path = filedialog.asksaveasfilename(\n                title=\"Xu\u1ea5t k\u1ebft qu\u1ea3 ra Excel\",\n                defaultextension=\".xlsx\",\n                filetypes=[(\"Excel files\", \"*.xlsx\")],\n                initialvalue=default_name\n            )\n            \n            if not output_path:\n                return\n            \n            exported_file = self.geometry_service.export_single_result(output_path)\n            messagebox.showinfo(\"Xu\u1ea5t th\u00e0nh c\u00f4ng\", f\"K\u1ebft qu\u1ea3 \u0111\u00e3 l\u01b0u t\u1ea1i:\\n{exported_file}\")\n            \n        except Exception as e:\n            messagebox.showerror(\"L\u1ed7i Xu\u1ea5t\", f\"L\u1ed7i xu\u1ea5t Excel: {str(e)}\")\n    \n    def _create_template(self):\n        \"\"\"Create Excel template\"\"\"\n        try:\n            shape_a = self.dropdown1_var.get()\n            shape_b = self.dropdown2_var.get() if self.pheptoan_var.get() not in [\"Di\u1ec7n t\u00edch\", \"Th\u1ec3 t\u00edch\"] else None\n            \n            if not shape_a:\n                messagebox.showwarning(\"C\u1ea3nh b\u00e1o\", \"Vui l\u00f2ng ch\u1ecdn h\u00ecnh d\u1ea1ng tr\u01b0\u1edbc!\")\n                return\n            \n            template_name = f\"template_{shape_a}\" + (f\"_{shape_b}\" if shape_b else \"\") + f\"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx\"\n            \n            output_path = filedialog.asksaveasfilename(\n                title=\"L\u01b0u template Excel\",\n                defaultextension=\".xlsx\",\n                filetypes=[(\"Excel files\", \"*.xlsx\")],\n                initialvalue=template_name\n            )\n            \n            if not output_path:\n                return\n            \n            template_file = self.geometry_service.create_excel_template_for_geometry(shape_a, shape_b, output_path)\n            \n            messagebox.showinfo(\"T\u1ea1o template th\u00e0nh c\u00f4ng\", \n                f\"Template Excel \u0111\u00e3 t\u1ea1o t\u1ea1i:\\n{template_file}\\n\\n\"\n                f\"B\u1ea1n c\u00f3 th\u1ec3 \u0111i\u1ec1n d\u1eef li\u1ec7u v\u00e0o template n\u00e0y r\u1ed3i import l\u1ea1i.\\n\\n\"\n                f\"\ud83d\udca1 Tip: Template h\u1ed7 tr\u1ee3 \u0111\u1ebfn 250,000 d\u00f2ng v\u1edbi anti-crash system!\")\n            \n        except Exception as e:\n            messagebox.showerror(\"L\u1ed7i\", f\"L\u1ed7i t\u1ea1o template: {str(e)}\")\n    \n    def _quit_import_mode(self):\n        \"\"\"Tho\u00e1t ch\u1ebf \u0111\u1ed9 import v\u00e0 quay l\u1ea1i manual\"\"\"\n        try:\n            result = messagebox.askyesno(\"Tho\u00e1t ch\u1ebf \u0111\u1ed9 import\", \n                \"B\u1ea1n c\u00f3 ch\u1eafc mu\u1ed1n tho\u00e1t ch\u1ebf \u0111\u1ed9 import Excel v\u00e0 quay l\u1ea1i nh\u1eadp th\u1ee7 c\u00f4ng?\")\n            \n            if result:\n                self.imported_data = False\n                self.imported_file_path = \"\"\n                self.imported_file_name = \"\"\n                self.manual_data_entered = False\n                self.is_large_file = False\n                \n                self._unlock_and_clear_inputs()\n                self._hide_action_buttons()\n                \n                self._update_result_display(\"\u2728 \u0110\u00e3 quay l\u1ea1i ch\u1ebf \u0111\u1ed9 nh\u1eadp th\u1ee7 c\u00f4ng.\\nNh\u1eadp d\u1eef li\u1ec7u v\u00e0o c\u00e1c \u00f4 tr\u00ean \u0111\u1ec3 b\u1eaft \u0111\u1ea7u.\")\n                self.excel_status_label.config(text=\"\ud83d\udcca Excel: \u2705 Ready\")\n        \n        except Exception as e:\n            messagebox.showerror(\"L\u1ed7i\", f\"L\u1ed7i tho\u00e1t ch\u1ebf \u0111\u1ed9 import: {str(e)}\")\n    \n    def _clear_and_lock_inputs(self):\n        \"\"\"Clear and lock all input fields when Excel is imported\"\"\"\n        entries = self._get_all_input_entries()\n        for entry in entries:\n            try:\n                entry.delete(0, tk.END)\n                entry.config(state='disabled', bg='#E0E0E0')\n            except:\n                pass\n    \n    def _unlock_and_clear_inputs(self):\n        \"\"\"Unlock and clear all input fields for manual input\"\"\"\n        entries = self._get_all_input_entries()\n        for entry in entries:\n            try:\n                entry.config(state='normal', bg='white')\n                entry.delete(0, tk.END)\n            except:\n                pass\n    \n    def _update_result_display(self, message):\n        \"\"\"C\u1eadp nh\u1eadt hi\u1ec3n th\u1ecb k\u1ebft qu\u1ea3 v\u1edbi m\u00e0u s\u1eafc\"\"\"\n        self.entry_tong.delete(1.0, tk.END)\n        self.entry_tong.insert(tk.END, message)\n        \n        # Color coding\n        if \"L\u1ed7i\" in message or \"l\u1ed7i\" in message:\n            self.entry_tong.config(bg=\"#FFEBEE\", fg=\"#D32F2F\")\n        elif \"\u0110\u00e3 import\" in message or \"Ho\u00e0n th\u00e0nh\" in message:\n            self.entry_tong.config(bg=\"#E8F5E8\", fg=\"#388E3C\")\n        elif \"\u0110ang x\u1eed l\u00fd\" in message:\n            self.entry_tong.config(bg=\"#FFF3E0\", fg=\"#F57C00\")\n        else:\n            self.entry_tong.config(bg=\"#F8F9FA\", fg=\"#2E86AB\")\n    \n    def _show_ready_message(self):\n        \"\"\"Hi\u1ec3n th\u00f4ng b\u00e1o s\u1eb5n s\u00e0ng\"\"\"\n        if self.geometry_service:\n            message = \"\u2728 Geometry Mode v2.1 - Anti-Crash Excel! \ud83d\udcaa\\n\\n\"\n            message += \"\ud83d\udcdd Ch\u1ebf \u0111\u1ed9 th\u1ee7 c\u00f4ng: Nh\u1eadp d\u1eef li\u1ec7u v\u00e0o c\u00e1c \u00f4, b\u1ea5m 'Th\u1ef1c thi t\u1ea5t c\u1ea3'\\n\"\n            message += \"\ud83d\udcc1 Ch\u1ebf \u0111\u1ed9 Excel: B\u1ea5m 'Import Excel' ch\u1ecdn file, r\u1ed3i 'X\u1eed l\u00fd File Excel'\\n\\n\"\n            message += \"\ud83d\udd25 NEW: Enhanced Import Logic\\n\"\n            message += \"\u2705 Import ch\u1ec9 l\u01b0u t\u00ean file (nhanh)\\n\"\n            message += \"\u2705 \u0110\u1ecdc file ch\u1ec9 khi x\u1eed l\u00fd (ti\u1ebft ki\u1ec7m memory)\\n\"\n            message += \"\u2705 Auto-detect large files (250k rows limit)\\n\"\n            message += \"\u2705 Crash protection v\u1edbi memory monitoring\\n\\n\"\n            message += \"\ud83d\udca1 T\u00ednh n\u0103ng: Import-defer-read, Batch, Chunked, Anti-Crash\"\n        else:\n            message = \"\u26a0\ufe0f GeometryService kh\u00f4ng kh\u1edfi t\u1ea1o \u0111\u01b0\u1ee3c.\\nVui l\u00f2ng ki\u1ec3m tra c\u00e0i \u0111\u1eb7t!\"\n        \n        self.entry_tong.insert(tk.END, message)\n\n    def _setup_control_frame(self):\n        \"\"\"Setup control frame v\u1edbi buttons v\u00e0 result display\"\"\"\n        self.frame_tong = tk.LabelFrame(\n            self.main_container, text=\"\ud83c\udf89 K\u1ebeT QU\u1ea2 & \u0110I\u1ec0U KHI\u1ec2N\",\n            bg=\"#FFFFFF\", font=(\"Arial\", 10, \"bold\")\n        )\n        self.frame_tong.grid(row=8, column=0, columnspan=4, padx=10, pady=10, sticky=\"we\")\n\n        # Text widget hi\u1ec3n th\u1ecb k\u1ebft qu\u1ea3\n        self.entry_tong = tk.Text(\n            self.main_container,\n            width=80, height=8,\n            font=(\"Courier New\", 9), wrap=tk.WORD,\n            bg=\"#F8F9FA\", fg=\"black\",\n            relief=\"solid\", bd=1, padx=5, pady=5\n        )\n        self.entry_tong.grid(row=9, column=0, columnspan=4, padx=5, pady=5, sticky=\"we\")\n\n        # N\u00fat Import Excel\n        self.btn_import_excel = tk.Button(\n            self.frame_tong, text=\"\ud83d\udcc1 Import Excel (Fast Select - 250k limit!)\",\n            command=self._import_excel,\n            bg=\"#FF9800\", fg=\"white\", font=(\"Arial\", 9, \"bold\")\n        )\n        self.btn_import_excel.grid(row=0, column=0, columnspan=4, pady=5, sticky=\"we\")\n\n        # Frame cho n\u00fat th\u1ee7 c\u00f4ng\n        self.frame_buttons_manual = tk.Frame(self.frame_tong, bg=\"#FFFFFF\")\n        self.frame_buttons_manual.grid(row=1, column=0, columnspan=4, pady=5, sticky=\"we\")\n\n        tk.Button(self.frame_buttons_manual, text=\"\ud83d\udd04 X\u1eed l\u00fd Nh\u00f3m A\",\n                  command=self._process_group_A,\n                  bg=\"#2196F3\", fg=\"white\", font=(\"Arial\", 9)).grid(row=0, column=0, padx=5)\n        tk.Button(self.frame_buttons_manual, text=\"\ud83d\udd04 X\u1eed l\u00fd Nh\u00f3m B\",\n                  command=self._process_group_B,\n                  bg=\"#2196F3\", fg=\"white\", font=(\"Arial\", 9)).grid(row=0, column=1, padx=5)\n        tk.Button(self.frame_buttons_manual, text=\"\ud83d\ude80 Th\u1ef1c thi t\u1ea5t c\u1ea3\",\n                  command=self._process_all,\n                  bg=\"#4CAF50\", fg=\"white\", font=(\"Arial\", 9, \"bold\")).grid(row=0, column=2, padx=5)\n        tk.Button(self.frame_buttons_manual, text=\"\ud83d\udcbe Xu\u1ea5t Excel\",\n                  command=self._export_excel,\n                  bg=\"#FF9800\", fg=\"white\", font=(\"Arial\", 9, \"bold\")).grid(row=0, column=3, padx=5)\n        \n        # Frame cho n\u00fat import mode\n        self.frame_buttons_import = tk.Frame(self.frame_tong, bg=\"#FFFFFF\")\n        self.frame_buttons_import.grid(row=1, column=0, columnspan=4, pady=5, sticky=\"we\")\n        \n        tk.Button(self.frame_buttons_import, text=\"\ud83d\udd25 X\u1eed l\u00fd File Excel\",\n                  command=self._process_excel_batch,\n                  bg=\"#F44336\", fg=\"white\", font=(\"Arial\", 9, \"bold\")).grid(row=0, column=0, padx=5)\n        tk.Button(self.frame_buttons_import, text=\"\ud83d\udcc1 Import File Kh\u00e1c\",\n                  command=self._import_excel,\n                  bg=\"#2196F3\", fg=\"white\", font=(\"Arial\", 9)).grid(row=0, column=1, padx=5)\n        tk.Button(self.frame_buttons_import, text=\"\ud83d\udcdd T\u1ea1o Template\",\n                  command=self._create_template,\n                  bg=\"#9C27B0\", fg=\"white\", font=(\"Arial\", 9)).grid(row=0, column=2, padx=5)\n        tk.Button(self.frame_buttons_import, text=\"\u21a9\ufe0f Quay l\u1ea1i\",\n                  command=self._quit_import_mode,\n                  bg=\"#607D8B\", fg=\"white\", font=(\"Arial\", 9)).grid(row=0, column=3, padx=5)\n        \n        # Initially hide import buttons\n        self.frame_buttons_import.grid_remove()\n        self.frame_buttons_manual.grid_remove()


if __name__ == \"__main__\":\n    root = tk.Tk()\n    app = GeometryView(root)\n    root.mainloop()\n