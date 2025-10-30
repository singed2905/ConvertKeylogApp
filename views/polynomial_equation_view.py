import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

from services.polynomial.polynomial_service import PolynomialService
from services.polynomial.polynomial_template_generator import PolynomialTemplateGenerator

class PolynomialEquationView:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Polynomial Equation Mode v2.1 - Fully Functional! 💪")
        self.window.geometry("900x1000")
        self.window.configure(bg="#F0F8FF")
        
        # Make window resizable
        self.window.resizable(True, True)
        self.window.minsize(800, 600)

        # Configure grid weights for responsive behavior
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Config và state management
        self.config = config or {}
        self.manual_data_entered = False
        self.has_result = False
        self.is_imported_mode = False

        # Variables
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
        
        # Bind input detection
        self.window.after(1000, self._setup_input_bindings)

    def _initialize_service(self):
        """Initialize PolynomialService"""
        try:
            self.polynomial_service = PolynomialService(self.config)
            self.polynomial_service.set_degree(int(self.bac_phuong_trinh_var.get()))
            self.polynomial_service.set_version(self.phien_ban_var.get())
        except Exception as e:
            print(f"Warning: Không thể khởi tạo PolynomialService: {e}")
            self.polynomial_service = None
    
    def _get_available_versions(self):
        """Lấy danh sách phiên bản từ config hoặc sử dụng mặc định"""
        try:
            if self.config and 'common' in self.config and 'versions' in self.config['common']:
                versions_data = self.config['common']['versions']
                if 'versions' in versions_data:
                    return versions_data['versions']
        except Exception as e:
            print(f"Warning: Không thể load versions từ config: {e}")
        
        # Fallback nếu không có config
        return ["fx799", "fx991", "fx570", "fx580", "fx115"]
    
    def _get_polynomial_config(self):
        """Lấy polynomial config từ config"""
        try:
            if self.config and 'polynomial' in self.config:
                return self.config['polynomial']
        except Exception as e:
            print(f"Warning: Không thể load polynomial config: {e}")
        
        return None

    # ========== UI SETUP ==========
    def _setup_ui(self):
        """Setup giao diện chính"""
        # Container chính với scrollbar
        main_container = tk.Frame(self.window, bg="#F0F8FF")
        main_container.pack(fill="both", expand=True, padx=15, pady=10)

        # === HEADER ===
        self._create_header(main_container)

        # === CONTROL PANEL ===
        self._create_control_panel(main_container)

        # === QUICK ACTIONS ===
        self._create_quick_actions(main_container)

        # === HƯỚNG DẪN ===
        self._create_guide_section(main_container)

        # === NHẬP HỆ SỐ ===
        self._create_input_section(main_container)

        # === KẾT QUẢ NGHIỆM ===
        self._create_roots_section(main_container)

        # === KẾT QUẢ TỔNG ===
        self._create_final_result_section(main_container)

        # === CONTROL BUTTONS ===
        self._create_control_buttons(main_container)

        # === STATUS BAR ===
        self._create_status_bar(main_container)

    def _create_header(self, parent):
        """Tạo header với title và icon"""
        header_frame = tk.Frame(parent, bg="#1E3A8A", height=80)
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)

        # Icon và Title
        title_frame = tk.Frame(header_frame, bg="#1E3A8A")
        title_frame.pack(expand=True, fill="both")

        icon_label = tk.Label(
            title_frame,
            text="📈",
            font=("Arial", 24),
            bg="#1E3A8A",
            fg="white"
        )
        icon_label.pack(side="left", padx=(20, 10), pady=20)

        title_label = tk.Label(
            title_frame,
            text="POLYNOMIAL EQUATION MODE v2.1",
            font=("Arial", 18, "bold"),
            bg="#1E3A8A",
            fg="white"
        )
        title_label.pack(side="left", pady=20)

        # Service status trong header
        service_status = "Service: ✅ Ready" if self.polynomial_service else "Service: ⚠️ Error"
        config_status = "Config: ✅ Loaded" if self.config else "Config: ⚠️ Fallback"
        subtitle_label = tk.Label(
            title_frame,
            text=f"Giải phương trình bậc cao với mã hóa • {service_status} • {config_status}",
            font=("Arial", 11),
            bg="#1E3A8A",
            fg="#B3D9FF"
        )
        subtitle_label.pack(side="right", padx=(0, 20), pady=(25, 15))

    def _create_control_panel(self, parent):
        """Tạo panel điều khiển chính"""
        control_frame = tk.LabelFrame(
            parent,
            text="⚙️ THIẾT LẬP PHƯƠNG TRÌNH",
            font=("Arial", 12, "bold"),
            bg="#FFFFFF",
            fg="#1E3A8A",
            bd=2,
            relief="groove"
        )
        control_frame.pack(fill="x", pady=10)

        # Dòng 1: Chọn bậc phương trình
        row1 = tk.Frame(control_frame, bg="#FFFFFF")
        row1.pack(fill="x", padx=20, pady=15)

        tk.Label(
            row1,
            text="Bậc phương trình:",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#333333",
            width=15
        ).pack(side="left")

        bac_menu = ttk.Combobox(
            row1,
            textvariable=self.bac_phuong_trinh_var,
            values=["2", "3", "4"],
            state="readonly",
            width=20,
            font=("Arial", 11)
        )
        bac_menu.pack(side="left", padx=10)
        bac_menu.bind("<<ComboboxSelected>>", self._on_bac_changed)

        # Thông tin về dạng phương trình
        self.equation_form_label = tk.Label(
            row1,
            text="ax² + bx + c = 0",
            font=("Arial", 11, "italic"),
            bg="#FFFFFF",
            fg="#666666"
        )
        self.equation_form_label.pack(side="left", padx=20)

        # Dòng 2: Chọn phiên bản máy tính
        row2 = tk.Frame(control_frame, bg="#FFFFFF")
        row2.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(
            row2,
            text="Phiên bản máy:",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#333333",
            width=15
        ).pack(side="left")

        phien_ban_menu = ttk.Combobox(
            row2,
            textvariable=self.phien_ban_var,
            values=self.phien_ban_list,
            state="readonly",
            width=20,
            font=("Arial", 11)
        )
        phien_ban_menu.pack(side="left", padx=10)
        phien_ban_menu.bind("<<ComboboxSelected>>", self._on_phien_ban_changed)
        
        # Thông tin config
        poly_config = self._get_polynomial_config()
        solver_method = poly_config.get('solver', {}).get('method', 'numpy') if poly_config else 'numpy'
        config_info = f"Solver: {solver_method}"
        
        tk.Label(
            row2,
            text=config_info,
            font=("Arial", 9),
            bg="#FFFFFF",
            fg="#666666"
        ).pack(side="right", padx=20)
    
    def _create_quick_actions(self, parent):
        """Tạo thanh hành động nhanh"""
        quick_frame = tk.Frame(parent, bg="#F0F8FF")
        quick_frame.pack(fill="x", pady=5)
        
        tk.Button(quick_frame, text="📝 Tạo Template", 
                 command=self._create_template,
                 bg="#1565C0", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Button(quick_frame, text="📁 Import Excel", 
                 command=self._import_excel,
                 bg="#FF9800", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)

    def _create_guide_section(self, parent):
        """Tạo section hướng dẫn"""
        guide_frame = tk.LabelFrame(
            parent,
            text="💡 HƯỚNG DẪN NHẬP LIỆU",
            font=("Arial", 10, "bold"),
            bg="#E8F4FD",
            fg="#1565C0",
            bd=1
        )
        guide_frame.pack(fill="x", pady=5)

        guide_text = (
            "• Nhập hệ số theo thứ tự từ cao đến thấp (a, b, c cho bậc 2)\n"
            "• Hỗ trợ biểu thức: sqrt(5), sin(pi/2), 1/2, 2^3, log(10)\n"
            "• Ô trống sẽ tự động điền số 0\n"
            "• Phương trình dạng: ax^n + bx^(n-1) + ... + k = 0"
        )

        guide_label = tk.Label(
            guide_frame,
            text=guide_text,
            font=("Arial", 9),
            bg="#E8F4FD",
            fg="#333333",
            justify="left"
        )
        guide_label.pack(padx=15, pady=10)

    def _create_input_section(self, parent):
        """Tạo section nhập hệ số"""
        self.input_frame = tk.LabelFrame(
            parent,
            text="📝 NHẬP HỆ SỐ PHƯƠNG TRÌNH",
            font=("Arial", 12, "bold"),
            bg="#FFFFFF",
            fg="#1E3A8A",
            bd=2,
            relief="groove"
        )
        self.input_frame.pack(fill="x", pady=10)

    def _create_roots_section(self, parent):
        """Tạo section kết quả nghiệm"""
        self.roots_frame = tk.LabelFrame(
            parent,
            text="🎯 NGHIỆM PHƯƠNG TRÌNH",
            font=("Arial", 12, "bold"),
            bg="#FFFFFF",
            fg="#D35400",
            bd=2,
            relief="groove"
        )
        self.roots_frame.pack(fill="x", pady=10)

        # Container cho text và scrollbar
        text_container = tk.Frame(self.roots_frame, bg="#FFFFFF")
        text_container.pack(fill="x", padx=15, pady=12)

        self.roots_text = tk.Text(
            text_container,
            width=80,
            height=8,
            font=("Courier New", 10),
            wrap=tk.WORD,
            bg="#FFF9E6",
            fg="#D35400"
        )
        self.roots_text.pack(side="left", fill="both", expand=True)

        # Scrollbar cho roots text
        scrollbar_roots = tk.Scrollbar(text_container, orient="vertical", command=self.roots_text.yview)
        scrollbar_roots.pack(side="right", fill="y")
        self.roots_text.config(yscrollcommand=scrollbar_roots.set)
        
        self.roots_text.insert("1.0", "Chưa có nghiệm được tính")

    def _create_final_result_section(self, parent):
        """Tạo section kết quả tổng"""
        self.final_frame = tk.LabelFrame(
            parent,
            text="📦 KẾT QUẢ TỔNG (CHO MÁY TÍNH)",
            font=("Arial", 12, "bold"),
            bg="#FFFFFF",
            fg="#2E7D32",
            bd=2,
            relief="groove"
        )
        self.final_frame.pack(fill="x", pady=10)

        self.final_result_text = tk.Text(
            self.final_frame,
            width=80,
            height=3,
            font=("Courier New", 9, "bold"),
            wrap=tk.WORD,
            bg="#F1F8E9",
            fg="#2E7D32"
        )
        self.final_result_text.pack(padx=15, pady=12, fill="x")
        
        # Hiển thị thông tin service status
        service_status = "Service Ready" if self.polynomial_service else "Service Failed"
        config_info = "Config loaded" if self.config else "Fallback config"
        self.final_result_text.insert("1.0", f"Polynomial Mode v2.1 - {service_status} | {config_info}")

    def _create_control_buttons(self, parent):
        """Tạo các nút điều khiển"""
        # Copy button (initially hidden)
        self.btn_copy_result = tk.Button(
            parent, text="📋 Copy Kết Quả", 
            command=self._copy_result,
            bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), width=20
        )
        self.btn_copy_result.pack(pady=5)
        self.btn_copy_result.pack_forget()  # Hide initially
        
        # Main button frame
        button_frame = tk.Frame(parent, bg="#F0F8FF")
        button_frame.pack(fill="x", pady=20)

        # Nút Xử lý
        self.btn_process = tk.Button(
            button_frame,
            text="🚀 Giải & Mã hóa",
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            height=2,
            command=self._process_polynomial
        )
        self.btn_process.pack(side="left", padx=10)

        # Nút Export
        self.btn_export = tk.Button(
            button_frame,
            text="💾 Export Excel",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            height=2,
            command=self._export_excel
        )
        self.btn_export.pack(side="left", padx=10)

        # Nút Reset
        self.btn_reset = tk.Button(
            button_frame,
            text="🔄 Reset",
            bg="#607D8B",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            height=2,
            command=self._reset_all
        )
        self.btn_reset.pack(side="left", padx=10)

        # Nút Đóng
        self.btn_close = tk.Button(
            button_frame,
            text="❌ Đóng",
            bg="#F44336",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            height=2,
            command=self.window.destroy
        )
        self.btn_close.pack(side="right", padx=10)

    def _create_status_bar(self, parent):
        """Tạo thanh trạng thái"""
        self.status_label = tk.Label(
            parent,
            text="🟢 Sẵn sàng nhập liệu phương trình bậc 2",
            font=("Arial", 10, "bold"),
            bg="#F0F8FF",
            fg="#2E7D32",
            relief="sunken",
            bd=1,
            anchor="w"
        )
        self.status_label.pack(fill="x", pady=(10, 0))

        # Footer
        footer_label = tk.Label(
            parent,
            text="Polynomial Mode v2.1 • Hỗ trợ giải phương trình bậc cao • Mã hóa tự động • Config-driven",
            font=("Arial", 8),
            bg="#F0F8FF",
            fg="#666666"
        )
        footer_label.pack(pady=5)

    # ========== EVENT HANDLERS ==========
    def _on_bac_changed(self, event=None):
        """Xử lý khi thay đổi bậc phương trình"""
        try:
            bac = int(self.bac_phuong_trinh_var.get())

            # Cập nhật dạng phương trình
            forms = {
                2: "ax² + bx + c = 0",
                3: "ax³ + bx² + cx + d = 0",
                4: "ax⁴ + bx³ + cx² + dx + e = 0"
            }
            self.equation_form_label.config(text=forms[bac])

            # Cập nhật service
            if self.polynomial_service:
                self.polynomial_service.set_degree(bac)

            # Cập nhật input fields
            self._update_input_fields()
            
            # Reset state
            self.has_result = False
            self._hide_copy_button()

            # Cập nhật status
            self.status_label.config(text=f"Đã chọn phương trình bậc {bac}", fg="#2E7D32")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đổi bậc phương trình: {e}")

    def _on_phien_ban_changed(self, event=None):
        """Xử lý khi thay đổi phiên bản"""
        try:
            phien_ban = self.phien_ban_var.get()
            
            # Cập nhật service
            if self.polynomial_service:
                self.polynomial_service.set_version(phien_ban)
            
            # Lấy thêm thông tin từ config nếu có
            poly_config = self._get_polynomial_config()
            precision = poly_config.get('solver', {}).get('precision', 6) if poly_config else 6
            
            self.status_label.config(text=f"Đã chọn phiên bản: {phien_ban} (precision: {precision})")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đổi phiên bản: {e}")

    # ========== INPUT MANAGEMENT ==========
    def _setup_input_bindings(self):
        """Setup bindings for input change detection"""
        for entry in self.coefficient_entries:
            if hasattr(entry, 'bind'):
                entry.bind('<KeyRelease>', self._on_manual_input)

    def _on_manual_input(self, event=None):
        """Xử lý khi nhập liệu thủ công"""
        if self.is_imported_mode:
            messagebox.showerror("Lỗi", "Đã ở chế độ import, không thể nhập thủ công!")
            if event and hasattr(event, 'widget'):
                event.widget.delete(0, tk.END)
            return

        has_data = self._check_manual_data()
        
        if has_data and not self.manual_data_entered:
            self.manual_data_entered = True
            self.status_label.config(text="✏️ Đang nhập liệu thủ công...", fg="#FF9800")
        elif not has_data and self.manual_data_entered:
            self.manual_data_entered = False
            bac = self.bac_phuong_trinh_var.get()
            self.status_label.config(text=f"🟢 Sẵn sàng nhập liệu phương trình bậc {bac}", fg="#2E7D32")

    def _check_manual_data(self):
        """Kiểm tra xem đã nhập dữ liệu thủ công chưa"""
        for entry in self.coefficient_entries:
            try:
                if entry.get().strip():
                    return True
            except Exception:
                pass
        return False

    def _update_input_fields(self):
        """Cập nhật các ô nhập liệu theo bậc phương trình"""
        try:
            bac = int(self.bac_phuong_trinh_var.get())

            # Xóa widgets cũ
            for widget in self.input_frame.winfo_children():
                widget.destroy()

            self.coefficient_entries = []

            # Tạo input fields mới
            self._create_coefficient_inputs(bac)
            
            # Reset bindings
            self.window.after(100, self._setup_input_bindings)

        except Exception as e:
            print(f"Lỗi khi cập nhật input fields: {e}")

    def _create_coefficient_inputs(self, bac):
        """Tạo các ô nhập hệ số"""
        # Header
        tk.Label(
            self.input_frame,
            text=f"Nhập {bac + 1} hệ số cho phương trình bậc {bac}:",
            font=("Arial", 10, "bold"),
            bg="#FFFFFF",
            fg="#333333"
        ).pack(anchor="w", padx=20, pady=10)

        # Container cho inputs
        input_container = tk.Frame(self.input_frame, bg="#FFFFFF")
        input_container.pack(fill="x", padx=20, pady=10)

        # Labels và entries theo bậc
        labels = self._get_coefficient_labels(bac)

        for i, (label, var_name) in enumerate(labels):
            row_frame = tk.Frame(input_container, bg="#FFFFFF")
            row_frame.pack(fill="x", pady=5)

            # Label hệ số
            coef_label = tk.Label(
                row_frame,
                text=label,
                font=("Arial", 10, "bold"),
                bg="#FFFFFF",
                fg="#1E3A8A",
                width=20,
                anchor="w"
            )
            coef_label.pack(side="left")

            # Entry
            entry = tk.Entry(
                row_frame,
                width=30,
                font=("Arial", 10),
                relief="groove",
                bd=2
            )
            entry.pack(side="left", padx=10)
            entry.bind('<KeyRelease>', self._on_manual_input)

            # Placeholder text
            placeholder = tk.Label(
                row_frame,
                text=f"(hệ số {var_name})",
                font=("Arial", 9, "italic"),
                bg="#FFFFFF",
                fg="#666666"
            )
            placeholder.pack(side="left", padx=10)

            self.coefficient_entries.append(entry)

    def _get_coefficient_labels(self, bac):
        """Lấy labels cho hệ số theo bậc"""
        labels_config = {
            2: [("Hệ số a (x²):", "a"), ("Hệ số b (x):", "b"), ("Hệ số c (hằng số):", "c")],
            3: [("Hệ số a (x³):", "a"), ("Hệ số b (x²):", "b"), ("Hệ số c (x):", "c"), ("Hệ số d (hằng số):", "d")],
            4: [("Hệ số a (x⁴):", "a"), ("Hệ số b (x³):", "b"), ("Hệ số c (x²):", "c"), ("Hệ số d (x):", "d"),
                ("Hệ số e (hằng số):", "e")]
        }
        return labels_config.get(bac, labels_config[2])

    # ========== BUTTON VISIBILITY ==========
    def _update_button_visibility(self):
        """Cập nhật hiển thị nút"""
        # Logic hiển thị nút theo trạng thái
        pass
    
    def _show_copy_button(self):
        """Hiển thị nút copy khi có kết quả"""
        self.btn_copy_result.pack(pady=5, before=self.btn_process.master)
    
    def _hide_copy_button(self):
        """Giấu nút copy"""
        self.btn_copy_result.pack_forget()

    # ========== PROCESSING METHODS ==========
    def _process_polynomial(self):
        """Xử lý giải phương trình polynomial"""
        try:
            if not self.polynomial_service:
                messagebox.showerror("Lỗi", "PolynomialService chưa được khởi tạo!")
                return

            # Lấy dữ liệu đầu vào
            coefficient_inputs = [entry.get().strip() for entry in self.coefficient_entries]
            
            # Kiểm tra input
            is_valid, validation_msg = self.polynomial_service.validate_input(coefficient_inputs)
            if not is_valid:
                messagebox.showwarning("Dữ liệu không hợp lệ", validation_msg)
                return

            # Cập nhật status
            self.status_label.config(text="🔄 Đang giải phương trình...", fg="#FF9800")
            self.window.update()

            # Xử lý
            success, status_msg, roots_display, final_keylog = self.polynomial_service.process_complete_workflow(coefficient_inputs)

            if success:
                # Hiển thị nghiệm
                self.roots_text.config(state='normal')
                self.roots_text.delete("1.0", tk.END)
                self.roots_text.insert("1.0", roots_display)
                self.roots_text.config(bg="#E8F5E8", fg="#2E7D32", state='disabled')

                # Hiển thị kết quả cuối
                self._show_final_result(final_keylog)

                # Cập nhật state
                self.has_result = True
                self._show_copy_button()
                self.status_label.config(text="✅ Giải phương trình thành công!", fg="#2E7D32")

            else:
                messagebox.showerror("Lỗi Xử lý", status_msg)
                self.status_label.config(text=f"❌ {status_msg}", fg="#F44336")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý polynomial: {str(e)}")
            self.status_label.config(text="❌ Lỗi xử lý", fg="#F44336")
    
    def _show_final_result(self, keylog: str):
        """Hiển thị kết quả cuối với font đặc biệt"""
        self.final_result_text.config(state='normal')
        self.final_result_text.delete("1.0", tk.END)
        self.final_result_text.insert("1.0", keylog)
        
        # Try special font for calculator display
        try:
            self.final_result_text.config(font=("Flexio Fx799VN", 11, "bold"), fg="#000000", bg="#E8F5E8")
        except Exception:
            self.final_result_text.config(font=("Courier New", 11, "bold"), fg="#000000", bg="#E8F5E8")
        
        self.final_result_text.config(state='disabled')

    def _copy_result(self):
        """Copy kết quả vào clipboard"""
        try:
            if not self.has_result:
                messagebox.showwarning("Cảnh báo", "Chưa có kết quả để copy!")
                return
            
            result_text = self.final_result_text.get("1.0", tk.END).strip()
            if result_text:
                self.window.clipboard_clear()
                self.window.clipboard_append(result_text)
                messagebox.showinfo("Đã copy", f"Đã copy kết quả Polynomial vào clipboard:\n\n{result_text}")
            else:
                messagebox.showwarning("Cảnh báo", "Không có kết quả để copy!")
                
        except Exception as e:
            messagebox.showerror("Lỗi Copy", f"Lỗi copy kết quả: {str(e)}")

    # ========== EXCEL METHODS ==========
    def _create_template(self):
        """Tạo Excel template cho polynomial"""
        try:
            degree = int(self.bac_phuong_trinh_var.get())
            
            default_name = f"polynomial_template_degree_{degree}.xlsx"
            path = filedialog.asksaveasfilename(
                defaultextension=".xlsx", 
                filetypes=[("Excel files", "*.xlsx")], 
                initialfile=default_name,
                title=f"Tạo Template cho Phương trình Bậc {degree}"
            )
            if not path:
                return
                
            success = PolynomialTemplateGenerator.create_template(degree, path)
            
            if success:
                messagebox.showinfo(
                    "Thành công", 
                    f"Đã tạo template bậc {degree}:\n{path}\n\n"
                    f"Template gồm 3 sheet:\n"
                    f"• Input: Nhập dữ liệu\n"
                    f"• Examples: Ví dụ mẫu\n"
                    f"• Instructions: Hướng dẫn sử dụng"
                )
            else:
                messagebox.showerror("Lỗi", f"Không thể tạo template: Unknown error")
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo template: {e}")

    def _import_excel(self):
        """Import file Excel"""
        messagebox.showinfo("Import Excel", "Chức năng Import Excel cho Polynomial Mode sẽ được bổ sung trong phiên bản tiếp theo.\n\nHiện tại vui lòng sử dụng 'Tạo Template' để tạo file Excel mẫu.")
    
    def _export_excel(self):
        """Export kết quả ra Excel"""
        try:
            if not self.has_result or not self.polynomial_service:
                messagebox.showwarning("Cảnh báo", "Chưa có kết quả để xuất!\n\nVui lòng giải phương trình trước.")
                return
            
            default_name = f"polynomial_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            output_path = filedialog.asksaveasfilename(
                title="Xuất kết quả Polynomial ra Excel", 
                defaultextension=".xlsx", 
                filetypes=[("Excel files", "*.xlsx")], 
                initialfile=default_name
            )
            
            if not output_path:
                return
            
            # Chuẩn bị dữ liệu xuất
            import pandas as pd
            
            input_data = [entry.get() for entry in self.coefficient_entries]
            roots_text = self.roots_text.get("1.0", tk.END).strip()
            final_result = self.final_result_text.get("1.0", tk.END).strip()
            polynomial_info = self.polynomial_service.get_polynomial_info()
            
            export_data = {
                'Polynomial_Degree': [self.bac_phuong_trinh_var.get()],
                'Calculator_Version': [self.phien_ban_var.get()],
                'Polynomial_Form': [self.polynomial_service.get_polynomial_form_display()],
                'Input_Coefficients': [' | '.join(input_data)],
                'Encoded_Coefficients': [' | '.join(self.polynomial_service.get_last_encoded_coefficients())],
                'Roots_Solution': [roots_text.replace('\n', ' | ')],
                'Final_Keylog': [final_result],
                'Solver_Method': [polynomial_info.get('solver_method', 'unknown')],
                'Real_Roots_Count': [len(self.polynomial_service.get_real_roots_only())],
                'Export_Time': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            }
            
            pd.DataFrame(export_data).to_excel(output_path, index=False, sheet_name='Polynomial_Results')
            messagebox.showinfo("Xuất thành công", f"Kết quả Polynomial Mode đã xuất tại:\n{output_path}")
            
        except Exception as e:
            messagebox.showerror("Lỗi Xuất", f"Lỗi xuất Excel: {str(e)}")

    def _reset_all(self):
        """Reset tất cả dữ liệu"""
        try:
            # Clear all entries
            for entry in self.coefficient_entries:
                entry.delete(0, tk.END)

            # Clear text areas
            self.roots_text.config(state='normal')
            self.roots_text.delete("1.0", tk.END)
            self.roots_text.insert("1.0", "Chưa có nghiệm được tính")
            self.roots_text.config(bg="#FFF9E6", fg="#D35400", state='disabled')

            self.final_result_text.config(state='normal')
            self.final_result_text.delete("1.0", tk.END)
            service_status = "Service Ready" if self.polynomial_service else "Service Failed"
            config_info = "Config loaded" if self.config else "Fallback config"
            self.final_result_text.insert("1.0", f"Polynomial Mode v2.1 - {service_status} | {config_info}")
            self.final_result_text.config(bg="#F1F8E9", font=("Courier New", 9), state='disabled')
            
            # Reset state
            self.manual_data_entered = False
            self.has_result = False
            self.is_imported_mode = False
            
            # Hide copy button
            self._hide_copy_button()
            
            # Reset service state
            if self.polynomial_service:
                self.polynomial_service.reset_state()

            # Reset status
            bac = self.bac_phuong_trinh_var.get()
            self.status_label.config(text=f"🔄 Đã reset - Sẵn sàng nhập phương trình bậc {bac}", fg="#2E7D32")
            
        except Exception as e:
            messagebox.showerror("Lỗi Reset", f"Lỗi khi reset: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PolynomialEquationView(root)
    root.mainloop()
