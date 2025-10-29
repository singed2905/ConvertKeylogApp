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
        self.manual_data_entered = False
        self.processing_cancelled = False
        self.is_large_file = False  # NEW: Track if current file is large
        
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
        """Tạo header với Large File status"""
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

        # Operation selector - lấy từ service
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

        # Phiên bản và status
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
        
        # Excel status indicator - Enhanced for large files
        self.excel_status_label = tk.Label(
            center_section, text="📊 Excel: ✅ Ready", font=("Arial", 8),
            bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["success"]
        )
        self.excel_status_label.pack(side="bottom")
        
        # Memory status indicator - NEW!
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
        # NHÓM A - Tất cả 5 hình
        self._create_point_frame_A()
        self._create_line_frame_A()
        self._create_plane_frame_A()
        self._create_circle_frame_A()
        self._create_sphere_frame_A()
        
        # NHÓM B - Tất cả 5 hình
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
        
        # Dòng 1: a, b
        tk.Label(self.frame_A_plane, text="a:", bg="#FFFFFF", width=3).grid(row=1, column=0, sticky="e")
        self.entry_a_A = tk.Entry(self.frame_A_plane, width=15)
        self.entry_a_A.grid(row=1, column=1, padx=5)
        
        tk.Label(self.frame_A_plane, text="b:", bg="#FFFFFF", width=3).grid(row=1, column=2, sticky="e")
        self.entry_b_A = tk.Entry(self.frame_A_plane, width=15)
        self.entry_b_A.grid(row=1, column=3, padx=5)
        
        # Dòng 2: c, d
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
        
        # Dòng 1: a, b
        tk.Label(self.frame_B_plane, text="a:", bg="#FFFFFF", width=3).grid(row=1, column=0, sticky="e")
        self.entry_a_B = tk.Entry(self.frame_B_plane, width=15)
        self.entry_a_B.grid(row=1, column=1, padx=5)
        
        tk.Label(self.frame_B_plane, text="b:", bg="#FFFFFF", width=3).grid(row=1, column=2, sticky="e")
        self.entry_b_B = tk.Entry(self.frame_B_plane, width=15)
        self.entry_b_B.grid(row=1, column=3, padx=5)
        
        # Dòng 2: c, d
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
        """Lấy dữ liệu nhập cho nhóm A - Đầy đủ 5 hình"""
        shape = self.dropdown1_var.get()
        data = {}
        
        if shape == "Điểm":
            data['point_input'] = self.entry_diem_A.get() if hasattr(self, 'entry_diem_A') else ''
        elif shape == "Đường thẳng":
            data['line_A1'] = self.entry_point_A.get() if hasattr(self, 'entry_point_A') else ''
            data['line_X1'] = self.entry_vector_A.get() if hasattr(self, 'entry_vector_A') else ''
        elif shape == "Mặt phẳng":
            data['plane_a'] = self.entry_a_A.get() if hasattr(self, 'entry_a_A') else ''
            data['plane_b'] = self.entry_b_A.get() if hasattr(self, 'entry_b_A') else ''
            data['plane_c'] = self.entry_c_A.get() if hasattr(self, 'entry_c_A') else ''
            data['plane_d'] = self.entry_d_A.get() if hasattr(self, 'entry_d_A') else ''
        elif shape == "Đường tròn":
            data['circle_center'] = self.entry_center_A.get() if hasattr(self, 'entry_center_A') else ''
            data['circle_radius'] = self.entry_radius_A.get() if hasattr(self, 'entry_radius_A') else ''
        elif shape == "Mặt cầu":
            data['sphere_center'] = self.entry_sphere_center_A.get() if hasattr(self, 'entry_sphere_center_A') else ''
            data['sphere_radius'] = self.entry_sphere_radius_A.get() if hasattr(self, 'entry_sphere_radius_A') else ''
        
        return data
    
    def _get_input_data_B(self):
        """Lấy dữ liệu nhập cho nhóm B - Đầy đủ 5 hình"""
        shape = self.dropdown2_var.get()
        data = {}
        
        if shape == "Điểm":
            data['point_input'] = self.entry_diem_B.get() if hasattr(self, 'entry_diem_B') else ''
        elif shape == "Đường thẳng":
            data['line_A2'] = self.entry_point_B.get() if hasattr(self, 'entry_point_B') else ''
            data['line_X2'] = self.entry_vector_B.get() if hasattr(self, 'entry_vector_B') else ''
        elif shape == "Mặt phẳng":
            data['plane_a'] = self.entry_a_B.get() if hasattr(self, 'entry_a_B') else ''
            data['plane_b'] = self.entry_b_B.get() if hasattr(self, 'entry_b_B') else ''
            data['plane_c'] = self.entry_c_B.get() if hasattr(self, 'entry_c_B') else ''
            data['plane_d'] = self.entry_d_B.get() if hasattr(self, 'entry_d_B') else ''
        elif shape == "Đường tròn":
            data['circle_center'] = self.entry_center_B.get() if hasattr(self, 'entry_center_B') else ''
            data['circle_radius'] = self.entry_radius_B.get() if hasattr(self, 'entry_radius_B') else ''
        elif shape == "Mặt cầu":
            data['sphere_center'] = self.entry_sphere_center_B.get() if hasattr(self, 'entry_sphere_center_B') else ''
            data['sphere_radius'] = self.entry_sphere_radius_B.get() if hasattr(self, 'entry_sphere_radius_B') else ''
        
        return data
    
    # ========== PROCESSING METHODS ==========
    def _process_group_A(self):
        """Xử lý nhóm A"""
        try:
            if not self.geometry_service:
                messagebox.showerror("Lỗi", "GeometryService chưa được khởi tạo!")
                return
            
            data_A = self._get_input_data_A()
            result = self.geometry_service.thuc_thi_A(data_A)
            self._update_result_display(f"Nhóm A đã xử lý: {result}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý nhóm A: {str(e)}")
    
    def _process_group_B(self):
        """Xử lý nhóm B"""
        try:
            if not self.geometry_service:
                messagebox.showerror("Lỗi", "GeometryService chưa được khởi tạo!")
                return
                
            data_B = self._get_input_data_B()
            result = self.geometry_service.thuc_thi_B(data_B)
            self._update_result_display(f"Nhóm B đã xử lý: {result}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý nhóm B: {str(e)}")
    
    def _process_all(self):
        """Thực thi tất cả - Core function!"""
        try:
            if not self.geometry_service:
                messagebox.showerror("Lỗi", "GeometryService chưa được khởi tạo!")
                return
            
            # Kiểm tra xem đã chọn phép toán và hình dạng chưa
            if not self.pheptoan_var.get():
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn phép toán!")
                return
            
            if not self.dropdown1_var.get():
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn hình dạng cho nhóm A!")
                return
            
            # Lấy dữ liệu
            data_A = self._get_input_data_A()
            data_B = self._get_input_data_B()
            
            # Xử lý
            result_A, result_B = self.geometry_service.thuc_thi_tat_ca(data_A, data_B)
            
            # Sinh kết quả cuối cùng
            final_result = self.geometry_service.generate_final_result()
            
            # Hiển thị kết quả - matching TL style
            message = f"✨ Kết quả mã hóa (cho máy tính):\n{final_result}\n\n"
            message += f"📈 Chi tiết xử lý:\n"
            message += f"Phép toán: {self.pheptoan_var.get()}\n"
            message += f"Nhóm A ({self.dropdown1_var.get()}): {result_A}\n"
            if self.pheptoan_var.get() not in ["Diện tích", "Thể tích"]:
                message += f"Nhóm B ({self.dropdown2_var.get()}): {result_B}"
            
            self._update_result_display(message)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi thực thi: {str(e)}")
    
    # ========== ENHANCED EXCEL METHODS - CRASH-PROOF! ==========
    def _import_excel(self):
        """Import dữ liệu từ Excel - Enhanced with crash protection!"""
        try:
            file_path = filedialog.askopenfilename(
                title="Chọn file Excel",
                filetypes=[("Excel files", "*.xlsx *.xls")]
            )
            
            if not file_path:
                return
            
            # Pre-check file size and warn user
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if file_size_mb > 50:
                proceed = messagebox.askyesno(
                    "File rất lớn!", 
                    f"File có kích thước: {file_size_mb:.1f}MB\n"
                    f"Đây có thể là file rất lớn (200k+ dòng).\n\n"
                    f"💪 ConvertKeylogApp v2.1 có thể xử lý file này nhờ:\n"
                    f"✅ Memory-optimized streaming\n"
                    f"✅ Chunked processing\n"
                    f"✅ Crash protection\n\n"
                    f"Tiếp tục import?"
                )
                if not proceed:
                    return
            
            # Get file info with large file detection
            file_info = self.geometry_service.get_excel_file_info(file_path)
            
            if file_info.get('is_large_file', False):
                self.is_large_file = True
                # Show large file specific info
                info_message = f"🔥 LARGE FILE DETECTED!\n\n"
                info_message += f"📊 File: {file_info['file_name']}\n"
                info_message += f"📏 Size: {file_info['file_size_mb']:.1f}MB\n"
                info_message += f"📈 Rows: {file_info.get('estimated_rows', 'Unknown'):,}\n"
                info_message += f"🎯 Columns: {file_info['total_columns']}\n\n"
                info_message += f"💡 Recommended chunk: {file_info.get('recommended_chunk_size', 500)}\n\n"
                info_message += f"⚡ Large File Mode will be used automatically!"
            else:
                self.is_large_file = False
                # Normal file info
                info_message = f"📁 File: {file_info['file_name']}\n"
                info_message += f"📏 Dòng: {file_info['total_rows']}\n"
                info_message += f"📊 Cột: {file_info['total_columns']}\n"
                info_message += f"💾 Kích thước: {file_info['file_size_mb']:.1f}MB\n\n"
                info_message += "Các cột: " + ", ".join(file_info['columns'][:5])
                if len(file_info['columns']) > 5:
                    info_message += f" (và {len(file_info['columns'])-5} cột khác)"
            
            proceed = messagebox.askyesno("Thông tin File", f"{info_message}\n\nTiếp tục import?")
            if not proceed:
                return
            
            # Validate file structure
            shape_a = self.dropdown1_var.get()
            shape_b = self.dropdown2_var.get() if self.pheptoan_var.get() not in ["Diện tích", "Thể tích"] else None
            
            validation_result = self.geometry_service.validate_excel_file_for_geometry(file_path, shape_a, shape_b)
            
            if not validation_result['valid']:
                error_message = "File Excel không hợp lệ!\n\n"
                if 'structure_issues' in validation_result:
                    error_message += "Thiếu các cột: " + ", ".join(validation_result['structure_issues'])
                if 'error' in validation_result:
                    error_message += f"Lỗi: {validation_result['error']}"
                
                # Offer to create template
                result = messagebox.askyesnocancel("File không hợp lệ", 
                    f"{error_message}\n\nBạn có muốn tạo template mẫu không?")
                
                if result:  # Yes - create template
                    self._create_template()
                return
            
            # File is valid - proceed with import
            self.imported_file_path = file_path
            self.imported_data = True
            self.manual_data_entered = False
            
            # Clear manual inputs and lock them
            self._clear_and_lock_inputs()
            
            # Show appropriate buttons based on file size
            self._show_import_buttons()
            
            # Update status
            if self.is_large_file:
                status_message = f"🔥 Large File imported: {file_info['file_name']}\n"
                status_message += f"📈 {file_info.get('estimated_rows', 'Unknown'):,} rows\n"
                status_message += f"💪 Anti-crash mode ENABLED!\n"
                status_message += f"⚡ Ready for streaming batch processing!"
                
                self.excel_status_label.config(text=f"Excel: 🔥 {file_info['file_name'][:15]}...")
            else:
                quality_info = validation_result.get('quality_issues', {})
                status_message = f"📁 Đã import: {file_info['file_name']}\n"
                status_message += f"Dòng có dữ liệu: {quality_info.get('rows_with_data', 0)}/{file_info['total_rows']}\n"
                status_message += f"Sẵn sàng xử lý hàng loạt!"
                
                self.excel_status_label.config(text=f"Excel: 📁 {file_info['file_name'][:15]}...")
            
            self._update_result_display(status_message)
            
        except Exception as e:
            messagebox.showerror("Lỗi Import", f"Lỗi import Excel: {str(e)}")
    
    def _process_excel_batch(self):
        """Process imported Excel file - Enhanced with crash protection!"""
        try:
            if not self.imported_data or not self.imported_file_path:
                messagebox.showwarning("Cảnh báo", "Chưa import file Excel nào!")
                return
            
            if not self.geometry_service:
                messagebox.showerror("Lỗi", "GeometryService chưa sẵn sàng!")
                return
            
            # Get processing info
            processing_info = self.geometry_service.get_large_file_processing_info(self.imported_file_path)
            
            if processing_info.get('is_large_file', False):
                # Large file processing
                self._process_large_file_with_options(processing_info)
            else:
                # Normal file processing
                self._process_normal_file()
                
        except Exception as e:
            messagebox.showerror("Lỗi Xử lý", f"Lỗi xử lý Excel: {str(e)}")
    
    def _process_large_file_with_options(self, processing_info):
        """Process large file with user options"""
        try:
            file_info = processing_info['file_info']
            recommended_chunk = processing_info['recommended_chunk_size']
            
            # Show large file processing dialog
            large_file_message = f"🔥 LARGE FILE PROCESSING\n\n"
            large_file_message += f"📊 Size: {file_info['file_size_mb']:.1f}MB\n"
            large_file_message += f"📈 Rows: ~{file_info['estimated_rows']:,}\n"
            large_file_message += f"💡 Recommended chunk: {recommended_chunk}\n\n"
            large_file_message += f"💪 Anti-crash features:\n"
            large_file_message += f"✅ Memory monitoring\n"
            large_file_message += f"✅ Streaming processing\n"
            large_file_message += f"✅ Emergency cleanup\n"
            large_file_message += f"✅ Progress tracking\n\n"
            large_file_message += f"⚡ This may take several minutes..."
            
            proceed = messagebox.askyesno("Large File Processing", large_file_message)
            if not proceed:
                return
            
            # Choose output file
            original_name = os.path.splitext(os.path.basename(self.imported_file_path))[0]
            default_output = f"{original_name}_large_encoded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            output_path = filedialog.asksaveasfilename(
                title="Chọn nơi lưu kết quả (Large File)",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialvalue=default_output
            )
            
            if not output_path:
                return
            
            # Get current settings
            shape_a = self.dropdown1_var.get()
            shape_b = self.dropdown2_var.get() if self.pheptoan_var.get() not in ["Diện tích", "Thể tích"] else None
            operation = self.pheptoan_var.get()
            dimension_a = self.kich_thuoc_A_var.get()
            dimension_b = self.kich_thuoc_B_var.get()
            
            # Process using large file processor
            self._process_large_file_background(output_path, shape_a, shape_b, operation, dimension_a, dimension_b)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý file lớn: {str(e)}")
    
    def _process_large_file_background(self, output_path, shape_a, shape_b, operation, dimension_a, dimension_b):
        """Process large file in background with progress tracking"""
        try:
            # Show enhanced progress window for large files
            progress_window = self._create_large_file_progress_window()
            
            def progress_callback(progress, processed, total, errors):
                if hasattr(self, 'progress_var') and not self.processing_cancelled:
                    try:
                        self.progress_var.set(progress)
                        memory_usage = self._get_memory_usage()
                        
                        # Enhanced progress display
                        progress_text = f"Đang xử lý: {processed:,}/{total:,} dòng\n"
                        progress_text += f"Lỗi: {errors:,}\n"
                        progress_text += f"Memory: {memory_usage:.1f}MB"
                        
                        self.progress_label.config(text=progress_text)
                        
                        # Update memory status in main window
                        if memory_usage > 800:
                            self.memory_status_label.config(text=f"💾 Memory: {memory_usage:.1f}MB (🔥 High)", fg="#F44336")
                        elif memory_usage > 500:
                            self.memory_status_label.config(text=f"💾 Memory: {memory_usage:.1f}MB (⚠️ Medium)", fg="#FF9800")
                        else:
                            self.memory_status_label.config(text=f"💾 Memory: {memory_usage:.1f}MB (✅ OK)", fg="#4CAF50")
                        
                        progress_window.update()
                    except Exception:
                        pass
            
            # Process in background thread
            def process_thread():
                try:
                    # Use the enhanced batch processor which auto-detects large files
                    results, output_file, success_count, error_count = self.geometry_service.process_excel_batch(
                        self.imported_file_path, shape_a, shape_b, operation, 
                        dimension_a, dimension_b, output_path, progress_callback
                    )
                    
                    # Close progress window
                    if not self.processing_cancelled:
                        progress_window.destroy()
                        
                        # Show success results
                        result_message = f"🎉 LARGE FILE PROCESSED SUCCESSFULLY!\n\n"
                        result_message += f"📁 Output: {os.path.basename(output_file)}\n"
                        result_message += f"✅ Success: {success_count:,} rows\n"
                        result_message += f"❌ Errors: {error_count:,} rows\n"
                        result_message += f"💾 Peak memory: {self._get_memory_usage():.1f}MB\n\n"
                        
                        if isinstance(results, list) and len(results) > 0:
                            result_message += f"📝 Sample result:\n{results[0][:80]}..."
                        else:
                            result_message += f"📝 Results written directly to file for memory efficiency"
                        
                        self._update_result_display(result_message)
                        messagebox.showinfo("Large File Complete!", 
                            f"🎉 Xử lý file lớn thành công!\n\n"
                            f"✅ Processed: {success_count:,} rows\n"
                            f"❌ Errors: {error_count:,} rows\n\n"
                            f"File đã lưu:\n{output_file}")
                    
                except Exception as e:
                    if not self.processing_cancelled:
                        progress_window.destroy()
                        messagebox.showerror("Lỗi Large File", f"Lỗi xử lý file lớn: {str(e)}")
            
            # Start processing thread
            thread = threading.Thread(target=process_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khởi tạo xử lý file lớn: {str(e)}")
    
    def _process_normal_file(self):
        """Process normal sized file"""
        try:
            # Choose output file
            original_name = os.path.splitext(os.path.basename(self.imported_file_path))[0]
            default_output = f"{original_name}_encoded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            output_path = filedialog.asksaveasfilename(
                title="Chọn nơi lưu kết quả",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialvalue=default_output
            )
            
            if not output_path:
                return
            
            # Get current settings
            shape_a = self.dropdown1_var.get()
            shape_b = self.dropdown2_var.get() if self.pheptoan_var.get() not in ["Diện tích", "Thể tích"] else None
            operation = self.pheptoan_var.get()
            dimension_a = self.kich_thuoc_A_var.get()
            dimension_b = self.kich_thuoc_B_var.get()
            
            # Show progress window
            progress_window = self._create_progress_window("Xử lý file Excel...")
            
            def progress_callback(progress, processed, total, errors):
                if hasattr(self, 'progress_var'):
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"Đang xử lý: {processed}/{total} dòng ({errors} lỗi)")
                    progress_window.update()
            
            # Process in background thread
            def process_thread():
                try:
                    results, output_file, success_count, error_count = self.geometry_service.process_excel_batch(
                        self.imported_file_path, shape_a, shape_b, operation, 
                        dimension_a, dimension_b, output_path, progress_callback
                    )
                    
                    # Close progress window
                    progress_window.destroy()
                    
                    # Show results
                    result_message = f"🎉 Hoàn thành xử lý Excel!\n\n"
                    result_message += f"File kết quả: {os.path.basename(output_file)}\n"
                    result_message += f"Thành công: {success_count} dòng\n"
                    result_message += f"Lỗi: {error_count} dòng\n\n"
                    
                    if isinstance(results, list) and len(results) > 0:
                        result_message += f"Mẫu kết quả đầu tiên:\n{results[0][:100]}..."
                    
                    self._update_result_display(result_message)
                    messagebox.showinfo("Hoàn thành", f"Xử lý thành công!\n\nFile đã lưu: {output_file}")
                    
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("Lỗi", f"Lỗi xử lý: {str(e)}")
            
            # Start processing thread
            thread = threading.Thread(target=process_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý file thường: {str(e)}")
    
    def _create_large_file_progress_window(self):
        """Create enhanced progress window for large files"""
        progress_window = tk.Toplevel(self.window)
        progress_window.title("🔥 Large File Processing - Anti-Crash Mode")
        progress_window.geometry("500x200")
        progress_window.resizable(False, False)
        progress_window.grab_set()
        
        # Center the window
        progress_window.transient(self.window)
        
        # Title
        tk.Label(progress_window, text="🔥 Large File Processing", 
                font=("Arial", 14, "bold"), fg="#F44336").pack(pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            progress_window, variable=self.progress_var, 
            maximum=100, length=400, mode='determinate'
        )
        progress_bar.pack(pady=10)
        
        # Progress label
        self.progress_label = tk.Label(progress_window, text="Chuẩn bị...", font=("Arial", 10))
        self.progress_label.pack(pady=5)
        
        # Warning label
        warning_label = tk.Label(
            progress_window, 
            text="⚠️ Đừng đóng cửa sổ này! File đang được xử lý với memory optimization.",
            font=("Arial", 8), fg="#FF9800"
        )
        warning_label.pack(pady=5)
        
        # Cancel button
        def cancel_processing():
            self.processing_cancelled = True
            self.large_file_processor.processing_cancelled = True if hasattr(self, 'large_file_processor') else None
            messagebox.showinfo("Đã hủy", "Đã yêu cầu hủy xử lý. Vui lòng đợi...")
            progress_window.after(3000, progress_window.destroy)  # Auto-close after 3s
        
        tk.Button(progress_window, text="🛑 Hủy xử lý", command=cancel_processing,
                 bg="#F44336", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
        
        return progress_window
    
    def _create_progress_window(self, title):
        """Create standard progress dialog window"""
        progress_window = tk.Toplevel(self.window)
        progress_window.title(title)
        progress_window.geometry("400x150")
        progress_window.resizable(False, False)
        progress_window.grab_set()
        
        # Center the window
        progress_window.transient(self.window)
        
        # Progress bar
        tk.Label(progress_window, text=title, font=("Arial", 12, "bold")).pack(pady=10)
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            progress_window, variable=self.progress_var, 
            maximum=100, length=300, mode='determinate'
        )
        progress_bar.pack(pady=10)
        
        self.progress_label = tk.Label(progress_window, text="Chuẩn bị...", font=("Arial", 10))
        self.progress_label.pack(pady=5)
        
        # Cancel button
        def cancel_processing():
            self.processing_cancelled = True
            progress_window.destroy()
        
        tk.Button(progress_window, text="Hủy", command=cancel_processing,
                 bg="#F44336", fg="white").pack(pady=5)
        
        return progress_window
    
    def _export_excel(self):
        """Xuất kết quả ra Excel - Full implementation!"""
        try:
            if not self.geometry_service:
                messagebox.showerror("Lỗi", "GeometryService chưa sẵn sàng!")
                return
            
            # Check if we have results to export
            final_result = self.geometry_service.generate_final_result()
            if not final_result:
                messagebox.showwarning("Cảnh báo", "Chưa có kết quả nào để xuất!\n\nVui lòng thực thi tính toán trước.")
                return
            
            # Choose output file
            default_name = f"geometry_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            output_path = filedialog.asksaveasfilename(
                title="Xuất kết quả ra Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialvalue=default_name
            )
            
            if not output_path:
                return
            
            # Export current result
            exported_file = self.geometry_service.export_single_result(output_path)
            
            # Show success
            result_summary = self.geometry_service.get_result_summary()
            success_message = f"💾 Xuất Excel thành công!\n\n"
            success_message += f"File: {os.path.basename(exported_file)}\n"
            success_message += f"Phép toán: {result_summary['operation']}\n"
            success_message += f"Nhóm A: {result_summary['shape_A']}\n"
            success_message += f"Nhóm B: {result_summary['shape_B']}\n"
            success_message += f"Kết quả mã hóa: {final_result[:50]}..."
            
            self._update_result_display(success_message)
            messagebox.showinfo("Xuất thành công", f"Kết quả đã lưu tại:\n{exported_file}")
            
        except Exception as e:
            messagebox.showerror("Lỗi Xuất", f"Lỗi xuất Excel: {str(e)}")
    
    def _create_template(self):
        """Create Excel template for current shape selection"""
        try:
            shape_a = self.dropdown1_var.get()
            shape_b = self.dropdown2_var.get() if self.pheptoan_var.get() not in ["Diện tích", "Thể tích"] else None
            
            if not shape_a:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn hình dạng trước!")
                return
            
            # Choose output location
            template_name = f"template_{shape_a}" + (f"_{shape_b}" if shape_b else "") + f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            output_path = filedialog.asksaveasfilename(
                title="Lưu template Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialvalue=template_name
            )
            
            if not output_path:
                return
            
            # Create template
            template_file = self.geometry_service.create_excel_template_for_geometry(shape_a, shape_b, output_path)
            
            messagebox.showinfo("Tạo template thành công", 
                f"Template Excel đã tạo tại:\n{template_file}\n\n"
                f"Bạn có thể điền dữ liệu vào template này rồi import lại.\n\n"
                f"💡 Tip: Template sẽ hoạt động tốt với cả file lớn nhờ anti-crash system!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tạo template: {str(e)}")
    
    def _quit_import_mode(self):
        """Exit import mode and return to manual input"""
        try:
            result = messagebox.askyesno("Thoát chế độ import", 
                "Bạn có chắc muốn thoát chế độ import Excel và quay lại nhập thủ công?")
            
            if result:
                self.imported_data = False
                self.imported_file_path = ""
                self.manual_data_entered = False
                self.is_large_file = False
                
                # Unlock and clear inputs
                self._unlock_and_clear_inputs()
                
                # Hide import buttons
                self._hide_action_buttons()
                
                # Update status
                self._update_result_display("✨ Đã quay lại chế độ nhập thủ công.\nNhập dữ liệu vào các ô trên để bắt đầu.")
                self.excel_status_label.config(text="📊 Excel: ✅ Ready")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi thoát chế độ import: {str(e)}")
    
    def _clear_and_lock_inputs(self):
        """Clear and lock all input fields when Excel is imported"""
        entries = self._get_all_input_entries()
        for entry in entries:
            try:
                entry.delete(0, tk.END)
                entry.config(state='disabled', bg='#E0E0E0')
            except:
                pass
    
    def _unlock_and_clear_inputs(self):
        """Unlock and clear all input fields for manual input"""
        entries = self._get_all_input_entries()
        for entry in entries:
            try:
                entry.config(state='normal', bg='white')
                entry.delete(0, tk.END)
            except:
                pass
    
    def _update_result_display(self, message):
        """Cập nhật hiển thị kết quả với màu sắc"""
        self.entry_tong.delete(1.0, tk.END)
        self.entry_tong.insert(tk.END, message)
        
        # Color coding based on message type
        if "Lỗi" in message or "lỗi" in message or "Lỗi" in message:
            self.entry_tong.config(bg="#FFEBEE", fg="#D32F2F")
        elif "Đã import" in message or "Đã xuất" in message or "Hoàn thành" in message or "SUCCESSFULLY" in message:
            self.entry_tong.config(bg="#E8F5E8", fg="#388E3C")
        elif "Đang xử lý" in message or "PROCESSING" in message:
            self.entry_tong.config(bg="#FFF3E0", fg="#F57C00")
        elif "LARGE FILE" in message or "🔥" in message:
            self.entry_tong.config(bg="#FFF3E0", fg="#F44336")
        else:
            self.entry_tong.config(bg="#F8F9FA", fg="#2E86AB")
    
    def _show_ready_message(self):
        """Hiển thông báo sẵn sàng với Excel features + Large file support"""
        if self.geometry_service:
            message = "✨ Geometry Mode v2.1 - Anti-Crash Excel! 💪\n\n"
            message += "📝 Chế độ thủ công: Nhập dữ liệu vào các ô, bấm 'Thực thi tất cả'\n"
            message += "📁 Chế độ Excel: Bấm 'Import Excel' để xử lý hàng loạt\n\n"
            message += "🔥 NEW: Large File Support\n"
            message += "✅ Memory-optimized streaming\n"
            message += "✅ Crash protection for 200k+ rows\n"
            message += "✅ Auto-detect large files (>20MB or >50k rows)\n"
            message += "✅ Emergency memory cleanup\n\n"
            message += "💡 Tính năng: Import, Batch, Chunked, Validation, Template, Anti-Crash"
        else:
            message = "⚠️ GeometryService không khởi tạo được.\nVui lòng kiểm tra cài đặt!"
        
        self.entry_tong.insert(tk.END, message)

    def _setup_control_frame(self):
        """Setup control frame với buttons và result display"""
        self.frame_tong = tk.LabelFrame(
            self.main_container, text="🎉 KẾT QUẢ & ĐIỀU KHIỂN",
            bg="#FFFFFF", font=("Arial", 10, "bold")
        )
        self.frame_tong.grid(row=8, column=0, columnspan=4, padx=10, pady=10, sticky="we")

        # Text widget hiển thị kết quả
        self.entry_tong = tk.Text(
            self.main_container,
            width=80,
            height=8,  # Increased height for large file messages
            font=("Courier New", 9),
            wrap=tk.WORD,
            bg="#F8F9FA",
            fg="black",
            relief="solid",
            bd=1,
            padx=5,
            pady=5
        )
        self.entry_tong.grid(row=9, column=0, columnspan=4, padx=5, pady=5, sticky="we")

        # Nút Import Excel với large file support
        self.btn_import_excel = tk.Button(
            self.frame_tong, text="📁 Import Excel (Large File Support!)",
            command=self._import_excel,
            bg="#FF9800", fg="white", font=("Arial", 9, "bold")
        )
        self.btn_import_excel.grid(row=0, column=0, columnspan=4, pady=5, sticky="we")

        # Frame cho nút thủ công
        self.frame_buttons_manual = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_manual.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")

        tk.Button(self.frame_buttons_manual, text="🔄 Xử lý Nhóm A",
                  command=self._process_group_A,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons_manual, text="🔄 Xử lý Nhóm B",
                  command=self._process_group_B,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_buttons_manual, text="🚀 Thực thi tất cả",
                  command=self._process_all,
                  bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5)
        tk.Button(self.frame_buttons_manual, text="💾 Xuất Excel",
                  command=self._export_excel,
                  bg="#FF9800", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5)
        
        # Frame cho nút import mode - Enhanced for large files
        self.frame_buttons_import = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_import.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        
        tk.Button(self.frame_buttons_import, text="🔥 Xử lý File Excel",
                  command=self._process_excel_batch,
                  bg="#F44336", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons_import, text="📁 Import File Khác",
                  command=self._import_excel,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_buttons_import, text="📝 Tạo Template",
                  command=self._create_template,
                  bg="#9C27B0", fg="white", font=("Arial", 9)).grid(row=0, column=2, padx=5)
        tk.Button(self.frame_buttons_import, text="↩️ Quay lại",
                  command=self._quit_import_mode,
                  bg="#607D8B", fg="white", font=("Arial", 9)).grid(row=0, column=3, padx=5)
        
        # Initially hide import buttons
        self.frame_buttons_import.grid_remove()
        self.frame_buttons_manual.grid_remove()


if __name__ == "__main__":
    root = tk.Tk()
    app = GeometryView(root)
    root.mainloop()
