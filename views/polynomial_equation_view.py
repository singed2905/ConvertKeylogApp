import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

from services.polynomial.polynomial_service import PolynomialService
from services.polynomial.polynomial_template_generator import PolynomialTemplateGenerator
from views.polynomial_excel_ui import PolynomialExcelUI

class PolynomialEquationView:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Polynomial Equation Mode v2.1 - Fully Functional! 💪")
        self.window.geometry("900x1200")
        self.window.configure(bg="#F0F8FF")
        self.window.resizable(True, True)
        self.window.minsize(800, 600)

        self.config = config or {}
        self.manual_data_entered = False
        self.has_result = False
        self.is_imported_mode = False

        self.bac_phuong_trinh_var = tk.StringVar(value="2")
        self.phien_ban_var = tk.StringVar()
        self.coefficient_entries = []
        self.root_entries = []

        # Load configuration
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var.set(self.phien_ban_list[0] if self.phien_ban_list else "fx799")
        
        # Initialize polynomial service
        self.polynomial_service = None
        self._initialize_service()

        # Setup UI
        self._setup_ui()
        self._update_input_fields()
        self._update_button_visibility()
        self.window.after(1000, self._setup_input_bindings)

    # ========== HELPERS ==========
    def _initialize_service(self):
        try:
            self.polynomial_service = PolynomialService(self.config)
            self.polynomial_service.set_degree(int(self.bac_phuong_trinh_var.get()))
            self.polynomial_service.set_version(self.phien_ban_var.get())
        except Exception as e:
            print(f"Warning: Không thể khởi tạo PolynomialService: {e}")
            self.polynomial_service = None

    def _get_available_versions(self):
        try:
            if self.config and 'common' in self.config and 'versions' in self.config['common']:
                versions_data = self.config['common']['versions']
                if 'versions' in versions_data:
                    return versions_data['versions']
        except Exception as e:
            print(f"Warning: Không thể load versions từ config: {e}")
        return ["fx799", "fx991", "fx570", "fx580", "fx115"]

    def _get_polynomial_config(self):
        try:
            if self.config and 'polynomial' in self.config:
                return self.config['polynomial']
        except Exception as e:
            print(f"Warning: Không thể load polynomial config: {e}")
        return None

    # ========== UI SETUP ==========
    def _setup_ui(self):
        main_container = tk.Frame(self.window, bg="#F0F8FF")
        main_container.pack(fill="both", expand=True, padx=15, pady=10)

        # HEADER
        self._create_header(main_container)
        # CONTROL PANEL
        self._create_control_panel(main_container)
        # QUICK ACTIONS
        self._create_quick_actions(main_container)
        # GUIDE
        self._create_guide_section(main_container)
        # INPUT
        self._create_input_section(main_container)
        # ROOTS
        self._create_roots_section(main_container)
        # FINAL RESULT
        self._create_final_result_section(main_container)
        # BUTTONS
        self._create_control_buttons(main_container)
        # STATUS BAR
        self._create_status_bar(main_container)

    def _create_header(self, parent):
        header_frame = tk.Frame(parent, bg="#1E3A8A", height=80)
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)

        title_frame = tk.Frame(header_frame, bg="#1E3A8A")
        title_frame.pack(expand=True, fill="both")

        tk.Label(title_frame, text="📈", font=("Arial", 24), bg="#1E3A8A", fg="white").pack(side="left", padx=(20,10), pady=20)
        tk.Label(title_frame, text="POLYNOMIAL EQUATION MODE v2.1", font=("Arial", 18, "bold"), bg="#1E3A8A", fg="white").pack(side="left", pady=20)

        service_status = "Service: ✅ Ready" if self.polynomial_service else "Service: ⚠️ Error"
        config_status = "Config: ✅ Loaded" if self.config else "Config: ⚠️ Fallback"
        tk.Label(title_frame, text=f"Giải phương trình bậc cao với mã hóa • {service_status} • {config_status}", font=("Arial", 11), bg="#1E3A8A", fg="#B3D9FF").pack(side="right", padx=(0,20), pady=(25,15))

    def _create_control_panel(self, parent):
        frame = tk.LabelFrame(parent, text="⚙️ THIẾT LẬP PHƯƠNG TRÌNH", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#1E3A8A", bd=2, relief="groove")
        frame.pack(fill="x", pady=10)

        row1 = tk.Frame(frame, bg="#FFFFFF"); row1.pack(fill="x", padx=20, pady=15)
        tk.Label(row1, text="Bậc phương trình:", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333", width=15).pack(side="left")
        bac_menu = ttk.Combobox(row1, textvariable=self.bac_phuong_trinh_var, values=["2","3","4"], state="readonly", width=20, font=("Arial", 11))
        bac_menu.pack(side="left", padx=10)
        bac_menu.bind("<<ComboboxSelected>>", self._on_bac_changed)
        self.equation_form_label = tk.Label(row1, text="ax² + bx + c = 0", font=("Arial", 11, "italic"), bg="#FFFFFF", fg="#666"); self.equation_form_label.pack(side="left", padx=20)

        row2 = tk.Frame(frame, bg="#FFFFFF"); row2.pack(fill="x", padx=20, pady=(0,15))
        tk.Label(row2, text="Phiên bản máy:", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333", width=15).pack(side="left")
        phien_ban_menu = ttk.Combobox(row2, textvariable=self.phien_ban_var, values=self.phien_ban_list, state="readonly", width=20, font=("Arial", 11))
        phien_ban_menu.pack(side="left", padx=10)
        phien_ban_menu.bind("<<ComboboxSelected>>", self._on_phien_ban_changed)

        poly_config = self._get_polynomial_config()
        solver_method = poly_config.get('solver', {}).get('method', 'numpy') if poly_config else 'numpy'
        tk.Label(row2, text=f"Solver: {solver_method}", font=("Arial", 9), bg="#FFFFFF", fg="#666").pack(side="right", padx=20)

    def _create_quick_actions(self, parent):
        quick = tk.Frame(parent, bg="#F0F8FF"); quick.pack(fill="x", pady=5)
        tk.Button(quick, text="📝 Tạo Template", command=self._create_template, bg="#1565C0", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Button(quick, text="📁 Import Excel", command=self._import_excel, bg="#FF9800", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Button(quick, text="🔥 Xử lý File Excel", command=lambda: PolynomialExcelUI.run_batch(self.window, lambda: self.bac_phuong_trinh_var.get(), lambda: self.phien_ban_var.get()), bg="#2E7D32", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)

    def _create_guide_section(self, parent):
        guide = tk.LabelFrame(parent, text="💡 HƯỚNG DẪN NHẬP LIỆU", font=("Arial", 10, "bold"), bg="#E8F4FD", fg="#1565C0", bd=1)
        guide.pack(fill="x", pady=5)
        text = ("• Nhập hệ số theo thứ tự từ cao đến thấp (a, b, c cho bậc 2)\n"
                "• Hỗ trợ biểu thức: sqrt(5), sin(pi/2), 1/2, 2^3, log(10)\n"
                "• Ô trống sẽ tự động điền số 0\n"
                "• Phương trình dạng: ax^n + bx^(n-1) + ... + k = 0")
        tk.Label(guide, text=text, font=("Arial", 9), bg="#E8F4FD", fg="#333", justify="left", anchor="w").pack(side="left", padx=15, pady=10)

    def _create_input_section(self, parent):
        self.input_frame = tk.LabelFrame(parent, text="📝 NHẬP HỆ SỐ PHƯƠNG TRÌNH", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#1E3A8A", bd=2, relief="groove")
        self.input_frame.pack(fill="x", pady=10)

    def _create_roots_section(self, parent):
        self.roots_frame = tk.LabelFrame(parent, text="🎯 NGHIỆM PHƯƠNG TRÌNH", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#D35400", bd=2, relief="groove")
        self.roots_frame.pack(fill="x", pady=10)
        txt_container = tk.Frame(self.roots_frame, bg="#FFFFFF"); txt_container.pack(fill="x", padx=15, pady=12)
        self.roots_text = tk.Text(txt_container, width=80, height=8, font=("Courier New", 10), wrap=tk.WORD, bg="#FFF9E6", fg="#D35400")
        self.roots_text.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(txt_container, orient="vertical", command=self.roots_text.yview); sb.pack(side="right", fill="y")
        self.roots_text.config(yscrollcommand=sb.set)
        self.roots_text.insert("1.0", "Chưa có nghiệm được tính")

    def _create_final_result_section(self, parent):
        self.final_frame = tk.LabelFrame(parent, text="📦 KẾT QUẢ TỔNG (CHO MÁY TÍNH)", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#2E7D32", bd=2, relief="groove")
        self.final_frame.pack(fill="x", pady=10)
        self.final_result_text = tk.Text(self.final_frame, width=80, height=3, font=("Courier New", 9, "bold"), wrap=tk.WORD, bg="#F1F8E9", fg="#2E7D32")
        self.final_result_text.pack(padx=15, pady=12, fill="x")
        service_status = "Service Ready" if self.polynomial_service else "Service Failed"
        config_info = "Config loaded" if self.config else "Fallback config"
        self.final_result_text.insert("1.0", f"Polynomial Mode v2.1 - {service_status} | {config_info}")

    def _create_control_buttons(self, parent):
        self.btn_copy_result = tk.Button(parent, text="📋 Copy Kết Quả", command=self._copy_result, bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), width=20)
        self.btn_copy_result.pack(pady=5); self.btn_copy_result.pack_forget()
        button_frame = tk.Frame(parent, bg="#F0F8FF"); button_frame.pack(fill="x", pady=20)
        self.btn_process = tk.Button(button_frame, text="🚀 Giải & Mã hóa", bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=15, height=2, command=self._process_polynomial); self.btn_process.pack(side="left", padx=10)
        self.btn_export = tk.Button(button_frame, text="💾 Export Excel", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=15, height=2, command=self._export_excel); self.btn_export.pack(side="left", padx=10)
        self.btn_reset = tk.Button(button_frame, text="🔄 Reset", bg="#607D8B", fg="white", font=("Arial", 10, "bold"), width=12, height=2, command=self._reset_all); self.btn_reset.pack(side="left", padx=10)
        self.btn_close = tk.Button(button_frame, text="❌ Đóng", bg="#F44336", fg="white", font=("Arial", 10, "bold"), width=12, height=2, command=self.window.destroy); self.btn_close.pack(side="right", padx=10)

    def _create_status_bar(self, parent):
        self.status_label = tk.Label(parent, text="🟢 Sẵn sàng nhập liệu phương trình bậc 2", font=("Arial", 10, "bold"), bg="#F0F8FF", fg="#2E7D32", relief="sunken", bd=1, anchor="w")
        self.status_label.pack(fill="x", pady=(10,0))
        tk.Label(parent, text="Polynomial Mode v2.1 • Hỗ trợ giải phương trình bậc cao • Mã hóa tự động • Config-driven", font=("Arial", 8), bg="#F0F8FF", fg="#666").pack(pady=5)

    # ===== Handlers / Processing / Export / Reset (copy from previous full version) =====
    # (Giữ nguyên các phương thức _on_bac_changed, _on_phien_ban_changed, _setup_input_bindings,
    #  _on_manual_input, _check_manual_data, _update_input_fields, _create_coefficient_inputs,
    #  _get_coefficient_labels, _update_button_visibility, _show_copy_button, _hide_copy_button,
    #  _process_polynomial, _show_final_result, _copy_result, _create_template, _import_excel,
    #  _export_excel, _reset_all) — tồn tại trong bản trước đó.
