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
        self.window.title("Geometry V2 Mode - 7 Shapes & 10 Operations 🚀")
        self.window.geometry("950x950")
        self.window.configure(bg="#F8F9FA")

        # Lưu config được truyền vào
        self.config = config or {}
        
        # Import và khởi tạo GeometryV2Service (lazy loading)
        self.geometry_service = None
        self._initialize_service()
        
        # Excel processing state
        self.imported_data = False
        self.imported_file_path = ""
        self.imported_file_name = ""
        self.manual_data_entered = False
        self.processing_cancelled = False
        self.is_large_file = False
        self.has_result = False
        
        # Biến và trạng thái
        self._initialize_variables()
        self._setup_ui()
        
        # Đảm bảo hiển thị đúng ngay lần đầu
        self._on_operation_changed()
        self._on_shape_changed()

    def _initialize_service(self):
        """
        Khởi tạo Geometry V2 Service.
        
        Tạm thời chưa import vì structure đã tạo nhưng logic chưa implement.
        """
        try:
            from services.geometry_v2.geometry_v2_service import GeometryV2Service
            self.geometry_service = GeometryV2Service(self.config)
            print("✅ Geometry V2 Service initialized successfully!")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Geometry V2 Service: {e}")
            self.geometry_service = None

    def _initialize_variables(self):
        """Khởi tạo tất cả biến"""
        self.dropdown1_var = tk.StringVar(value="")
        self.dropdown2_var = tk.StringVar(value="")
        self.kich_thuoc_A_var = tk.StringVar(value="3")
        self.kich_thuoc_B_var = tk.StringVar(value="3")
        
        # Phép toán mặc định
        self.pheptoan_var = tk.StringVar(value="Khoảng cách")

        # Phiên bản mặc định
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var = tk.StringVar(value=self.phien_ban_list[0])
        
        # Bind các thay đổi
        self.dropdown1_var.trace('w', self._on_shape_changed)
        self.dropdown2_var.trace('w', self._on_shape_changed)
        self.pheptoan_var.trace('w', self._on_operation_changed)
        self.kich_thuoc_A_var.trace('w', self._on_dimension_changed)
        self.kich_thuoc_B_var.trace('w', self._on_dimension_changed)
        
        # Bind input events
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
        for attr_name in dir(self):
            if attr_name.startswith('entry_') and hasattr(self, attr_name):
                entry = getattr(self, attr_name)
                if hasattr(entry, 'get'):
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
        
        return ["Phiên bản fx799", "Phiên bản fx880", "Phiên bản fx801"]
    
    def _get_available_operations(self):
        """
        Lấy danh sách phép toán (10 phép).
        
        Nếu service đã khởi tạo, dùng từ service.
        Nếu không, dùng danh sách mặc định.
        """
        if self.geometry_service:
            return self.geometry_service.get_available_operations()
        else:
            return [
                "Tương giao",
                "Khoảng cách",
                "Diện tích",
                "Thể tích",
                "PT đường thẳng",
                "PT mặt phẳng",
                "Góc",
                "Tích vô hướng 2 vecto",
                "Vecto đơn vị",
                "Phép tính tam giác"
            ]
    
    def _get_available_shapes(self):
        """
        Lấy danh sách hình học (7 hình).
        
        Nếu service đã khởi tạo, dùng từ service.
        Nếu không, dùng danh sách mặc định.
        """
        if self.geometry_service:
            return self.geometry_service.get_available_shapes()
        else:
            return [
                "Điểm",
                "Vecto",
                "Đường thẳng",
                "Mặt phẳng",
                "Đường tròn",
                "Mặt cầu",
                "Tam giác"
            ]
    
    def _on_shape_changed(self, *args):
        """Xử lý khi thay đổi hình dạng"""
        if self.geometry_service:
            self.geometry_service.set_current_shapes(
                self.dropdown1_var.get(),
                self.dropdown2_var.get()
            )
        self._update_input_frames()
    
    def _on_operation_changed(self, *args):
        """Xử lý khi thay đổi phép toán"""
        operation = self.pheptoan_var.get()
        if operation:
            if self.geometry_service:
                self.geometry_service.set_current_operation(operation)
                available_shapes = self.geometry_service.update_dropdown_options(operation)
            else:
                available_shapes = self._get_available_shapes()
            
            self._update_shape_dropdowns(available_shapes)
        self._update_input_frames()
    
    def _on_dimension_changed(self, *args):
        """Xử lý khi thay đổi kích thước"""
        if self.geometry_service:
            self.geometry_service.set_dimension(
                self.kich_thuoc_A_var.get(),
                self.kich_thuoc_B_var.get()
            )
    
    def _update_shape_dropdowns(self, available_shapes):
        """Cập nhật các dropdown theo phép toán"""
        if not available_shapes:
            return
        try:
            # Cập nhật dropdown A
            menu_A = self.dropdown1_menu['menu']
            menu_A.delete(0, 'end')
            for shape in available_shapes:
                menu_A.add_command(label=shape, command=tk._setit(self.dropdown1_var, shape))
            if self.dropdown1_var.get() not in available_shapes:
                self.dropdown1_var.set(available_shapes[0])
            
            # Cập nhật dropdown B khi cần
            single_shape_operations = ["Diện tích", "Thể tích", "Vecto đơn vị", "Phép tính tam giác"]
            
            if self.pheptoan_var.get() not in single_shape_operations:
                menu_B = self.dropdown2_menu['menu']
                menu_B.delete(0, 'end')
                for shape in available_shapes:
                    menu_B.add_command(label=shape, command=tk._setit(self.dropdown2_var, shape))
                if self.dropdown2_var.get() not in available_shapes:
                    self.dropdown2_var.set(available_shapes[0])
                self.label_B.grid()
                self.dropdown2_menu.grid()
            else:
                self.label_B.grid_remove()
                self.dropdown2_menu.grid_remove()
        except Exception as e:
            print(f"Warning: Could not update dropdowns: {e}")
    
    def _update_input_frames(self):
        """Cập nhật hiển thị các frame nhập liệu"""
        # Ẩn các frame cũ trước (7 hình x 2 nhóm = 14 frames)
        all_frames = [
            'frame_A_diem', 'frame_A_vecto', 'frame_A_duong', 'frame_A_plane', 
            'frame_A_circle', 'frame_A_sphere', 'frame_A_triangle',
            'frame_B_diem', 'frame_B_vecto', 'frame_B_duong', 'frame_B_plane',
            'frame_B_circle', 'frame_B_sphere', 'frame_B_triangle'
        ]
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
        single_shape_operations = ["Diện tích", "Thể tích", "Vecto đơn vị", "Phép tính tam giác"]
        if self.pheptoan_var.get() not in single_shape_operations:
            shape_B = self.dropdown2_var.get()
            if shape_B:
                self._show_input_frame_B(shape_B)
    
    def _show_input_frame_A(self, shape):
        """Hiển thị frame nhập liệu cho nhóm A"""
        try:
            if shape == "Điểm" and hasattr(self, 'frame_A_diem'):
                self.frame_A_diem.grid()
            elif shape == "Vecto" and hasattr(self, 'frame_A_vecto'):
                self.frame_A_vecto.grid()
            elif shape == "Đường thẳng" and hasattr(self, 'frame_A_duong'):
                self.frame_A_duong.grid()
            elif shape == "Mặt phẳng" and hasattr(self, 'frame_A_plane'):
                self.frame_A_plane.grid()
            elif shape == "Đường tròn" and hasattr(self, 'frame_A_circle'):
                self.frame_A_circle.grid()
            elif shape == "Mặt cầu" and hasattr(self, 'frame_A_sphere'):
                self.frame_A_sphere.grid()
            elif shape == "Tam giác" and hasattr(self, 'frame_A_triangle'):
                self.frame_A_triangle.grid()
        except Exception as e:
            print(f"Warning: Could not show frame A for {shape}: {e}")
    
    def _show_input_frame_B(self, shape):
        """Hiển thị frame nhập liệu cho nhóm B"""
        try:
            if shape == "Điểm" and hasattr(self, 'frame_B_diem'):
                self.frame_B_diem.grid()
            elif shape == "Vecto" and hasattr(self, 'frame_B_vecto'):
                self.frame_B_vecto.grid()
            elif shape == "Đường thẳng" and hasattr(self, 'frame_B_duong'):
                self.frame_B_duong.grid()
            elif shape == "Mặt phẳng" and hasattr(self, 'frame_B_plane'):
                self.frame_B_plane.grid()
            elif shape == "Đường tròn" and hasattr(self, 'frame_B_circle'):
                self.frame_B_circle.grid()
            elif shape == "Mặt cầu" and hasattr(self, 'frame_B_sphere'):
                self.frame_B_sphere.grid()
            elif shape == "Tam giác" and hasattr(self, 'frame_B_triangle'):
                self.frame_B_triangle.grid()
        except Exception as e:
            print(f"Warning: Could not show frame B for {shape}: {e}")

    def _setup_ui(self):
        """Setup giao diện chính"""
        self._create_header()
        
        self.main_container = tk.Frame(self.window, bg="#F8F9FA")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=5)

        top_frame = tk.Frame(self.main_container, bg="#F8F9FA")
        top_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        self._setup_dropdowns(top_frame)
        self._setup_all_input_frames()
        self._setup_control_frame()
        
        self._show_ready_message()

    def _create_header(self):
        """Tạo header với memory monitoring"""
        HEADER_COLORS = {
            "primary": "#9C27B0", "secondary": "#7B1FA2", "text": "#FFFFFF",
            "accent": "#E91E63", "success": "#4CAF50", "warning": "#FF9800", "danger": "#F44336"
        }

        self.header_frame = tk.Frame(self.window, bg=HEADER_COLORS["primary"], height=90)
        self.header_frame.pack(fill="x", padx=10, pady=5)
        self.header_frame.pack_propagate(False)

        header_content = tk.Frame(self.header_frame, bg=HEADER_COLORS["primary"])
        header_content.pack(fill="both", expand=True, padx=15, pady=10)

        left_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        left_section.pack(side="left", fill="y")

        logo_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        logo_frame.pack(side="top", fill="x")
        tk.Label(logo_frame, text="🚀", font=("Arial", 20),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        tk.Label(logo_frame, text="Geometry V2 - 7 Shapes & 10 Operations", font=("Arial", 14, "bold"),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left", padx=(5, 20))

        operation_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        operation_frame.pack(side="top", fill="x", pady=(5, 0))
        tk.Label(operation_frame, text="Phép toán:", font=("Arial", 10),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")

        operations = self._get_available_operations()
        self.operation_menu = tk.OptionMenu(operation_frame, self.pheptoan_var, *operations)
        self.operation_menu.config(
            bg=HEADER_COLORS["secondary"], fg=HEADER_COLORS["text"],
            font=("Arial", 9, "bold"), width=18, relief="flat", borderwidth=0
        )
        self.operation_menu.pack(side="left", padx=(5, 0))

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
        
        self.excel_status_label = tk.Label(
            center_section, text="📋 Excel: ✅ Ready", font=("Arial", 8),
            bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["success"]
        )
        self.excel_status_label.pack(side="bottom")
        
        self.memory_status_label = tk.Label(
            center_section, text=f"💾 Memory: {self._get_memory_usage():.1f}MB", font=("Arial", 8),
            bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]
        )
        self.memory_status_label.pack(side="bottom")
        
        status_text = "Service: ✅ Ready" if self.geometry_service else "Service: ⚠️ Not Initialized"
        tk.Label(center_section, text=status_text, font=("Arial", 8),
                bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="bottom")
        
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
                if memory_mb > 800:
                    color, status = "#F44336", "🔥 High"
                elif memory_mb > 500:
                    color, status = "#FF9800", "⚠️ Medium"
                else:
                    color, status = "#4CAF50", "✅ OK"
                
                self.memory_status_label.config(
                    text=f"💾 Memory: {memory_mb:.1f}MB ({status})", fg=color
                )
            except Exception:
                pass
            
            self.window.after(5000, update_memory)
        
        update_memory()

    def _setup_dropdowns(self, parent):
        """Setup dropdown chọn nhóm"""
        shapes = self._get_available_shapes()

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
        """
        Tạo tất cả các frame nhập liệu cho 7 hình học.
        
        NHÓM A: Điểm, Vecto, Đường thẳng, Mặt phẳng, Đường tròn, Mặt cầu, Tam giác
        NHÓM B: Tương tự
        """
        # NHÓM A
        self._create_point_frame_A()
        self._create_vector_frame_A()
        self._create_line_frame_A()
        self._create_plane_frame_A()
        self._create_circle_frame_A()
        self._create_sphere_frame_A()
        self._create_triangle_frame_A()
        
        # NHÓM B
        self._create_point_frame_B()
        self._create_vector_frame_B()
        self._create_line_frame_B()
        self._create_plane_frame_B()
        self._create_circle_frame_B()
        self._create_sphere_frame_B()
        self._create_triangle_frame_B()
    
    # ========== NHÓM A FRAMES (7 HÌNH) ==========
    
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
    
    def _create_vector_frame_A(self):
        """Tạo frame vecto A"""
        self.frame_A_vecto = tk.LabelFrame(
            self.main_container, text="➡️ NHÓM A - Vecto",
            bg="#FFFFFF", fg="#7B1FA2", font=("Arial", 10, "bold")
        )
        self.frame_A_vecto.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_vecto, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(self.frame_A_vecto, self.kich_thuoc_A_var, "2", "3").grid(row=0, column=1)

        tk.Label(self.frame_A_vecto, text="Nhập thành phần (x,y,z):", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_vecto_A = tk.Entry(self.frame_A_vecto, width=40)
        self.entry_vecto_A.grid(row=1, column=1, columnspan=2, sticky="we")
        
        self.frame_A_vecto.grid_remove()
    
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
    
    def _create_triangle_frame_A(self):
        """Tạo frame tam giác A"""
        self.frame_A_triangle = tk.LabelFrame(
            self.main_container, text="🔺 NHÓM A - Tam giác",
            bg="#FFFFFF", fg="#7B1FA2", font=("Arial", 10, "bold")
        )
        self.frame_A_triangle.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_triangle, text="Đỉnh A (x,y,z):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_triangle_a_A = tk.Entry(self.frame_A_triangle, width=25)
        self.entry_triangle_a_A.grid(row=0, column=1, padx=5)
        
        tk.Label(self.frame_A_triangle, text="Đỉnh B (x,y,z):", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_triangle_b_A = tk.Entry(self.frame_A_triangle, width=25)
        self.entry_triangle_b_A.grid(row=1, column=1, padx=5)
        
        tk.Label(self.frame_A_triangle, text="Đỉnh C (x,y,z):", bg="#FFFFFF").grid(row=2, column=0)
        self.entry_triangle_c_A = tk.Entry(self.frame_A_triangle, width=25)
        self.entry_triangle_c_A.grid(row=2, column=1, padx=5)
        
        self.frame_A_triangle.grid_remove()
    
    # ========== NHÓM B FRAMES (7 HÌNH - TƯƠNG TỰ) ==========
    # (Tương tự nhóm A nhưng màu khác)
    
    def _create_point_frame_B(self):
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
    
    def _create_vector_frame_B(self):
        self.frame_B_vecto = tk.LabelFrame(
            self.main_container, text="➡️ NHÓM B - Vecto",
            bg="#FFFFFF", fg="#E91E63", font=("Arial", 10, "bold")
        )
        self.frame_B_vecto.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_B_vecto, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(self.frame_B_vecto, self.kich_thuoc_B_var, "2", "3").grid(row=0, column=1)
        tk.Label(self.frame_B_vecto, text="Nhập thành phần (x,y,z):", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_vecto_B = tk.Entry(self.frame_B_vecto, width=40)
        self.entry_vecto_B.grid(row=1, column=1, columnspan=2, sticky="we")
        self.frame_B_vecto.grid_remove()
    
    def _create_line_frame_B(self):
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
    
    def _create_triangle_frame_B(self):
        self.frame_B_triangle = tk.LabelFrame(
            self.main_container, text="🔺 NHÓM B - Tam giác",
            bg="#FFFFFF", fg="#E91E63", font=("Arial", 10, "bold")
        )
        self.frame_B_triangle.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_B_triangle, text="Đỉnh A (x,y,z):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_triangle_a_B = tk.Entry(self.frame_B_triangle, width=25)
        self.entry_triangle_a_B.grid(row=0, column=1, padx=5)
        tk.Label(self.frame_B_triangle, text="Đỉnh B (x,y,z):", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_triangle_b_B = tk.Entry(self.frame_B_triangle, width=25)
        self.entry_triangle_b_B.grid(row=1, column=1, padx=5)
        tk.Label(self.frame_B_triangle, text="Đỉnh C (x,y,z):", bg="#FFFFFF").grid(row=2, column=0)
        self.entry_triangle_c_B = tk.Entry(self.frame_B_triangle, width=25)
        self.entry_triangle_c_B.grid(row=2, column=1, padx=5)
        self.frame_B_triangle.grid_remove()
    
    # ========== PROCESSING METHODS (PLACEHOLDERS) ==========
    def _process_all(self):
        """Thực thi tất cả - Placeholder cho Geometry V2"""
        if self.geometry_service:
            messagebox.showinfo("Geometry V2", 
                "✅ Service đã khởi tạo!\n\n"
                "🚧 Logic xử lý chưa implement.\n\n"
                "Cấu trúc thư mục đã sẵn sàng.")
        else:
            messagebox.showinfo("Geometry V2", 
                "🚧 Đây là UI mode only!\n\n"
                "Logic xử lý sẽ được implement sau.\n\n"
                "Hiện tại chỉ có giao diện để test.")
    
    def _copy_result(self):
        """Copy kết quả - Placeholder"""
        messagebox.showinfo("Geometry V2", "Chưa có kết quả để copy (logic chưa implement)")
    
    def _show_copy_button(self):
        if hasattr(self, 'btn_copy_result'):
            self.btn_copy_result.grid()
    
    def _hide_copy_button(self):
        if hasattr(self, 'btn_copy_result'):
            self.btn_copy_result.grid_remove()
    
    def _update_result_display(self, message):
        self.entry_tong.delete(1.0, tk.END)
        self.entry_tong.insert(tk.END, message)
        
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
        if self.geometry_service:
            message = "✅ Geometry V2 Service Ready!\n\n7 hình học: Điểm, Vecto, Đường thẳng, Mặt phẳng, Đường tròn, Mặt cầu, Tam giác\n10 phép tính: Tương giao, Khoảng cách, Diện tích, Thể tích, PT đường thẳng, PT mặt phẳng, Góc, Tích vô hướng, Vecto đơn vị, Phép tính tam giác"
        else:
            message = "⚠️ Service chưa khởi tạo\n\nGiao diện UI đã sẵn sàng."
        
        self.entry_tong.insert(tk.END, message)

    def _setup_control_frame(self):
        self.frame_tong = tk.LabelFrame(
            self.main_container, text="🎉 KẾT QUẢ & ĐIỀU KHIỂN",
            bg="#FFFFFF", font=("Arial", 10, "bold")
        )
        self.frame_tong.grid(row=8, column=0, columnspan=4, padx=10, pady=10, sticky="we")

        self.entry_tong = tk.Text(
            self.main_container,
            width=80, height=4,
            font=("Courier New", 9), wrap=tk.WORD,
            bg="#F8F9FA", fg="black",
            relief="solid", bd=1, padx=5, pady=5
        )
        self.entry_tong.grid(row=9, column=0, columnspan=4, padx=5, pady=5, sticky="we")

        self.btn_copy_result = tk.Button(
            self.main_container, text="📋 Copy Kết Quả",
            command=self._copy_result,
            bg="#9C27B0", fg="white", font=("Arial", 9, "bold"),
            width=20
        )
        self.btn_copy_result.grid(row=10, column=0, sticky="w", padx=0, pady=5)
        self.btn_copy_result.grid_remove()

        self.frame_buttons_manual = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_manual.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")

        tk.Button(self.frame_buttons_manual, text="🚀 Test Xử Lý",
                  command=self._process_all,
                  bg="#9C27B0", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
        
        tk.Label(self.frame_buttons_manual, text="🚧 Logic đang được implement", 
                bg="#FFFFFF", fg="#FF9800", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        
        self.frame_buttons_import = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_import.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        
        tk.Label(self.frame_buttons_import, text="🚧 Import mode chưa implement", 
                bg="#FFFFFF", fg="#FF9800", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
        
        self.frame_buttons_import.grid_remove()
        self.frame_buttons_manual.grid_remove()


if __name__ == "__main__":
    root = tk.Tk()
    app = GeometryV2View(root)
    root.mainloop()