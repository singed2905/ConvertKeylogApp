"""Geometry Input Panels - Input Manager"""
import tkinter as tk

class GeometryInputManager:
    """Quản lý các panel nhập liệu cho 5 hình học"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
        self.main_container = None
        
        # Dictionary chứa tất cả frames
        self.frames = {}
    
    def create_all_input_frames(self, main_container):
        """Tạo tất cả các frame nhập liệu cho đầy đủ 5 hình"""
        self.main_container = main_container
        
        # Tạo frames cho nhóm A
        self._create_point_frame_A()
        self._create_line_frame_A()
        self._create_plane_frame_A()
        self._create_circle_frame_A()
        self._create_sphere_frame_A()
        
        # Tạo frames cho nhóm B
        self._create_point_frame_B()
        self._create_line_frame_B()
        self._create_plane_frame_B()
        self._create_circle_frame_B()
        self._create_sphere_frame_B()
    
    # ========== NHÓM A FRAMES ==========
    def _create_point_frame_A(self):
        """Tạo frame điểm A"""
        self.frames['frame_A_diem'] = tk.LabelFrame(
            self.main_container, text="🎯 NHÓM A - Điểm",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        frame = self.frames['frame_A_diem']
        frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(frame, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(frame, self.parent.kich_thuoc_A_var, "2", "3").grid(row=0, column=1)
        
        tk.Label(frame, text="Nhập tọa độ (x,y,z):", bg="#FFFFFF").grid(row=1, column=0)
        self.parent.entry_diem_A = tk.Entry(frame, width=40)
        self.parent.entry_diem_A.grid(row=1, column=1, columnspan=2, sticky="we")
        
        frame.grid_remove()
    
    def _create_line_frame_A(self):
        """Tạo frame đường thẳng A"""
        self.frames['frame_A_duong'] = tk.LabelFrame(
            self.main_container, text="📏 NHÓM A - Đường thẳng",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        frame = self.frames['frame_A_duong']
        frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(frame, text="Điểm (A,B,C):", bg="#FFFFFF").grid(row=0, column=0)
        self.parent.entry_point_A = tk.Entry(frame, width=30)
        self.parent.entry_point_A.grid(row=0, column=1)
        
        tk.Label(frame, text="Vector (X,Y,Z):", bg="#FFFFFF").grid(row=1, column=0)
        self.parent.entry_vector_A = tk.Entry(frame, width=30)
        self.parent.entry_vector_A.grid(row=1, column=1)
        
        frame.grid_remove()
    
    def _create_plane_frame_A(self):
        """Tạo frame mặt phẳng A"""
        self.frames['frame_A_plane'] = tk.LabelFrame(
            self.main_container, text="📐 NHÓM A - Mặt phẳng",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        frame = self.frames['frame_A_plane']
        frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(frame, text="Phương trình ax+by+cz+d=0:", bg="#FFFFFF").grid(row=0, column=0, columnspan=4)
        
        tk.Label(frame, text="a:", bg="#FFFFFF", width=3).grid(row=1, column=0, sticky="e")
        self.parent.entry_a_A = tk.Entry(frame, width=15)
        self.parent.entry_a_A.grid(row=1, column=1, padx=5)
        
        tk.Label(frame, text="b:", bg="#FFFFFF", width=3).grid(row=1, column=2, sticky="e")
        self.parent.entry_b_A = tk.Entry(frame, width=15)
        self.parent.entry_b_A.grid(row=1, column=3, padx=5)
        
        tk.Label(frame, text="c:", bg="#FFFFFF", width=3).grid(row=2, column=0, sticky="e")
        self.parent.entry_c_A = tk.Entry(frame, width=15)
        self.parent.entry_c_A.grid(row=2, column=1, padx=5)
        
        tk.Label(frame, text="d:", bg="#FFFFFF", width=3).grid(row=2, column=2, sticky="e")
        self.parent.entry_d_A = tk.Entry(frame, width=15)
        self.parent.entry_d_A.grid(row=2, column=3, padx=5)
        
        frame.grid_remove()
    
    def _create_circle_frame_A(self):
        """Tạo frame đường tròn A"""
        self.frames['frame_A_circle'] = tk.LabelFrame(
            self.main_container, text="⭕ NHÓM A - Đường tròn",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        frame = self.frames['frame_A_circle']
        frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(frame, text="Tâm đường tròn (x,y):", bg="#FFFFFF").grid(row=0, column=0)
        self.parent.entry_center_A = tk.Entry(frame, width=25)
        self.parent.entry_center_A.grid(row=0, column=1, padx=5)
        
        tk.Label(frame, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.parent.entry_radius_A = tk.Entry(frame, width=20)
        self.parent.entry_radius_A.grid(row=0, column=3, padx=5)
        
        frame.grid_remove()
    
    def _create_sphere_frame_A(self):
        """Tạo frame mặt cầu A"""
        self.frames['frame_A_sphere'] = tk.LabelFrame(
            self.main_container, text="🌍 NHÓM A - Mặt cầu",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        frame = self.frames['frame_A_sphere']
        frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(frame, text="Tâm mặt cầu (x,y,z):", bg="#FFFFFF").grid(row=0, column=0)
        self.parent.entry_sphere_center_A = tk.Entry(frame, width=25)
        self.parent.entry_sphere_center_A.grid(row=0, column=1, padx=5)
        
        tk.Label(frame, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.parent.entry_sphere_radius_A = tk.Entry(frame, width=20)
        self.parent.entry_sphere_radius_A.grid(row=0, column=3, padx=5)
        
        frame.grid_remove()
    
    # ========== NHÓM B FRAMES ==========
    def _create_point_frame_B(self):
        """Tạo frame điểm B"""
        self.frames['frame_B_diem'] = tk.LabelFrame(
            self.main_container, text="🎯 NHÓM B - Điểm",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        frame = self.frames['frame_B_diem']
        frame.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(frame, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(frame, self.parent.kich_thuoc_B_var, "2", "3").grid(row=0, column=1)
        
        tk.Label(frame, text="Nhập tọa độ (x,y,z):", bg="#FFFFFF").grid(row=1, column=0)
        self.parent.entry_diem_B = tk.Entry(frame, width=40)
        self.parent.entry_diem_B.grid(row=1, column=1, columnspan=2, sticky="we")
        
        frame.grid_remove()
    
    def _create_line_frame_B(self):
        """Tạo frame đường thẳng B"""
        self.frames['frame_B_duong'] = tk.LabelFrame(
            self.main_container, text="📏 NHÓM B - Đường thẳng",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        frame = self.frames['frame_B_duong']
        frame.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(frame, text="Điểm (A,B,C):", bg="#FFFFFF").grid(row=0, column=0)
        self.parent.entry_point_B = tk.Entry(frame, width=30)
        self.parent.entry_point_B.grid(row=0, column=1)
        
        tk.Label(frame, text="Vector (X,Y,Z):", bg="#FFFFFF").grid(row=1, column=0)
        self.parent.entry_vector_B = tk.Entry(frame, width=30)
        self.parent.entry_vector_B.grid(row=1, column=1)
        
        frame.grid_remove()
    
    def _create_plane_frame_B(self):
        """Tạo frame mặt phẳng B"""
        self.frames['frame_B_plane'] = tk.LabelFrame(
            self.main_container, text="📐 NHÓM B - Mặt phẳng",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        frame = self.frames['frame_B_plane']
        frame.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(frame, text="Phương trình ax+by+cz+d=0:", bg="#FFFFFF").grid(row=0, column=0, columnspan=4)
        
        tk.Label(frame, text="a:", bg="#FFFFFF", width=3).grid(row=1, column=0, sticky="e")
        self.parent.entry_a_B = tk.Entry(frame, width=15)
        self.parent.entry_a_B.grid(row=1, column=1, padx=5)
        
        tk.Label(frame, text="b:", bg="#FFFFFF", width=3).grid(row=1, column=2, sticky="e")
        self.parent.entry_b_B = tk.Entry(frame, width=15)
        self.parent.entry_b_B.grid(row=1, column=3, padx=5)
        
        tk.Label(frame, text="c:", bg="#FFFFFF", width=3).grid(row=2, column=0, sticky="e")
        self.parent.entry_c_B = tk.Entry(frame, width=15)
        self.parent.entry_c_B.grid(row=2, column=1, padx=5)
        
        tk.Label(frame, text="d:", bg="#FFFFFF", width=3).grid(row=2, column=2, sticky="e")
        self.parent.entry_d_B = tk.Entry(frame, width=15)
        self.parent.entry_d_B.grid(row=2, column=3, padx=5)
        
        frame.grid_remove()
    
    def _create_circle_frame_B(self):
        """Tạo frame đường tròn B"""
        self.frames['frame_B_circle'] = tk.LabelFrame(
            self.main_container, text="⭕ NHÓM B - Đường tròn",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        frame = self.frames['frame_B_circle']
        frame.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(frame, text="Tâm đường tròn (x,y):", bg="#FFFFFF").grid(row=0, column=0)
        self.parent.entry_center_B = tk.Entry(frame, width=25)
        self.parent.entry_center_B.grid(row=0, column=1, padx=5)
        
        tk.Label(frame, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.parent.entry_radius_B = tk.Entry(frame, width=20)
        self.parent.entry_radius_B.grid(row=0, column=3, padx=5)
        
        frame.grid_remove()
    
    def _create_sphere_frame_B(self):
        """Tạo frame mặt cầu B"""
        self.frames['frame_B_sphere'] = tk.LabelFrame(
            self.main_container, text="🌍 NHÓM B - Mặt cầu",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        frame = self.frames['frame_B_sphere']
        frame.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")
        
        tk.Label(frame, text="Tâm mặt cầu (x,y,z):", bg="#FFFFFF").grid(row=0, column=0)
        self.parent.entry_sphere_center_B = tk.Entry(frame, width=25)
        self.parent.entry_sphere_center_B.grid(row=0, column=1, padx=5)
        
        tk.Label(frame, text="Bán kính:", bg="#FFFFFF").grid(row=0, column=2)
        self.parent.entry_sphere_radius_B = tk.Entry(frame, width=20)
        self.parent.entry_sphere_radius_B.grid(row=0, column=3, padx=5)
        
        frame.grid_remove()
    
    def update_input_frames(self):
        """Cập nhật hiển thị các frame nhập liệu"""
        # Ẩn các frame cũ trước
        all_frame_names = [
            'frame_A_diem', 'frame_A_duong', 'frame_A_plane', 'frame_A_circle', 'frame_A_sphere',
            'frame_B_diem', 'frame_B_duong', 'frame_B_plane', 'frame_B_circle', 'frame_B_sphere'
        ]
        
        for frame_name in all_frame_names:
            if frame_name in self.frames:
                try:
                    self.frames[frame_name].grid_remove()
                except:
                    pass
        
        # Hiện thị frame cho nhóm A
        shape_A = self.parent.dropdown1_var.get()
        if shape_A:
            self._show_input_frame_A(shape_A)
        
        # Hiện thị frame cho nhóm B (nếu cần)
        if hasattr(self.parent, 'operation_manager') and self.parent.operation_manager.needs_shape_B():
            shape_B = self.parent.dropdown2_var.get()
            if shape_B:
                self._show_input_frame_B(shape_B)
    
    def _show_input_frame_A(self, shape):
        """Hiện thị frame nhập liệu cho nhóm A"""
        frame_map = {
            "Điểm": "frame_A_diem",
            "Đường thẳng": "frame_A_duong",
            "Mặt phẳng": "frame_A_plane",
            "Đường tròn": "frame_A_circle",
            "Mặt cầu": "frame_A_sphere"
        }
        
        frame_name = frame_map.get(shape)
        if frame_name and frame_name in self.frames:
            try:
                self.frames[frame_name].grid()
            except Exception as e:
                print(f"Warning: Could not show frame A for {shape}: {e}")
    
    def _show_input_frame_B(self, shape):
        """Hiện thị frame nhập liệu cho nhóm B"""
        frame_map = {
            "Điểm": "frame_B_diem",
            "Đường thẳng": "frame_B_duong",
            "Mặt phẳng": "frame_B_plane",
            "Đường tròn": "frame_B_circle",
            "Mặt cầu": "frame_B_sphere"
        }
        
        frame_name = frame_map.get(shape)
        if frame_name and frame_name in self.frames:
            try:
                self.frames[frame_name].grid()
            except Exception as e:
                print(f"Warning: Could not show frame B for {shape}: {e}")