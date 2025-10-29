import tkinter as tk
from tkinter import messagebox, filedialog

class GeometryView:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Geometry Mode - Now with Logic!")
        self.window.geometry("900x900")
        self.window.configure(bg="#F8F9FA")

        # Lưu config được truyền vào
        self.config = config or {}
        
        # Import và khởi tạo GeometryService (lazy loading)
        self.geometry_service = None
        self._initialize_service()
        
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

        # Phên bản mặc định - lấy từ config hoặc fallback
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var = tk.StringVar(value=self.phien_ban_list[0])
        
        # Bind các thay đổi để cập nhật service
        self.dropdown1_var.trace('w', self._on_shape_changed)
        self.dropdown2_var.trace('w', self._on_shape_changed)
        self.pheptoan_var.trace('w', self._on_operation_changed)
        self.kich_thuoc_A_var.trace('w', self._on_dimension_changed)
        self.kich_thuoc_B_var.trace('w', self._on_dimension_changed)
        
        # Cập nhật state ban đầu cho service
        if self.geometry_service:
            self.geometry_service.set_kich_thuoc(self.kich_thuoc_A_var.get(), self.kich_thuoc_B_var.get())

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
        """Tạo header"""
        HEADER_COLORS = {
            "primary": "#2E86AB", "secondary": "#1B5299", "text": "#FFFFFF",
            "accent": "#F18F01", "success": "#4CAF50", "warning": "#FF9800"
        }

        # Main header frame
        self.header_frame = tk.Frame(self.window, bg=HEADER_COLORS["primary"], height=80)
        self.header_frame.pack(fill="x", padx=10, pady=5)
        self.header_frame.pack_propagate(False)

        header_content = tk.Frame(self.header_frame, bg=HEADER_COLORS["primary"])
        header_content.pack(fill="both", expand=True, padx=15, pady=10)

        # Logo và title
        left_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        left_section.pack(side="left", fill="y")

        logo_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        logo_frame.pack(side="top", fill="x")
        tk.Label(logo_frame, text="🧠", font=("Arial", 20),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        tk.Label(logo_frame, text="Geometry Mode v2.0 - With Logic!", font=("Arial", 16, "bold"),
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

        # Phiên bản
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
        
        # Service status indicator
        status_text = "Service: ✅ Ready" if self.geometry_service else "Service: ⚠️ Error"
        tk.Label(center_section, text=status_text, font=("Arial", 8),
                bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="bottom")

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

        tk.Label(self.frame_A_diem, text="Nhập toạ độ (x,y,z):", bg="#FFFFFF").grid(row=1, column=0)
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
            self.main_container, text="📎 NHÓM A - Mặt phẳng",
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

        tk.Label(self.frame_B_diem, text="Nhập toạ độ (x,y,z):", bg="#FFFFFF").grid(row=1, column=0)
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
            self.main_container, text="📎 NHÓM B - Mặt phẳng",
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
    
    def _import_excel(self):
        """Import dữ liệu từ Excel"""
        try:
            file_path = filedialog.askopenfilename(
                title="Chọn file Excel",
                filetypes=[("Excel files", "*.xlsx *.xls")]
            )
            
            if file_path:
                self._update_result_display(f"📁 File Excel đã chọn: {file_path}\n\nChức năng import Excel sẽ được hoàn thiện trong commit tiếp theo.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi import Excel: {str(e)}")
    
    def _export_excel(self):
        """Xuất kết quả ra Excel"""
        try:
            summary = self.geometry_service.get_result_summary() if self.geometry_service else {}
            message = f"💾 Export thông tin hiện tại:\n"
            if summary:
                message += f"Phép toán: {summary.get('operation', 'Chưa chọn')}\n"
                message += f"Nhóm A: {summary.get('shape_A', 'Chưa chọn')}\n"
                message += f"Nhóm B: {summary.get('shape_B', 'Chưa chọn')}\n"
                message += f"Kết quả: {summary.get('encoded_result', 'Chưa có')}\n\n"
            message += "Chức năng export Excel sẽ được hoàn thiện trong commit tiếp theo."
            self._update_result_display(message)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi export Excel: {str(e)}")
    
    def _update_result_display(self, message):
        """Cập nhật hiển thị kết quả"""
        self.entry_tong.delete(1.0, tk.END)
        self.entry_tong.insert(tk.END, message)
    
    def _show_ready_message(self):
        """Hiện thông báo sẵn sàng"""
        if self.geometry_service:
            message = "✨ Geometry Mode v2.0 - Đã tích hợp logic từ TL!\n"
            message += "Chọn phép toán và hình dạng, sau đó nhập dữ liệu để thực thi.\n\n"
            message += "Các hình được hỗ trợ: Điểm, Đường thẳng, Mặt phẳng, Đường tròn, Mặt cầu"
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
            height=5,
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

        # Nút Import Excel
        self.btn_import_excel = tk.Button(
            self.frame_tong, text="📁 Import Excel",
            command=self._import_excel,
            bg="#FF9800", fg="white", font=("Arial", 9, "bold")
        )
        self.btn_import_excel.grid(row=0, column=0, columnspan=4, pady=5, sticky="we")

        # Frame cho nút thủ công
        self.frame_buttons = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")

        tk.Button(self.frame_buttons, text="🔄 Xử lý Nhóm A",
                  command=self._process_group_A,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons, text="🔄 Xử lý Nhóm B",
                  command=self._process_group_B,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_buttons, text="🚀 Thực thi tất cả",
                  command=self._process_all,
                  bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5)
        tk.Button(self.frame_buttons, text="💾 Xuất Excel",
                  command=self._export_excel,
                  bg="#FF9800", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = GeometryView(root)
    root.mainloop()
