import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import threading
import os
from datetime import datetime
import psutil
from services.geometry_v2.excel_processor import ExcelProcessor


class GeometryV2View:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Geometry V2 Mode - 7 Shapes & 10 Operations")
        self.window.geometry("950x950")
        self.window.configure(bg="#F8F9FA")
        self.config = config or {}
        self.geometry_service = None
        self.excel_processor = None
        self._initialize_service()
        self.imported_data = False
        self.imported_file_path = ""
        self.imported_file_name = ""
        self.manual_data_entered = False
        self.processing_cancelled = False
        self.is_large_file = False
        self.has_result = False
        self._initialize_variables()
        self._setup_ui()
        self._on_operation_changed()
        self._on_shape_changed()

    def _initialize_service(self):
        try:
            from services.geometry_v2.geometry_v2_service import GeometryV2Service
            self.geometry_service = GeometryV2Service(self.config)

            if self.geometry_service:
                self.excel_processor = ExcelProcessor(self.geometry_service)
                print("✅ Excel Processor initialized")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize Geometry V2 Service: {e}")
            self.geometry_service = None
            self.excel_processor = None

    def _initialize_variables(self):
        self.dropdown1_var = tk.StringVar(value="")
        self.dropdown2_var = tk.StringVar(value="")
        self.kich_thuoc_A_var = tk.StringVar(value="3")
        self.kich_thuoc_B_var = tk.StringVar(value="3")
        self.pheptoan_var = tk.StringVar(value="Khoảng cách")
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var = tk.StringVar(value=self.phien_ban_list[0])
        self.dropdown1_var.trace('w', self._on_shape_changed)
        self.dropdown2_var.trace('w', self._on_shape_changed)
        self.pheptoan_var.trace('w', self._on_operation_changed)
        self.kich_thuoc_A_var.trace('w', self._on_dimension_changed)
        self.kich_thuoc_B_var.trace('w', self._on_dimension_changed)
        self.window.after(1000, self._setup_input_bindings)

    def _setup_input_bindings(self):
        entries = self._get_all_input_entries()
        for entry in entries:
            if hasattr(entry, 'bind'):
                entry.bind('<KeyRelease>', self._on_input_data_changed)

    def _get_all_input_entries(self):
        entries = []
        for attr_name in dir(self):
            if attr_name.startswith('entry_') and hasattr(self, attr_name):
                entry = getattr(self, attr_name)
                if hasattr(entry, 'get'):
                    entries.append(entry)
        return entries

    def _on_input_data_changed(self, event):
        if self.imported_data:
            messagebox.showerror("Lỗi",
                                 "Đã import Excel, không thể nhập dữ liệu thủ công!\n\nNhấn 'Quay lại' để thoát chế độ import.")
            event.widget.delete(0, tk.END)
            return
        has_data = self._check_manual_data()
        if has_data and not self.manual_data_entered:
            self.manual_data_entered = True
            self.frame_buttons_excel.grid_remove()
            self.frame_buttons_manual.grid()
        elif not has_data and self.manual_data_entered:
            self.manual_data_entered = False
            self.frame_buttons_manual.grid_remove()

    def _check_manual_data(self):
        entries = self._get_all_input_entries()
        for entry in entries:
            try:
                if entry.get().strip():
                    return True
            except:
                pass
        return False

    def _get_available_versions(self):
        try:
            if self.config and 'common' in self.config and 'versions' in self.config['common']:
                versions_data = self.config['common']['versions']
                if 'versions' in versions_data:
                    return [f"Phiên bản {v}" for v in versions_data['versions']]
        except Exception as e:
            print(f"Warning: Không thể load versions từ config: {e}")
        return ["Phiên bản fx799", "Phiên bản fx880", "Phiên bản fx801"]

    def _get_available_operations(self):
        if self.geometry_service:
            return self.geometry_service.get_available_operations()
        else:
            return [
                "Tương giao", "Khoảng cách", "Diện tích", "Thể tích", "PT đường thẳng",
                "PT mặt phẳng", "Góc", "Tích vô hướng 2 vecto", "Vecto đơn vị", "Phép tính tam giác"
            ]

    def _get_operation_shape_map(self):
        return {
            "Tương giao": (
                ["Điểm", "Vecto", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"],
                ["Điểm", "Vecto", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"]
            ),
            "Khoảng cách": (["Điểm", "Đường thẳng", "Mặt phẳng"], ["Điểm", "Đường thẳng", "Mặt phẳng"]),
            "Diện tích": (["Đường tròn", "Mặt cầu"], None),
            "Thể tích": (["Mặt cầu"], None),
            "PT đường thẳng": (["Điểm", "Vecto"], ["Điểm", "Vecto"]),
            "PT mặt phẳng": (["Điểm", "Vecto"], ["Điểm", "Vecto"]),
            "Góc": (["Vecto", "Đường thẳng", "Mặt phẳng"], ["Vecto", "Đường thẳng", "Mặt phẳng"]),
            "Tích vô hướng 2 vecto": (["Vecto"], ["Vecto"]),
            "Vecto đơn vị": (["Vecto"], None),
            "Phép tính tam giác": (["Tam giác"], None),
        }

    def _get_available_shapes(self):
        if self.geometry_service:
            return self.geometry_service.get_available_shapes()
        else:
            return ["Điểm", "Vecto", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu", "Tam giác"]

    def _update_shape_dropdowns(self, _):
        op = self.pheptoan_var.get()
        op_map = self._get_operation_shape_map()
        allowed_a, allowed_b = op_map.get(op, ([], []))
        if allowed_a is None:
            allowed_a = []
        if allowed_b is None:
            allowed_b = []
        menu_A = self.dropdown1_menu['menu']
        menu_A.delete(0, 'end')
        for shape in allowed_a:
            menu_A.add_command(label=shape, command=tk._setit(self.dropdown1_var, shape))
        if self.dropdown1_var.get() not in allowed_a:
            self.dropdown1_var.set(allowed_a[0] if allowed_a else "")
        if allowed_b:
            menu_B = self.dropdown2_menu['menu']
            menu_B.delete(0, 'end')
            for shape in allowed_b:
                menu_B.add_command(label=shape, command=tk._setit(self.dropdown2_var, shape))
            if self.dropdown2_var.get() not in allowed_b:
                self.dropdown2_var.set(allowed_b[0] if allowed_b else "")
            self.label_B.grid()
            self.dropdown2_menu.grid()
        else:
            self.label_B.grid_remove()
            self.dropdown2_menu.grid_remove()

    def _on_operation_changed(self, *args):
        self._update_shape_dropdowns(None)
        self._update_input_frames()

    def _on_shape_changed(self, *args):
        self._update_input_frames()

    def _on_dimension_changed(self, *args):
        if self.geometry_service:
            self.geometry_service.set_dimension(
                self.kich_thuoc_A_var.get(),
                self.kich_thuoc_B_var.get()
            )

    def _update_input_frames(self):
        op = self.pheptoan_var.get()
        op_map = self._get_operation_shape_map()
        allowed_a, allowed_b = op_map.get(op, ([], []))
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
        shape_A = self.dropdown1_var.get()
        if allowed_a and shape_A in allowed_a:
            self._show_input_frame_A(shape_A)
        if allowed_b:
            shape_B = self.dropdown2_var.get()
            if shape_B in allowed_b:
                self._show_input_frame_B(shape_B)

    def _show_input_frame_A(self, shape):
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
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0

    def _start_memory_monitoring(self):
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
        self._create_point_frame_A()
        self._create_vector_frame_A()
        self._create_line_frame_A()
        self._create_plane_frame_A()
        self._create_circle_frame_A()
        self._create_sphere_frame_A()
        self._create_triangle_frame_A()
        self._create_point_frame_B()
        self._create_vector_frame_B()
        self._create_line_frame_B()
        self._create_plane_frame_B()
        self._create_circle_frame_B()
        self._create_sphere_frame_B()
        self._create_triangle_frame_B()

    def _create_point_frame_A(self):
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
        self.frame_A_plane = tk.LabelFrame(
            self.main_container, text="📐 NHÓM A - Mặt phẳng",
            bg="#FFFFFF", fg="#7B1FA2", font=("Arial", 10, "bold")
        )
        self.frame_A_plane.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_A_plane, text="Phương trình ax+by+cz+d=0:", bg="#FFFFFF").grid(row=0, column=0,
                                                                                           columnspan=4)
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
        self.frame_A_triangle = tk.LabelFrame(
            self.main_container, text="🔺 NHÓM A - Tam giác",
            bg="#FFFFFF", fg="#7B1FA2", font=("Arial", 10, "bold")
        )
        self.frame_A_triangle.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        tk.Label(self.frame_A_triangle, text="Độ dài cạnh a:", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_triangle_a_A = tk.Entry(self.frame_A_triangle, width=25)
        self.entry_triangle_a_A.grid(row=0, column=1, padx=5)
        tk.Label(self.frame_A_triangle, text="Độ dài cạnh b:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_triangle_b_A = tk.Entry(self.frame_A_triangle, width=25)
        self.entry_triangle_b_A.grid(row=1, column=1, padx=5)
        tk.Label(self.frame_A_triangle, text="Góc C (độ):", bg="#FFFFFF").grid(row=2, column=0)
        self.entry_triangle_c_A = tk.Entry(self.frame_A_triangle, width=25)
        self.entry_triangle_c_A.grid(row=2, column=1, padx=5)
        self.frame_A_triangle.grid_remove()

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
        tk.Label(self.frame_B_plane, text="Phương trình ax+by+cz+d=0:", bg="#FFFFFF").grid(row=0, column=0,
                                                                                           columnspan=4)
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

    # ========== CONTROL FRAME ==========
    def _setup_control_frame(self):
        self.frame_tong = tk.LabelFrame(
            self.main_container, text="🎉 KẾT QUẢ & ĐIỀU KHIỂN",
            bg="#FFFFFF", font=("Arial", 10, "bold")
        )
        self.frame_tong.grid(row=8, column=0, columnspan=4, padx=10, pady=10, sticky="we")

        self.entry_tong = tk.Text(
            self.main_container,
            width=80, height=6,
            font=("Courier New", 9), wrap=tk.WORD,
            bg="#F3E5F5", fg="#6A1B9A",
            relief="solid", bd=1, padx=5, pady=5
        )
        self.entry_tong.grid(row=9, column=0, columnspan=4, padx=5, pady=5, sticky="we")

        buttons_row = tk.Frame(self.main_container, bg="#F8F9FA")
        buttons_row.grid(row=10, column=0, columnspan=4, pady=5, sticky="we")

        self.btn_copy_result = tk.Button(
            buttons_row, text="📋 Copy Keylog",
            command=self._copy_result,
            bg="#9C27B0", fg="white", font=("Arial", 9, "bold"),
            width=15, height=1
        )
        self.btn_copy_result.pack(side="left", padx=5)
        self.btn_copy_result.pack_forget()

        self.btn_clear = tk.Button(
            buttons_row, text="🗑️ Clear All",
            command=self._clear_all_inputs,
            bg="#607D8B", fg="white", font=("Arial", 9, "bold"),
            width=15, height=1
        )
        self.btn_clear.pack(side="left", padx=5)

        self.btn_import_excel = tk.Button(
            self.frame_tong, text="📁 Import Excel",
            command=self._import_excel,
            bg="#FF9800", fg="white", font=("Arial", 10, "bold")
        )
        self.btn_import_excel.grid(row=0, column=0, columnspan=4, pady=5, sticky="we")

        self.frame_buttons_manual = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_manual.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        tk.Button(
            self.frame_buttons_manual, text="🔐 Encode",
            command=self._encode_manual,
            bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
            width=20, height=1
        ).pack(pady=5)
        self.frame_buttons_manual.grid_remove()

        self.frame_buttons_excel = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_excel.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        tk.Button(self.frame_buttons_excel, text="🚀 Xử lý Excel",
                  command=self._process_excel,
                  bg="#F44336", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons_excel, text="↩️ Quay lại",
                  command=self._quit_import_mode,
                  bg="#607D8B", fg="white", font=("Arial", 10)).grid(row=0, column=1, padx=5)
        self.frame_buttons_excel.grid_remove()

    # ========== DATA COLLECTION ==========
    def _collect_data_from_inputs(self, group):
        if group == 'A':
            shape = self.dropdown1_var.get()
        else:
            shape = self.dropdown2_var.get()

        data = {}

        try:
            if shape == "Điểm":
                if group == 'A':
                    point_input = self.entry_diem_A.get().strip()
                else:
                    point_input = self.entry_diem_B.get().strip()
                if not point_input:
                    return None
                data['point_input'] = point_input

            elif shape == "Vecto":
                if group == 'A':
                    vecto_input = self.entry_vecto_A.get().strip()
                else:
                    vecto_input = self.entry_vecto_B.get().strip()
                if not vecto_input:
                    return None
                data['vecto_input'] = vecto_input

            elif shape == "Đường thẳng":
                if group == 'A':
                    point = self.entry_point_A.get().strip()
                    vector = self.entry_vector_A.get().strip()
                else:
                    point = self.entry_point_B.get().strip()
                    vector = self.entry_vector_B.get().strip()
                if not point or not vector:
                    return None
                data['line_A1'] = point
                data['line_X1'] = vector

            elif shape == "Mặt phẳng":
                if group == 'A':
                    a = self.entry_a_A.get().strip()
                    b = self.entry_b_A.get().strip()
                    c = self.entry_c_A.get().strip()
                    d = self.entry_d_A.get().strip()
                else:
                    a = self.entry_a_B.get().strip()
                    b = self.entry_b_B.get().strip()
                    c = self.entry_c_B.get().strip()
                    d = self.entry_d_B.get().strip()
                if not a or not b or not c or not d:
                    return None
                data['plane_a'] = a
                data['plane_b'] = b
                data['plane_c'] = c
                data['plane_d'] = d

            elif shape == "Đường tròn":
                if group == 'A':
                    center = self.entry_center_A.get().strip()
                    radius = self.entry_radius_A.get().strip()
                else:
                    center = self.entry_center_B.get().strip()
                    radius = self.entry_radius_B.get().strip()
                if not center or not radius:
                    return None
                data['circle_center'] = center
                data['circle_radius'] = radius

            elif shape == "Mặt cầu":
                if group == 'A':
                    center = self.entry_sphere_center_A.get().strip()
                    radius = self.entry_sphere_radius_A.get().strip()
                else:
                    center = self.entry_sphere_center_B.get().strip()
                    radius = self.entry_sphere_radius_B.get().strip()
                if not center or not radius:
                    return None
                data['sphere_center'] = center
                data['sphere_radius'] = radius

            elif shape == "Tam giác":
                if group == 'A':
                    a = self.entry_triangle_a_A.get().strip()
                    b = self.entry_triangle_b_A.get().strip()
                    c = self.entry_triangle_c_A.get().strip()
                else:
                    a = self.entry_triangle_a_B.get().strip()
                    b = self.entry_triangle_b_B.get().strip()
                    c = self.entry_triangle_c_B.get().strip()
                if not a or not b or not c:
                    return None
                data['triangle_a'] = a
                data['triangle_b'] = b
                data['triangle_c'] = c

            return data if data else None

        except Exception as e:
            print(f"⚠️ Error collecting data for group {group}: {e}")
            return None

    def _requires_group_b(self):
        operation = self.pheptoan_var.get()
        op_map = self._get_operation_shape_map()
        allowed_a, allowed_b = op_map.get(operation, ([], []))
        return allowed_b is not None and len(allowed_b) > 0

    # ========== ENCODE MANUAL ==========
    def _encode_manual(self):
        try:
            if not self.geometry_service:
                messagebox.showerror("Lỗi", "GeometryV2Service chưa sẵn sàng!")
                return

            data_a = self._collect_data_from_inputs('A')
            if not data_a:
                messagebox.showerror(
                    "Lỗi",
                    "Vui lòng nhập dữ liệu cho Nhóm A!\n\nTất cả các trường bắt buộc phải được điền."
                )
                return

            data_b = None
            if self._requires_group_b():
                data_b = self._collect_data_from_inputs('B')
                if not data_b:
                    messagebox.showerror(
                        "Lỗi",
                        "Phép toán này cần Nhóm B!\n\nVui lòng nhập dữ liệu cho Nhóm B."
                    )
                    return

            self.geometry_service.set_operation(self.pheptoan_var.get())
            self.geometry_service.set_shapes(
                self.dropdown1_var.get(),
                self.dropdown2_var.get() if self._requires_group_b() else None
            )
            self.geometry_service.set_dimension(
                self.kich_thuoc_A_var.get(),
                self.kich_thuoc_B_var.get()
            )
            self.geometry_service.set_version(
                self.phien_ban_var.get().replace("Phiên bản ", "")
            )

            result = self.geometry_service.process_manual_data(data_a, data_b)

            if result['success']:
                output_message = (
                    f"✅ Encode thành công!\n\n"
                    f"📋 Phép toán: {self.pheptoan_var.get()}\n"
                    f"🔷 Nhóm A: {self.dropdown1_var.get()} ({self.kich_thuoc_A_var.get()}D)\n"
                )
                if data_b:
                    output_message += f"🔶 Nhóm B: {self.dropdown2_var.get()} ({self.kich_thuoc_B_var.get()}D)\n"
                output_message += f"\n🔐 Keylog:\n{result['encoded']}"

                self._update_result_display(output_message)
                self.btn_copy_result.pack(side="left", padx=5)
                self.has_result = True
            else:
                messagebox.showerror("Lỗi Encode", result['error'])
                self._update_result_display(f"❌ Lỗi encode:\n\n{result['error']}")

        except Exception as e:
            error_msg = f"Lỗi encode:\n\n{str(e)}"
            messagebox.showerror("Lỗi", error_msg)
            self._update_result_display(f"❌ {error_msg}")

    def _copy_result(self):
        try:
            if not self.has_result:
                messagebox.showinfo("Thông báo", "Chưa có kết quả để copy!")
                return

            result_text = self.entry_tong.get(1.0, tk.END).strip()
            lines = result_text.split('\n')
            keylog = None

            for i, line in enumerate(lines):
                if '🔐 Keylog:' in line:
                    if i + 1 < len(lines):
                        keylog = lines[i + 1].strip()
                    break

            if keylog:
                self.window.clipboard_clear()
                self.window.clipboard_append(keylog)
                self.window.update()
                messagebox.showinfo("Thành công", f"✅ Đã copy keylog vào clipboard!\n\n{keylog}")
            else:
                messagebox.showwarning("Cảnh báo", "Không tìm thấy keylog trong kết quả!")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi copy:\n{str(e)}")

    def _clear_all_inputs(self):
        try:
            entries = self._get_all_input_entries()
            for entry in entries:
                try:
                    if hasattr(entry, 'delete'):
                        entry.delete(0, tk.END)
                except:
                    pass

            self._update_result_display("✨ Đã xóa tất cả input!\n\nSẵn sàng nhập dữ liệu mới.")
            self.btn_copy_result.pack_forget()
            self.has_result = False
            self.manual_data_entered = False

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi clear inputs:\n{str(e)}")

    def _update_result_display(self, message):
        self.entry_tong.delete(1.0, tk.END)
        self.entry_tong.insert(tk.END, message)

        if "❌" in message or "Lỗi" in message or "lỗi" in message:
            self.entry_tong.config(bg="#FFEBEE", fg="#D32F2F")
        elif "✅" in message or "thành công" in message:
            self.entry_tong.config(bg="#E8F5E9", fg="#2E7D32")
        elif "⚠️" in message or "Cảnh báo" in message:
            self.entry_tong.config(bg="#FFF3E0", fg="#F57C00")
        elif "🚧" in message or "Coming Soon" in message or "⏳" in message:
            self.entry_tong.config(bg="#E3F2FD", fg="#1976D2")
        else:
            self.entry_tong.config(bg="#F3E5F5", fg="#6A1B9A")

    # ========== EXCEL PROCESSING ==========
    def _import_excel(self):
        try:
            if self.manual_data_entered or self._check_manual_data():
                messagebox.showerror(
                    "Lỗi",
                    "Đã có dữ liệu thủ công!\n\nVui lòng xóa dữ liệu thủ công trước khi import Excel."
                )
                return

            file_path = filedialog.askopenfilename(
                title="Chọn file Excel",
                filetypes=[("Excel files", "*.xlsx *.xls")]
            )

            if not file_path:
                return

            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in ['.xlsx', '.xls']:
                messagebox.showerror("Lỗi", "Chỉ hỗ trợ file Excel (.xlsx, .xls)!")
                return

            if not os.path.exists(file_path):
                messagebox.showerror("Lỗi", "File không tồn tại!")
                return

            if self.excel_processor:
                is_large, file_info = self.excel_processor.is_large_file(file_path)

                if is_large:
                    response = messagebox.askyesno(
                        "Large File Detected",
                        f"File này khá lớn ({file_info['size_mb']} MB).\n\n"
                        f"Sẽ sử dụng chunked processing để tránh memory overflow.\n"
                        f"Chunk size: {file_info['recommended_chunk_size']} rows\n\n"
                        f"Tiếp tục?"
                    )
                    if not response:
                        return

                    self.is_large_file = True
                else:
                    self.is_large_file = False

            self.imported_file_path = file_path
            self.imported_file_name = os.path.basename(file_path)
            self.imported_data = True
            self.manual_data_entered = False

            self._lock_manual_inputs()

            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            result_message = (
                f"✅ Import thành công!\n\n"
                f"📁 File: {self.imported_file_name}\n"
                f"📂 Đường dẫn: {file_path}\n"
                f"📊 Kích thước: {file_size_mb:.2f} MB\n"
            )

            if self.is_large_file:
                result_message += f"\n⚠️ Large file - Sẽ dùng chunked processing"

            result_message += f"\n\nNhấn 'Xử lý Excel' để bắt đầu encode."

            self._update_result_display(result_message)
            self.excel_status_label.config(text=f"📁 Excel: {self.imported_file_name[:20]}...")

            self.frame_buttons_manual.grid_remove()
            self.frame_buttons_excel.grid()

        except Exception as e:
            messagebox.showerror("Lỗi Import", f"Lỗi import Excel:\n{str(e)}")

    def _process_excel(self):
        try:
            if not self.imported_data or not self.imported_file_path:
                messagebox.showwarning("Cảnh báo", "Chưa import file Excel nào!")
                return

            if not self.excel_processor:
                messagebox.showerror("Lỗi", "Excel Processor chưa sẵn sàng!")
                return

            if not os.path.exists(self.imported_file_path):
                messagebox.showerror("Lỗi", f"File không tồn tại:\n{self.imported_file_path}")
                return

            original_name = os.path.splitext(self.imported_file_name)[0]
            default_output = f"{original_name}_encoded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            output_path = filedialog.asksaveasfilename(
                title="Chọn nơi lưu kết quả",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=default_output
            )

            if not output_path:
                return

            confirm = messagebox.askyesno(
                "Xác nhận",
                f"Bắt đầu xử lý Excel?\n\n"
                f"Input: {self.imported_file_name}\n"
                f"Output: {os.path.basename(output_path)}\n\n"
                f"Quá trình có thể mất vài phút..."
            )

            if not confirm:
                return

            self.btn_import_excel.config(state='disabled')
            for widget in self.frame_buttons_excel.winfo_children():
                widget.config(state='disabled')

            def update_progress(current, total, errors):
                progress_pct = (current / total * 100) if total > 0 else 0
                message = (
                    f"⏳ Đang xử lý Excel...\n\n"
                    f"📊 Progress: {current}/{total} ({progress_pct:.1f}%)\n"
                    f"✅ Thành công: {current - errors}\n"
                    f"❌ Lỗi: {errors}\n\n"
                    f"Vui lòng đợi..."
                )
                self._update_result_display(message)
                self.window.update()

            def process_thread():
                try:
                    result = self.excel_processor.process_file_auto(
                        input_path=self.imported_file_path,
                        output_path=output_path,
                        progress_callback=update_progress
                    )

                    self.window.after(0, lambda: self._show_processing_result(result))

                except Exception as e:
                    error_msg = f"Lỗi xử lý Excel:\n{str(e)}"
                    self.window.after(0, lambda: self._show_processing_error(error_msg))

            thread = threading.Thread(target=process_thread, daemon=True)
            thread.start()

            self._update_result_display(
                "⏳ Đang khởi động xử lý Excel...\n\n"
                "Vui lòng đợi..."
            )

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý Excel:\n{str(e)}")
            self._re_enable_buttons()

    def _show_processing_result(self, result):
        """Hiển thị kết quả xử lý (gọi từ main thread)"""
        try:
            if result['success']:
                success_rate = (result['processed'] / result['total'] * 100) if result['total'] > 0 else 0

                message = (
                    f"✅ Xử lý Excel hoàn tất!\n\n"
                    f"📊 Tổng số rows: {result['total']}\n"
                    f"✅ Thành công: {result['processed']}\n"
                    f"❌ Lỗi: {result['errors']}\n"
                    f"📈 Tỷ lệ thành công: {success_rate:.1f}%\n\n"
                    f"💾 File kết quả:\n{os.path.basename(result['output_file'])}\n\n"
                )

                if 'chunks_processed' in result:
                    message += f"📦 Chunks processed: {result['chunks_processed']}\n\n"

                message += f"📂 Đường dẫn đầy đủ:\n{result['output_file']}"

                self._update_result_display(message)

                # Ask to open file
                open_file = messagebox.askyesno(
                    "Thành công",
                    f"Xử lý hoàn tất!\n\n"
                    f"Thành công: {result['processed']}/{result['total']}\n"
                    f"Lỗi: {result['errors']}\n\n"
                    f"Bạn có muốn mở file kết quả không?"
                )

                if open_file:
                    import platform
                    import subprocess

                    if platform.system() == 'Windows':
                        os.startfile(result['output_file'])
                    elif platform.system() == 'Darwin':  # macOS
                        subprocess.call(['open', result['output_file']])
                    else:  # Linux
                        subprocess.call(['xdg-open', result['output_file']])
            else:
                # ✅ HANDLE VALIDATION ERROR (thiếu columns)
                error_msg = result.get('error', 'Unknown error')

                # Check if it's a column validation error
                if "thiếu các cột" in error_msg or "thiếu columns" in error_msg:
                    # Display detailed error with formatting
                    self._update_result_display(
                        f"❌ Validation Error\n\n{error_msg}"
                    )

                    messagebox.showerror(
                        "File Excel không hợp lệ",
                        f"{error_msg}\n\n"
                        f"💡 Giải pháp:\n"
                        f"1. Kiểm tra lại Shape A, B trong dropdown\n"
                        f"2. Hoặc thêm các cột thiếu vào Excel\n"
                        f"3. Hoặc chọn shape khác phù hợp với Excel"
                    )
                else:
                    # Generic error
                    self._update_result_display(f"❌ Lỗi xử lý:\n\n{error_msg}")
                    messagebox.showerror("Lỗi", error_msg)

        finally:
            self._re_enable_buttons()

    def _show_processing_error(self, error_msg):
        self._update_result_display(f"❌ Lỗi xử lý:\n\n{error_msg}")
        messagebox.showerror("Lỗi", error_msg)
        self._re_enable_buttons()

    def _re_enable_buttons(self):
        try:
            self.btn_import_excel.config(state='normal')
            for widget in self.frame_buttons_excel.winfo_children():
                widget.config(state='normal')
        except:
            pass

    def _quit_import_mode(self):
        try:
            result = messagebox.askyesno(
                "Thoát chế độ import",
                "Bạn có chắc muốn thoát chế độ import Excel?\n\n"
                "Dữ liệu import sẽ bị xóa và bạn có thể nhập thủ công lại."
            )

            if result:
                self.imported_data = False
                self.imported_file_path = ""
                self.imported_file_name = ""
                self.manual_data_entered = False
                self.is_large_file = False

                self._unlock_manual_inputs()

                self._update_result_display(
                    "✅ Đã quay lại chế độ nhập thủ công.\n\n"
                    "Bạn có thể nhập dữ liệu hoặc import Excel mới."
                )

                self.excel_status_label.config(text="📋 Excel: ✅ Ready")

                self.frame_buttons_excel.grid_remove()
                self.frame_buttons_manual.grid_remove()

                self.btn_import_excel.config(state='normal')

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi thoát chế độ import:\n{str(e)}")

    def _lock_manual_inputs(self):
        entries = self._get_all_input_entries()
        for entry in entries:
            try:
                entry.config(state='disabled', bg='#E0E0E0')
            except:
                pass

    def _unlock_manual_inputs(self):
        entries = self._get_all_input_entries()
        for entry in entries:
            try:
                entry.config(state='normal', bg='white')
                entry.delete(0, tk.END)
            except:
                pass

    def _show_ready_message(self):
        if self.geometry_service:
            message = "✅ Geometry V2 Service Ready!\n\n7 hình học: Điểm, Vecto, Đường thẳng, Mặt phẳng, Đường tròn, Mặt cầu, Tam giác\n10 phép tính: Tương giao, Khoảng cách, Diện tích, Thể tích, PT đường thẳng, PT mặt phẳng, Góc, Tích vô hướng, Vecto đơn vị, Phép tính tam giác"
        else:
            message = "⚠️ Service chưa khởi tạo\n\nGiao diện UI đã sẵn sàng."
        self.entry_tong.insert(tk.END, message)

    def _process_excel(self):
        """Xử lý Excel với validation columns theo UI dropdown"""
        try:
            if not self.imported_data or not self.imported_file_path:
                messagebox.showwarning("Cảnh báo", "Chưa import file Excel!")
                return

            if not self.excel_processor:
                messagebox.showerror("Lỗi", "Excel Processor chưa sẵn sàng!")
                return

            if not os.path.exists(self.imported_file_path):
                messagebox.showerror("Lỗi", f"File không tồn tại:\n{self.imported_file_path}")
                return

            # ✅ LẤY CONFIG TỪ UI DROPDOWNS
            operation = self.pheptoan_var.get()
            shape_a = self.dropdown1_var.get()
            shape_b = self.dropdown2_var.get() if self._requires_group_b() else None
            dimension_a = self.kich_thuoc_A_var.get()
            dimension_b = self.kich_thuoc_B_var.get()
            version = self.phien_ban_var.get().replace("Phiên bản ", "")

            # ✅ VALIDATE UI SELECTIONS
            if not operation:
                messagebox.showerror("Lỗi", "Vui lòng chọn Phép toán từ dropdown!")
                return

            if not shape_a:
                messagebox.showerror("Lỗi", "Vui lòng chọn Shape A từ dropdown!")
                return

            # ✅ SHOW CONFIG CONFIRMATION
            config_msg = (
                f"Xác nhận xử lý Excel?\n\n"
                f"📋 Phép toán: {operation}\n"
                f"🔷 Shape A: {shape_a} ({dimension_a}D)\n"
            )
            if shape_b:
                config_msg += f"🔶 Shape B: {shape_b} ({dimension_b}D)\n"
            config_msg += (
                f"\n💻 Version: {version}\n"
                f"📁 File: {self.imported_file_name}\n\n"
                f"⚙️ App sẽ kiểm tra Excel có đủ columns cho {shape_a}"
            )
            if shape_b:
                config_msg += f" và {shape_b}"
            config_msg += " không.\n\nTiếp tục?"

            confirm = messagebox.askyesno("Xác nhận", config_msg)
            if not confirm:
                return

            # ✅ SELECT OUTPUT PATH
            original_name = os.path.splitext(self.imported_file_name)[0]
            default_output = f"{original_name}_encoded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            output_path = filedialog.asksaveasfilename(
                title="Chọn nơi lưu kết quả",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=default_output
            )

            if not output_path:
                return

            # ✅ DISABLE BUTTONS DURING PROCESSING
            self.btn_import_excel.config(state='disabled')
            for widget in self.frame_buttons_excel.winfo_children():
                widget.config(state='disabled')

            # ✅ PROGRESS CALLBACK
            def update_progress(current, total, errors):
                progress_pct = (current / total * 100) if total > 0 else 0
                message = (
                    f"⏳ Đang xử lý Excel...\n\n"
                    f"📊 Progress: {current}/{total} ({progress_pct:.1f}%)\n"
                    f"✅ Thành công: {current - errors}\n"
                    f"❌ Lỗi: {errors}\n\n"
                    f"Vui lòng đợi..."
                )
                self._update_result_display(message)
                self.window.update()

            # ✅ PROCESS IN THREAD
            def process_thread():
                try:
                    result = self.excel_processor.process_file_auto(
                        input_path=self.imported_file_path,
                        output_path=output_path,
                        progress_callback=update_progress,
                        # Truyền config từ UI
                        operation=operation,
                        shape_a=shape_a,
                        shape_b=shape_b,
                        dimension_a=dimension_a,
                        dimension_b=dimension_b,
                        version=version
                    )

                    self.window.after(0, lambda: self._show_processing_result(result))

                except Exception as e:
                    error_msg = f"Lỗi xử lý Excel:\n{str(e)}"
                    self.window.after(0, lambda: self._show_processing_error(error_msg))

            thread = threading.Thread(target=process_thread, daemon=True)
            thread.start()

            # ✅ SHOW INITIAL MESSAGE
            self._update_result_display(
                f"⏳ Đang kiểm tra Excel columns...\n\n"
                f"Kiểm tra columns cho:\n"
                f"  • {shape_a}\n" +
                (f"  • {shape_b}\n" if shape_b else "") +
                f"\nVui lòng đợi..."
            )

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý Excel:\n{str(e)}")
            self._re_enable_buttons()


if __name__ == "__main__":
    root = tk.Tk()
    app = GeometryV2View(root)
    root.mainloop()
