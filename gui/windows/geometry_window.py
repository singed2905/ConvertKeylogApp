"""Geometry window - tương tự GeometryView của TL."""

import tkinter as tk
from tkinter import messagebox
import json
import os
import gc


class GeometryWindow:
    """Geometry Mode window implementation - giống TL GeometryView."""
    
    def __init__(self, window):
        self.window = window
        
        # Khởi tạo cửa sổ giống TL
        self.window.title("Geometry Mode")
        self.window.geometry("700x700")
        self.window.configure(bg="#F8F9FA")

        # Biến và trạng thái giống TL
        self._initialize_variables()
        self._initialize_data_storage()

        # Tạo giao diện giống TL
        self._create_smart_header()
        self._setup_ui()
        self._setup_bindings()

        # Khởi động giống TL
        self._update_operation_menu()
        self.start_header_updates()
        self._hide_all_input_frames()
        self._hide_action_buttons()

    def _initialize_variables(self):
        """Khởi tạo tất cả biến - giống TL"""
        self.dropdown1_var = tk.StringVar(value="")
        self.dropdown2_var = tk.StringVar(value="")
        self.kich_thuoc_A_var = tk.StringVar(value="3")
        self.kich_thuoc_B_var = tk.StringVar(value="3")
        self.pheptoan_var = tk.StringVar(value="")

        # Load phiên bản giống TL
        self.phien_ban_list = self._load_phien_ban_from_json()
        self.phien_ban_var = tk.StringVar(value=self.phien_ban_list[0] if self.phien_ban_list else "Phiên bản 1.0")

        # Trạng thái giống TL
        self.imported_data = False
        self.manual_data_entered = False
        self.imported_file_path = ""

    def _initialize_data_storage(self):
        """Khởi tạo storage cho kết quả - giống TL"""
        self.ket_qua_A1 = []; self.ket_qua_X1 = []; self.ket_qua_N1 = []
        self.ket_qua_A2 = []; self.ket_qua_X2 = []; self.ket_qua_N2 = []
        self.ket_qua_diem_A = []; self.ket_qua_diem_B = []
        self.ket_qua_duong_tron_A = []; self.ket_qua_mat_cau_A = []
        self.ket_qua_duong_tron_B = []; self.ket_qua_mat_cau_B = []

    def _load_phien_ban_from_json(self, file_path: str = "config/versions.json") -> list:
        """Load danh sách phiên bản từ JSON - giống TL"""
        try:
            # TODO: Implement actual JSON loading
            return ["fx799", "fx880"]
        except Exception as e:
            print(f"Lỗi khi đọc file versions.json: {e}")
            return ["fx799", "fx880"]

    def _create_smart_header(self):
        """Tạo header thông minh - giống TL"""
        HEADER_COLORS = {
            "primary": "#2E86AB", "secondary": "#1B5299", "text": "#FFFFFF",
            "accent": "#F18F01", "success": "#4CAF50", "warning": "#FF9800"
        }

        # Main header frame giống TL
        self.header_frame = tk.Frame(self.window, bg=HEADER_COLORS["primary"], height=80)
        self.header_frame.pack(fill="x", padx=10, pady=5)
        self.header_frame.pack_propagate(False)

        header_content = tk.Frame(self.header_frame, bg=HEADER_COLORS["primary"])
        header_content.pack(fill="both", expand=True, padx=15, pady=10)

        # === PHẦN TRÁI: Logo và Operation ===
        left_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        left_section.pack(side="left", fill="y")

        # Logo giống TL
        logo_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        logo_frame.pack(side="top", fill="x")
        tk.Label(logo_frame, text="🧮", font=("Arial", 20),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        tk.Label(logo_frame, text="Geometry Mode", font=("Arial", 16, "bold"),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left", padx=(5, 20))

        # Operation selector giống TL
        operation_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        operation_frame.pack(side="top", fill="x", pady=(5, 0))
        tk.Label(operation_frame, text="Phép toán:", font=("Arial", 10),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")

        self.operation_menu = tk.OptionMenu(operation_frame, self.pheptoan_var, "")
        self.operation_menu.config(
            bg=HEADER_COLORS["secondary"], fg=HEADER_COLORS["text"],
            font=("Arial", 10, "bold"), width=15, relief="flat", borderwidth=0
        )
        self.operation_menu.pack(side="left", padx=(5, 0))

        # === PHẦN GIỮA: Version và Stats ===
        center_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        center_section.pack(side="left", fill="both", expand=True, padx=20)

        # Version selector giống TL
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

        # Quick stats giống TL
        self.stats_frame = tk.Frame(center_section, bg=HEADER_COLORS["primary"])
        self.stats_frame.pack(side="top", fill="x", pady=(5, 0))
        self.quick_stats_label = tk.Label(
            self.stats_frame, text="🔧 Sẵn sàng", font=("Arial", 9),
            bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]
        )
        self.quick_stats_label.pack(side="left")

        # === PHẦN PHẢI: System Info ===
        right_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        right_section.pack(side="right", fill="y")

        # System info giống TL
        sys_info_frame = tk.Frame(right_section, bg=HEADER_COLORS["primary"])
        sys_info_frame.pack(side="top", fill="x")
        self.memory_label = tk.Label(
            sys_info_frame, text="", font=("Arial", 8),
            bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]
        )
        self.memory_label.pack(side="top", anchor="e")
        self.status_label = tk.Label(
            sys_info_frame, text="✅ Hệ thống ổn định", font=("Arial", 8),
            bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["success"]
        )
        self.status_label.pack(side="top", anchor="e")

        # Quick action buttons giống TL
        action_frame = tk.Frame(right_section, bg=HEADER_COLORS["primary"])
        action_frame.pack(side="top", fill="x", pady=(5, 0))
        self.btn_quick_help = tk.Button(
            action_frame, text="❓", font=("Arial", 10),
            bg=HEADER_COLORS["secondary"], fg="white", relief="flat", width=3,
            command=self._show_quick_help
        )
        self.btn_quick_help.pack(side="right", padx=(2, 0))

    def _setup_ui(self):
        """Setup giao diện chính - giống TL"""
        self.main_container = tk.Frame(self.window, bg="#F8F9FA")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Top frame với dropdown giống TL
        top_frame = tk.Frame(self.main_container, bg="#F8F9FA")
        top_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        self._setup_dropdowns(top_frame)
        self._setup_group_a_frames()
        self._setup_group_b_frames()
        self._setup_control_frame()

    def _setup_dropdowns(self, parent):
        """Setup dropdown chọn nhóm - giống TL"""
        # TODO: Load shapes từ controller
        shapes = ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"]

        self.label_A = tk.Label(parent, text="Chọn nhóm A:", bg="#F8F9FA", font=("Arial", 10))
        self.label_A.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.label_A.grid_remove()

        self.dropdown1_menu = tk.OptionMenu(parent, self.dropdown1_var, *shapes)
        self.dropdown1_menu.config(width=15, font=("Arial", 9))
        self.dropdown1_menu.grid(row=0, column=1, padx=5, pady=5)
        self.dropdown1_menu.grid_remove()

        self.label_B = tk.Label(parent, text="Chọn nhóm B:", bg="#F8F9FA", font=("Arial", 10))
        self.label_B.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.label_B.grid_remove()

        self.dropdown2_menu = tk.OptionMenu(parent, self.dropdown2_var, *shapes)
        self.dropdown2_menu.config(width=15, font=("Arial", 9))
        self.dropdown2_menu.grid(row=0, column=3, padx=5, pady=5)
        self.dropdown2_menu.grid_remove()

    def _setup_group_a_frames(self):
        """Setup frames cho nhóm A - giống TL"""
        # Frame Điểm A giống TL
        self.frame_A_diem = tk.LabelFrame(
            self.main_container, text="🎯 NHÓM A - Điểm",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_diem.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_diem, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(self.frame_A_diem, self.kich_thuoc_A_var, "2", "3").grid(row=0, column=1)

        tk.Label(self.frame_A_diem, text="Nhập toạ độ:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_dau_vao_diem_A = tk.Entry(self.frame_A_diem, width=40)
        self.entry_dau_vao_diem_A.grid(row=1, column=1)

        self.entry_Xd_A = tk.Entry(self.frame_A_diem, width=10)
        self.entry_Yd_A = tk.Entry(self.frame_A_diem, width=10)
        self.entry_Zd_A = tk.Entry(self.frame_A_diem, width=10)
        self.entry_Xd_A.grid(row=2, column=0)
        self.entry_Yd_A.grid(row=2, column=1)
        self.entry_Zd_A.grid(row=2, column=2)

        # Frame Đường thẳng A giống TL
        self.frame_A_duong = tk.LabelFrame(
            self.main_container, text="📏 NHÓM A - Đường thẳng",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_duong.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_duong, text="Nhập A1,B1,C1:", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_dau_vao_A1 = tk.Entry(self.frame_A_duong, width=40)
        self.entry_dau_vao_A1.grid(row=0, column=1)

        tk.Label(self.frame_A_duong, text="Nhập X1,Y1,Z1:", bg="#FFFFFF").grid(row=2, column=0)
        self.entry_dau_vao_X1 = tk.Entry(self.frame_A_duong, width=40)
        self.entry_dau_vao_X1.grid(row=2, column=1)

        # Các entry riêng lẻ giống TL
        self.entry_A1 = tk.Entry(self.frame_A_duong, width=10)
        self.entry_B1 = tk.Entry(self.frame_A_duong, width=10)
        self.entry_C1 = tk.Entry(self.frame_A_duong, width=10)
        self.entry_X1 = tk.Entry(self.frame_A_duong, width=10)
        self.entry_Y1 = tk.Entry(self.frame_A_duong, width=10)
        self.entry_Z1 = tk.Entry(self.frame_A_duong, width=10)
        self.entry_A1.grid(row=1, column=0); self.entry_B1.grid(row=1, column=1); self.entry_C1.grid(row=1, column=2)
        self.entry_X1.grid(row=3, column=0); self.entry_Y1.grid(row=3, column=1); self.entry_Z1.grid(row=3, column=2)

        # Frame Mặt phẳng A giống TL
        self.frame_A_mat = tk.LabelFrame(
            self.main_container, text="📐 NHÓM A - Mặt phẳng (4 tham số)",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_mat.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        # Input boxes giống TL
        tk.Label(self.frame_A_mat, text="Input - Nhập hệ số:", bg="#FFFFFF").grid(row=0, column=0, columnspan=8, pady=5)
        tk.Label(self.frame_A_mat, text="a:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_N1_in = tk.Entry(self.frame_A_mat, width=10); self.entry_N1_in.grid(row=1, column=1)
        tk.Label(self.frame_A_mat, text="b:", bg="#FFFFFF").grid(row=1, column=2)
        self.entry_N2_in = tk.Entry(self.frame_A_mat, width=10); self.entry_N2_in.grid(row=1, column=3)
        tk.Label(self.frame_A_mat, text="c:", bg="#FFFFFF").grid(row=1, column=4)
        self.entry_N3_in = tk.Entry(self.frame_A_mat, width=10); self.entry_N3_in.grid(row=1, column=5)
        tk.Label(self.frame_A_mat, text="d:", bg="#FFFFFF").grid(row=1, column=6)
        self.entry_N4_in = tk.Entry(self.frame_A_mat, width=10); self.entry_N4_in.grid(row=1, column=7)

        # Output boxes giống TL
        tk.Label(self.frame_A_mat, text="Output - Kết quả mã hóa:", bg="#FFFFFF").grid(row=2, column=0, columnspan=8, pady=5)
        tk.Label(self.frame_A_mat, text="a:", bg="#FFFFFF").grid(row=3, column=0)
        self.entry_N1_out = tk.Entry(self.frame_A_mat, width=10); self.entry_N1_out.grid(row=3, column=1); self.entry_N1_out.config(state='readonly')
        tk.Label(self.frame_A_mat, text="b:", bg="#FFFFFF").grid(row=3, column=2)
        self.entry_N2_out = tk.Entry(self.frame_A_mat, width=10); self.entry_N2_out.grid(row=3, column=3); self.entry_N2_out.config(state='readonly')
        tk.Label(self.frame_A_mat, text="c:", bg="#FFFFFF").grid(row=3, column=4)
        self.entry_N3_out = tk.Entry(self.frame_A_mat, width=10); self.entry_N3_out.grid(row=3, column=5); self.entry_N3_out.config(state='readonly')
        tk.Label(self.frame_A_mat, text="d:", bg="#FFFFFF").grid(row=3, column=6)
        self.entry_N4_out = tk.Entry(self.frame_A_mat, width=10); self.entry_N4_out.grid(row=3, column=7); self.entry_N4_out.config(state='readonly')

        # Ẩn tất cả frame ban đầu giống TL
        for frame in [self.frame_A_diem, self.frame_A_duong, self.frame_A_mat]:
            frame.grid_remove()

    def _setup_group_b_frames(self):
        """Setup frames cho nhóm B - giống TL"""
        # Tương tự nhóm A nhưng với màu khác giống TL
        self.frame_B_diem = tk.LabelFrame(
            self.main_container, text="🎯 NHÓM B - Điểm",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        self.frame_B_diem.grid(row=6, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_B_diem, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(self.frame_B_diem, self.kich_thuoc_B_var, "2", "3").grid(row=0, column=1)

        tk.Label(self.frame_B_diem, text="Nhập toạ độ:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_dau_vao_diem_B = tk.Entry(self.frame_B_diem, width=40)
        self.entry_dau_vao_diem_B.grid(row=1, column=1)

        self.entry_Xd_B = tk.Entry(self.frame_B_diem, width=10)
        self.entry_Yd_B = tk.Entry(self.frame_B_diem, width=10)
        self.entry_Zd_B = tk.Entry(self.frame_B_diem, width=10)
        self.entry_Xd_B.grid(row=2, column=0)
        self.entry_Yd_B.grid(row=2, column=1)
        self.entry_Zd_B.grid(row=2, column=2)

        # Ẩn frame giống TL
        self.frame_B_diem.grid_remove()

    def _setup_control_frame(self):
        """Setup control frame với buttons và result display - giống TL"""
        self.frame_tong = tk.LabelFrame(
            self.main_container, text="🎉 KẾT QUẢ & ĐIỀU KHIỂN",
            bg="#FFFFFF", font=("Arial", 10, "bold")
        )
        self.frame_tong.grid(row=11, column=0, columnspan=4, padx=10, pady=10, sticky="we")

        # THay thế Entry bằng Text để xuống dòng giống TL
        self.entry_tong = tk.Text(
            self.frame_tong,
            width=80,
            height=3,  # Chiều cao 3 dòng
            font=("Arial", 10),
            wrap=tk.WORD,  # Tự động xuống dòng theo từ
            bg="#F8F9FA",
            fg="black",
            relief="solid",
            bd=1,
            padx=5,  # Padding ngang
            pady=5  # Padding dọc
        )
        self.entry_tong.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="we")

        # Tạo thanh cuộn dọc cho Text widget giống TL
        scrollbar = tk.Scrollbar(self.frame_tong, orient="vertical", command=self.entry_tong.yview)
        scrollbar.grid(row=0, column=4, sticky="ns", pady=5)
        self.entry_tong.config(yscrollcommand=scrollbar.set)

        # Nút Import Excel - Ẩn ban đầu giống TL
        self.btn_import_excel = tk.Button(
            self.frame_tong, text="📁 Import Excel",
            command=self._import_from_excel,
            bg="#FF9800", fg="white", font=("Arial", 9, "bold")
        )
        self.btn_import_excel.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        self.btn_import_excel.grid_remove()

        # Frame cho nút thủ công giống TL
        self.frame_buttons_manual = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_manual.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")

        tk.Button(self.frame_buttons_manual, text="🔄 Xử lý Nhóm A",
                  command=self._thuc_thi_A,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons_manual, text="🔄 Xử lý Nhóm B",
                  command=self._thuc_thi_B,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_buttons_manual, text="🚀 Thực thi tất cả",
                  command=self._thuc_thi_tat_ca,
                  bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5)
        tk.Button(self.frame_buttons_manual, text="💾 Xuất Excel",
                  command=self._export_to_excel,
                  bg="#FF9800", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5)

        self.frame_buttons_manual.grid_remove()

        # Frame cho nút import giống TL
        self.frame_buttons_import = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_import.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")

        tk.Button(self.frame_buttons_import, text="🚀 Xử lý File Excel",
                  command=self._thuc_thi_import_excel,
                  bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons_import, text="📁 Import File Khác",
                  command=self._import_from_excel,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_buttons_import, text="↩️ Quay lại",
                  command=self._quit_import_mode,
                  bg="#F44336", fg="white", font=("Arial", 9)).grid(row=0, column=2, padx=5)

        self.frame_buttons_import.grid_remove()

    def _setup_bindings(self):
        """Setup event bindings - giống TL"""
        self.kich_thuoc_A_var.trace_add("write", self._on_kich_thuoc_changed)
        self.kich_thuoc_B_var.trace_add("write", self._on_kich_thuoc_changed)
        self.dropdown1_var.trace_add("write", self._on_dropdown_change)
        self.dropdown2_var.trace_add("write", self._on_dropdown_change)
        self.pheptoan_var.trace_add("write", self._on_operation_selected_callback)
        self.phien_ban_var.trace_add("write", self._on_version_changed)

    def _update_operation_menu(self):
        """Cập nhật operation menu - giống TL"""
        operations_with_icons = {
            "Tương giao": "", "Khoảng cách": "", "Diện tích": "",
            "Thể tích": "", "PT đường thẳng": ""
        }

        menu = self.operation_menu["menu"]
        menu.delete(0, "end")
        for operation, icon in operations_with_icons.items():
            menu.add_command(
                label=f"{operation}",
                command=lambda op=operation: self._on_operation_selected(op)
            )

        if not self.pheptoan_var.get() and operations_with_icons:
            self.pheptoan_var.set(list(operations_with_icons.keys())[0])

    def start_header_updates(self):
        """Bắt đầu cập nhật tự động cho header - giống TL"""
        self._update_system_info()
        self._update_quick_stats()
        self.window.after(5000, self.start_header_updates)

    def _hide_all_input_frames(self):
        """Placeholder - giống TL"""
        pass

    def _hide_action_buttons(self):
        """Placeholder - giống TL"""
        pass

    # Placeholder methods giống TL (chưa có logic)
    def _on_operation_selected(self, operation): pass
    def _on_operation_selected_callback(self, *args): pass
    def _on_version_changed(self, *args): pass
    def _on_kich_thuoc_changed(self, *args): pass
    def _on_dropdown_change(self, *args): pass
    def _update_system_info(self): pass
    def _update_quick_stats(self): pass
    def _show_quick_help(self): pass
    def _import_from_excel(self): pass
    def _thuc_thi_A(self): pass
    def _thuc_thi_B(self): pass
    def _thuc_thi_tat_ca(self): pass
    def _export_to_excel(self): pass
    def _thuc_thi_import_excel(self): pass
    def _quit_import_mode(self): pass

    def setup_ui(self):
        """Override từ BaseWindow - đã implement trong _setup_ui()"""
        pass

    def run(self):
        """Chạy ứng dụng - giống TL"""
        # Căn giữa cửa sổ
        self.window.eval('tk::PlaceWindow . center')
        self.window.mainloop()