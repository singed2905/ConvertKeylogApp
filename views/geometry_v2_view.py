import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
import threading
import os
from datetime import datetime
import psutil

class GeometryV2View:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Geometry V2 Mode - UI Only (No Logic) 🚧")
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
        self.has_result = False  # Track if manual result is available
        
        # Biến và trạng thái
        self._initialize_variables()
        self._setup_ui()
        
        # Đảm bảo hiển thị đúng ngay lần đầu
        self._on_operation_changed()
        self._on_shape_changed()

    def _initialize_service(self):
        """Khởi tạo GeometryService (tạm thời bỏ qua cho Geometry V2)"""
        # TODO: Implement Geometry V2 Service sau
        print("Warning: Geometry V2 Service chưa được implement. Đây là UI mode only.")
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
            # Ẩn copy button khi clear dữ liệu
            self._hide_copy_button()
    
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
        # Geometry V2: giữ nguyên operations mặc định
        return ["Tương giao", "Khoảng cách", "Diện tích", "Thể tích", "PT đường thẳng"]
    
    def _on_shape_changed(self, *args):
        """Xử lý khi thay đổi hình dạng"""
        self._update_input_frames()
    
    def _on_operation_changed(self, *args):
        """Xử lý khi thay đổi phép toán"""
        operation = self.pheptoan_var.get()
        if operation:
            # TODO: Update available shapes based on operation for Geometry V2
            available_shapes = ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"]
            self._update_shape_dropdowns(available_shapes)
        self._update_input_frames()
    
    def _on_dimension_changed(self, *args):
        """Xử lý khi thay đổi kích thước"""
        # TODO: Implement dimension change logic for Geometry V2
        pass
    
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
            "primary": "#9C27B0", "secondary": "#7B1FA2", "text": "#FFFFFF",  # Purple theme for V2
            "accent": "#E91E63", "success": "#4CAF50", "warning": "#FF9800", "danger": "#F44336"
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
        tk.Label(logo_frame, text="🛠️", font=("Arial", 20),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        tk.Label(logo_frame, text="Geometry V2.0 - UI Only 🚧", font=("Arial", 16, "bold"),
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
            center_section, text="📋 Excel: ✅ Ready", font=("Arial", 8),
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
        status_text = "Service: ⚠️ UI Only (No Logic)"
        tk.Label(center_section, text=status_text, font=("Arial", 8),
                bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["warning"]).pack(side="bottom")
        
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
            bg="#FFFFFF", fg="#7B1FA2", font=("Arial", 10, "bold")
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
            bg="#FFFFFF", fg="#7B1FA2", font=("Arial", 10, "bold")
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
            bg="#FFFFFF", fg="#7B1FA2", font=("Arial", 10, "bold")
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
            bg="#FFFFFF", fg="#7B1FA2", font=("Arial", 10, "bold")
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
            bg="#FFFFFF", fg="#7B1FA2", font=("Arial", 10, "bold")
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
            bg="#FFFFFF", fg="#E91E63", font=("Arial", 10, "bold")
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
            bg="#FFFFFF", fg="#E91E63", font=("Arial", 10, "bold")
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
            bg="#FFFFFF", fg="#E91E63", font=("Arial", 10, "bold")
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
            bg="#FFFFFF", fg="#E91E63", font=("Arial", 10, "bold")
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
            bg="#FFFFFF", fg="#E91E63", font=("Arial", 10, "bold")
        )
        self.frame_B_sphere.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(self.frame_B_sphere, text="Tâm mặt cầu (x,y,z):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_sphere_center_B = tk.Entry(self.frame_B_sphere, width=25)
        self.entry_sphere_center_B.grid(row=0, column=1, padx=5)
        
        tk.Label(self.frame_B_sphere, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.entry_sphere_radius_B = tk.Entry(self.frame_B_sphere, width=20)
        self.entry_sphere_radius_B.grid(row=0, column=3, padx=5)
        
        self.frame_B_sphere.grid_remove()
    
    # ========== PROCESSING METHODS (PLACEHOLDERS) ==========
    def _process_all(self):
        """Thực thi tất cả - Placeholder cho Geometry V2"""
        messagebox.showinfo("Geometry V2", 
            "🚧 Đây là UI mode only!\n\n"
            "Logic xử lý sẽ được implement sau.\n\n"
            "Hiện tại chỉ có giao diện để test.")
    
    def _copy_result(self):
        """Copy kết quả - Placeholder"""
        messagebox.showinfo("Geometry V2", "Chưa có kết quả để copy (UI only mode)")
    
    def _show_copy_button(self):
        """Hiển thị nút copy khi có kết quả"""
        if hasattr(self, 'btn_copy_result'):
            self.btn_copy_result.grid()
    
    def _hide_copy_button(self):
        """Ẩn nút copy khi không có kết quả"""
        if hasattr(self, 'btn_copy_result'):
            self.btn_copy_result.grid_remove()
    
    def _update_result_display(self, message):
        """Cập nhật hiển thị kết quả với màu sắc (dùng cho thông báo nhiều dòng)"""
        self.entry_tong.delete(1.0, tk.END)
        self.entry_tong.insert(tk.END, message)
        
        # Giữ font mặc định cho thông báo
        try:
            self.entry_tong.config(font=("Courier New", 9), fg="black")
        except Exception:
            pass
        
        if "Lỗi" in message or "lỗi" in message:
            self.entry_tong.config(bg="#FFEBEE", fg="#D32F2F")
        elif "Đã import" in message or "Hoàn thành" in message:
            self.entry_tong.config(bg="#E8F5E8", fg="#388E3C")
        elif "Đang xử lý" in message:
            self.entry_tong.config(bg="#FFF3E0", fg="#F57C00")
        else:
            self.entry_tong.config(bg="#F8F9FA", fg="#9C27B0")
    
    def _show_ready_message(self):
        """Hiển thông báo sẵn sàng"""
        message = "🚧 Geometry V2 Mode - UI Only\n\nGiao diện đã sẵn sàng. Logic xử lý sẽ được implement sau."
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
            width=80, height=3,
            font=("Courier New", 9), wrap=tk.WORD,
            bg="#F8F9FA", fg="black",
            relief="solid", bd=1, padx=5, pady=5
        )
        self.entry_tong.grid(row=9, column=0, columnspan=4, padx=5, pady=5, sticky="we")

        # Nút copy kết quả (ẩn ban đầu)
        self.btn_copy_result = tk.Button(
            self.main_container, text="📋 Copy Kết Quả",
            command=self._copy_result,
            bg="#9C27B0", fg="white", font=("Arial", 9, "bold"),
            width=20
        )
        self.btn_copy_result.grid(row=10,  column=0, sticky="w", padx=0, pady=5)
        self.btn_copy_result.grid_remove()  # Ẩn ban đầu

        # Frame cho nút thủ công
        self.frame_buttons_manual = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_manual.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")

        tk.Button(self.frame_buttons_manual, text="🚀 Test Xử Lý (Placeholder)",
                  command=self._process_all,
                  bg="#9C27B0", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
        
        tk.Label(self.frame_buttons_manual, text="🚧 Logic chưa implement", 
                bg="#FFFFFF", fg="#FF9800", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        
        # Frame cho nút import mode
        self.frame_buttons_import = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_import.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        
        tk.Label(self.frame_buttons_import, text="🚧 Import mode chưa implement", 
                bg="#FFFFFF", fg="#FF9800", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
        
        # Initially hide import buttons
        self.frame_buttons_import.grid_remove()
        self.frame_buttons_manual.grid_remove()


if __name__ == "__main__":
    root = tk.Tk()
    app = GeometryV2View(root)
    root.mainloop()