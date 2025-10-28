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

    # Placeholder methods giống TL (chưa có logic)
    def _on_operation_selected(self, operation): pass
    def _on_operation_selected_callback(self, *args): pass
    def _on_version_changed(self, *args): pass
    def _on_kich_thuoc_changed(self, *args): pass
    def _on_dropdown_change(self, *args): pass
    def _update_system_info(self): pass
    def _update_quick_stats(self): pass
    def _show_quick_help(self): 
        messagebox.showinfo("Hướng dẫn", "Geometry Mode: Chọn phép toán → Chọn hình dạng → Nhập dữ liệu → Thực thi")
    def _import_from_excel(self): messagebox.showinfo("Import", "Chức năng import sẽ được implement")
    def _thuc_thi_A(self): messagebox.showinfo("Xử lý", "Xử lý nhóm A sẽ được implement")
    def _thuc_thi_B(self): messagebox.showinfo("Xử lý", "Xử lý nhóm B sẽ được implement")
    def _thuc_thi_tat_ca(self): messagebox.showinfo("Thực thi", "Thực thi tất cả sẽ được implement")
    def _export_to_excel(self): messagebox.showinfo("Xuất", "Xuất Excel sẽ được implement")
    def _thuc_thi_import_excel(self): messagebox.showinfo("Import Excel", "Xử lý import Excel sẽ được implement")
    def _quit_import_mode(self): messagebox.showinfo("Quay lại", "Quay lại chế độ manual")
    def _setup_ui(self): pass
    def _setup_dropdowns(self, parent): pass
    def _setup_group_a_frames(self): pass
    def _setup_group_b_frames(self): pass
    def _setup_control_frame(self): pass
    def _setup_bindings(self): pass
    def _update_operation_menu(self): pass
    def start_header_updates(self): pass
    def _hide_all_input_frames(self): pass
    def _hide_action_buttons(self): pass