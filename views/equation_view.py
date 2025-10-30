import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import psutil
import threading

from services.equation.equation_template_generator import EquationTemplateGenerator
from services.equation.equation_batch_processor import EquationBatchProcessor
from services.equation.equation_service import EquationService

class EquationView:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Equation Mode v2.2 - Enhanced Solution Analysis")
        self.window.geometry("900x1000")
        self.window.configure(bg="#F8F9FA")

        # Config và state management
        self.config = config or {}
        self.manual_data_entered = False
        self.has_result = False
        self.imported_data = False
        self.imported_file_path = ""
        self.imported_file_name = ""
        self.imported_file_size_mb = 0.0
        self.processing_cancelled = False
        self.show_detailed_analysis = False  # Toggle giữa basic/detailed

        # Variables
        self.so_an_var = tk.StringVar(value="2")
        self.phien_ban_var = tk.StringVar()
        self.input_entries = []
        self.result_entries = []

        # Load configuration
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var.set(self.phien_ban_list[0] if self.phien_ban_list else "fx799")
        
        # Initialize services
        self.equation_service = None
        self.batch_processor = EquationBatchProcessor()
        self._initialize_service()

        # Setup UI
        self._setup_ui()
        self._update_input_fields()
        self._update_button_visibility()
        
        # Bind input detection
        self.window.after(1000, self._setup_input_bindings)

    def _initialize_service(self):
        """Khởi tạo EquationService"""
        try:
            self.equation_service = EquationService(self.config)
            self.equation_service.set_variables_count(int(self.so_an_var.get()))
            self.equation_service.set_version(self.phien_ban_var.get())
        except Exception as e:
            print(f"Warning: Không thể khởi tạo EquationService: {e}")
            self.equation_service = None

    def _get_available_versions(self):
        """Load available versions from config"""
        try:
            if self.config and 'common' in self.config and 'versions' in self.config['common']:
                versions_data = self.config['common']['versions']
                if 'versions' in versions_data:
                    return versions_data['versions']
        except Exception as e:
            print(f"Warning: Không thể load versions từ config: {e}")
        return ["fx799", "fx800", "fx801", "fx802", "fx803"]

    # ========== UI SETUP ==========
    def _setup_ui(self):
        """Setup main UI"""
        self._create_header()
        self.main_container = tk.Frame(self.window, bg="#F8F9FA")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=5)
        self._setup_control_frame()
        self._setup_guide_frame()
        self._setup_input_output_frames()
        self._setup_control_buttons()

    def _create_header(self):
        HEADER_COLORS = {"primary": "#1565C0", "secondary": "#0D47A1", "text": "#FFFFFF","accent": "#FF9800"}
        self.header_frame = tk.Frame(self.window, bg=HEADER_COLORS["primary"], height=90)
        self.header_frame.pack(fill="x", padx=10, pady=5)
        self.header_frame.pack_propagate(False)
        header_content = tk.Frame(self.header_frame, bg=HEADER_COLORS["primary"])
        header_content.pack(fill="both", expand=True, padx=15, pady=10)
        left_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        left_section.pack(side="left", fill="y")
        tk.Label(left_section, text="🧠", font=("Arial", 20), bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        tk.Label(left_section, text="Equation v2.2 - Enhanced Analysis", font=("Arial", 16, "bold"), bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left", padx=(5, 20))
        controls_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        controls_frame.pack(side="top", fill="x", pady=(5, 0))
        tk.Label(controls_frame, text="Số ẩn:", font=("Arial", 10), bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        variables_menu = tk.OptionMenu(controls_frame, self.so_an_var, "2", "3", "4")
        variables_menu.config(bg=HEADER_COLORS["secondary"], fg=HEADER_COLORS["text"], font=("Arial", 10, "bold"), width=8, relief="flat", borderwidth=0)
        variables_menu.pack(side="left", padx=(5, 10))
        tk.Label(controls_frame, text="Phiên bản:", font=("Arial", 10), bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        version_menu = tk.OptionMenu(controls_frame, self.phien_ban_var, *self._get_available_versions())
        version_menu.config(bg=HEADER_COLORS["accent"], fg="white", font=("Arial", 10), width=12, relief="flat", borderwidth=0)
        version_menu.pack(side="left", padx=(5, 0))
        self.so_an_var.trace('w', self._on_so_an_changed)
        self.phien_ban_var.trace('w', self._on_phien_ban_changed)

    def _setup_control_frame(self):
        excel_frame = tk.Frame(self.main_container, bg="#F8F9FA")
        excel_frame.grid(row=0, column=0, columnspan=4, pady=5, sticky="we")
        tk.Button(excel_frame, text="📝 Tạo Template", command=self._on_create_template, bg="#1565C0", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Button(excel_frame, text="📁 Import Excel", command=self._on_import_excel, bg="#FF9800", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        # Nút toggle detailed analysis
        self.btn_toggle_detail = tk.Button(excel_frame, text="🔍 Chi tiết", command=self._toggle_detailed_analysis, bg="#9C27B0", fg="white", font=("Arial", 9, "bold"))
        self.btn_toggle_detail.pack(side="right", padx=2)

    def _setup_guide_frame(self):
        guide_frame = tk.LabelFrame(self.main_container, text="💡 HƯỚNG DẪN NHẬP LIỆU", font=("Arial", 10, "bold"), bg="#E3F2FD", fg="#1565C0", bd=1, relief="solid")
        guide_frame.grid(row=1, column=0, columnspan=4, pady=5, padx=10, sticky="we")
        guide_text = ("• Hỗ trợ: sqrt(5), sin(pi/2), 2^3, log(10)\n" "• Nhập hệ số cách nhau bằng dấu phẩy\n" "• Ô trống sẽ tự động điền số 0 | Nhấn '🔍 Chi tiết' để xem rank analysis")
        tk.Label(guide_frame, text=guide_text, font=("Arial", 9), bg="#E3F2FD", fg="#333333", justify="left", anchor="w").pack(padx=10, pady=8, fill="x")

    def _setup_input_output_frames(self):
        self.input_frame = tk.LabelFrame(self.main_container, text="📝 NHẬP HỆ SỐ PHƯƠNG TRÌNH", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#1B5299", bd=2, relief="groove")
        self.input_frame.grid(row=2, column=0, columnspan=4, pady=5, padx=10, sticky="we")
        self.result_frame = tk.LabelFrame(self.main_container, text="🔐 KẾT QUẢ MÃ HÓA", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#7B1FA2", bd=2, relief="groove")
        self.result_frame.grid(row=3, column=0, columnspan=4, pady=5, padx=10, sticky="we")
        self.frame_nghiem = tk.LabelFrame(self.main_container, text="🎯 KẾT QUẢ NGHIỆM", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#D35400", bd=2, relief="groove")
        self.frame_nghiem.grid(row=4, column=0, columnspan=4, pady=5, padx=10, sticky="we")
        self.entry_nghiem = tk.Entry(self.frame_nghiem, width=80, font=("Arial", 10), justify="left")
        self.entry_nghiem.pack(padx=15, pady=12, fill="x")
        self.entry_nghiem.insert(0, "Chưa có kết quả nghiệm")
        self.entry_nghiem.config(bg="#FFF9E6", fg="#FF6F00")
        self.frame_tong = tk.LabelFrame(self.main_container, text="📦 KẾT QUẢ TỔNG (CHO MÁY TÍNH)", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#2E7D32", bd=2, relief="groove")
        self.frame_tong.grid(row=5, column=0, columnspan=4, pady=5, padx=10, sticky="we")
        self.entry_tong = tk.Text(self.frame_tong, width=80, height=2, font=("Courier New", 9, "bold"), wrap=tk.NONE)
        self.entry_tong.pack(padx=15, pady=12, fill="x")
        service_status = "Service Ready" if self.equation_service else "Service Failed"
        config_info = "Config loaded" if self.config else "Fallback config"
        self.entry_tong.insert(tk.END, f"Equation Mode v2.2 - {service_status} | {config_info}")
        self.entry_tong.config(bg="#F1F8E9")

    def _setup_control_buttons(self):
        self.btn_copy_result = tk.Button(self.main_container, text="📋 Copy Kết Quả", command=self._copy_result, bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), width=20)
        self.btn_copy_result.grid(row=6, column=0, sticky="w", padx=10, pady=5)
        self.btn_copy_result.grid_remove()
        self.frame_buttons_manual = tk.Frame(self.main_container, bg="#F8F9FA")
        self.frame_buttons_manual.grid(row=7, column=0, columnspan=4, pady=10, sticky="we")
        tk.Button(self.frame_buttons_manual, text="🚀 Xử lý & Mã hóa", command=self._process_equations, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_manual, text="💾 Xuất Excel", command=self._export_excel, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.frame_buttons_import = tk.Frame(self.main_container, bg="#F8F9FA")
        self.frame_buttons_import.grid(row=7, column=0, columnspan=4, pady=10, sticky="we")
        tk.Button(self.frame_buttons_import, text="📁 Import File Khác", command=self._on_import_excel, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_import, text="🔥 Xử lý File Excel", command=self._on_process_excel, bg="#F44336", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_import, text="↩️ Quay lại", command=self._quit_import_mode, bg="#607D8B", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.frame_buttons_import.grid_remove()
        self.frame_buttons_manual.grid_remove()
        self.status_label = tk.Label(self.main_container, text="🟢 Sẵn sàng nhập liệu và mã hóa keylog", font=("Arial", 10, "bold"), bg="#F8F9FA", fg="#2E7D32", anchor="w", justify="left")
        self.status_label.grid(row=8, column=0, columnspan=4, pady=10, sticky="we")

    # ========== BUTTON VISIBILITY MANAGEMENT ==========
    def _update_button_visibility(self):
        try:
            if self.imported_data:
                self._show_import_buttons()
            elif self.manual_data_entered:
                self._show_manual_buttons()
            else:
                self._hide_action_buttons()
        except Exception:
            try:
                self.frame_buttons_manual.grid_remove()
                self.frame_buttons_import.grid_remove()
            except Exception:
                pass

    def _show_manual_buttons(self):
        self.frame_buttons_manual.grid()
        self.frame_buttons_import.grid_remove()

    def _show_import_buttons(self):
        self.frame_buttons_import.grid()
        self.frame_buttons_manual.grid_remove()

    def _hide_action_buttons(self):
        self.frame_buttons_manual.grid_remove()
        self.frame_buttons_import.grid_remove()

    def _show_copy_button(self):
        self.btn_copy_result.grid()

    def _hide_copy_button(self):
        self.btn_copy_result.grid_remove()

    def _toggle_detailed_analysis(self):
        """Toggle giữa basic và detailed solution analysis"""
        self.show_detailed_analysis = not self.show_detailed_analysis
        btn_text = "🔍 Bỏ chi tiết" if self.show_detailed_analysis else "🔍 Chi tiết"
        self.btn_toggle_detail.config(text=btn_text)
        
        # Cập nhật hiển thị nghiệm hiện tại nếu có
        if self.has_result and self.equation_service:
            self._refresh_solution_display()

    # ========== INPUT FIELD MANAGEMENT ==========
    def _setup_input_bindings(self):
        for entry in self.input_entries:
            if hasattr(entry, 'bind'):
                entry.bind('<KeyRelease>', self._on_manual_input)

    def _on_manual_input(self, event=None):
        if self.imported_data:
            messagebox.showerror("Lỗi", "Đã import Excel, không thể nhập dữ liệu thủ công!")
            if event and getattr(event, 'widget', None):
                try:
                    event.widget.delete(0, tk.END)
                except Exception:
                    pass
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
        for entry in self.input_entries:
            try:
                if entry.get().strip():
                    return True
            except Exception:
                pass
        return False

    def _update_input_fields(self):
        try:
            so_an = int(self.so_an_var.get())
            for widget in self.input_frame.winfo_children():
                widget.destroy()
            for widget in self.result_frame.winfo_children():
                widget.destroy()
            self.input_entries = []
            self.result_entries = []
            tk.Label(self.input_frame, text=f"Nhập {so_an + 1} hệ số cho mỗi phương trình (cách nhau bằng dấu phẩy):", font=("Arial", 9, "bold"), bg="#FFFFFF", fg="#333333").pack(anchor="w", padx=15, pady=8)
            labels = self._get_input_labels(so_an)
            for i, label_text in enumerate(labels):
                row_frame = tk.Frame(self.input_frame, bg="#FFFFFF")
                row_frame.pack(fill="x", padx=15, pady=6)
                tk.Label(row_frame, text=label_text, font=("Arial", 9), bg="#FFFFFF", fg="#333333", width=50).pack(side="left")
                entry = tk.Entry(row_frame, width=45, font=("Arial", 9))
                entry.pack(side="left", padx=5, fill="x", expand=True)
                entry.bind('<KeyRelease>', self._on_manual_input)
                self.input_entries.append(entry)
            tk.Label(self.result_frame, text=f"Kết quả mã hóa ({self._get_result_count(so_an)} hệ số):", font=("Arial", 9, "bold"), bg="#FFFFFF", fg="#333333").pack(anchor="w", padx=15, pady=8)
            if so_an == 2:
                labels_2an = ["a11", "a12", "c1", "a21", "a22", "c2"]
                self._create_result_grid(labels_2an, 2, 3)
            elif so_an == 3:
                labels_3an = ["a11", "a12", "a13", "c1", "a21", "a22", "a23", "c2", "a31", "a32", "a33", "c3"]
                self._create_result_grid(labels_3an, 3, 4)
            elif so_an == 4:
                labels_4an = ["a11", "a12", "a13", "a14", "c1", "a21", "a22", "a23", "a24", "c2", "a31", "a32", "a33", "a34", "c3", "a41", "a42", "a43", "a44", "c4"]
                self._create_result_grid(labels_4an, 4, 5)
            self.window.after(100, self._setup_input_bindings)
        except Exception as e:
            print(f"Lỗi khi cập nhật ô nhập liệu: {e}")

    def _create_result_grid(self, labels, rows, cols):
        for row in range(rows):
            row_frame = tk.Frame(self.result_frame, bg="#FFFFFF")
            row_frame.pack(fill="x", padx=15, pady=4)
            tk.Label(row_frame, text=f"PT {row + 1}:", font=("Arial", 8, "bold"), bg="#FFFFFF", fg="#333333", width=6).pack(side="left", padx=2)
            for col in range(cols):
                idx = row * cols + col
                if idx < len(labels):
                    label_frame = tk.Frame(row_frame, bg="#FFFFFF")
                    label_frame.pack(side="left", padx=2)
                    tk.Label(label_frame, text=labels[idx] + ":", font=("Arial", 8, "bold"), bg="#FFFFFF", fg="#7B1FA2", width=4).pack(side="top")
                    entry = tk.Entry(label_frame, width=12, font=("Arial", 8), state='readonly', bg="#F3E5F5")
                    entry.pack(side="top", padx=2)
                    self.result_entries.append(entry)

    def _get_input_labels(self, so_an):
        config = {
            2: ["Phương trình 1 (a₁₁, a₁₂, c₁):", "Phương trình 2 (a₂₁, a₂₂, c₂):"],
            3: ["Phương trình 1 (a₁₁, a₁₂, a₁₃, c₁):", "Phương trình 2 (a₂₁, a₂₂, a₂₃, c₂):", "Phương trình 3 (a₃₁, a₃₂, a₃₃, c₃):"],
            4: ["Phương trình 1 (a₁₁, a₁₂, a₁₃, a₁₄, c₁):", "Phương trình 2 (a₂₁, a₂₂, a₂₃, a₂₄, c₂):", "Phương trình 3 (a₃₁, a₃₂, a₃₃, a₃₄, c₃):", "Phương trình 4 (a₄₁, a₄₂, a₄₃, a₄₄, c₄):"]
        }
        return config.get(so_an, config[2])

    def _get_result_count(self, so_an):
        return {2: 6, 3: 12, 4: 20}.get(so_an, 6)

    # ========== EVENT HANDLERS ==========
    def _on_so_an_changed(self, *args):
        try:
            self._update_input_fields()
            if self.equation_service:
                self.equation_service.set_variables_count(int(self.so_an_var.get()))
            self.has_result = False
            self._hide_copy_button()
            self._update_button_visibility()
            so_an = self.so_an_var.get()
            expected_coeffs = int(so_an) * (int(so_an) + 1)
            self.status_label.config(text=f"Đã chọn hệ {so_an}×{so_an} (cần {expected_coeffs} hệ số)", anchor='w', justify='left')
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đổi số ẩn: {e}")

    def _on_phien_ban_changed(self, *args):
        try:
            selected_version = self.phien_ban_var.get()
            if self.equation_service:
                self.equation_service.set_version(selected_version)
            self.status_label.config(text=f"Đã chọn phiên bản: {selected_version}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đổi phiên bản: {e}")

    # ========== PROCESSING ==========
    def _process_equations(self):
        try:
            if not self.equation_service:
                messagebox.showerror("Lỗi", "EquationService chưa được khởi tạo!")
                return
            equation_inputs = [entry.get().strip() for entry in self.input_entries]
            is_valid, validation_msg = self.equation_service.validate_input(equation_inputs)
            if not is_valid:
                messagebox.showwarning("Dữ liệu không hợp lệ", validation_msg)
                return
            self.status_label.config(text="🔄 Đang mã hóa keylog...", fg="#FF9800", anchor="w", justify="left")
            self.window.update()
            
            # Xử lý với detailed analysis nếu đã bật
            if self.show_detailed_analysis:
                success, status_msg, solutions_text, enhanced_solutions, final_result = self.equation_service.process_complete_workflow_detailed(equation_inputs)
                display_solution = enhanced_solutions
            else:
                success, status_msg, solutions_text, final_result = self.equation_service.process_complete_workflow(equation_inputs)
                display_solution = solutions_text
            
            # Hiển thị nghiệm
            self.entry_nghiem.config(state='normal', justify='left')
            self.entry_nghiem.delete(0, tk.END)
            self.entry_nghiem.insert(0, display_solution or "Chưa có kết quả")
            
            # Color coding dựa trên loại nghiệm
            if "vô nghiệm" in display_solution.lower() and "vô số" not in display_solution.lower():
                # Vô nghiệm
                self.entry_nghiem.config(bg="#FFEBEE", fg="#C62828")
            elif "vô số nghiệm" in display_solution.lower():
                # Vô số nghiệm
                self.entry_nghiem.config(bg="#FFF3E0", fg="#F57C00")
            elif "=" in display_solution and any(var in display_solution for var in ['x', 'y', 'z', 't']):
                # Có nghiệm
                self.entry_nghiem.config(bg="#E8F5E8", fg="#2E7D32")
            else:
                # Default hoặc unknown
                self.entry_nghiem.config(bg="#FFF9E6", fg="#FF6F00")
            
            self.entry_nghiem.config(state='readonly', justify='left')
            
            # Hiển thị final keylog
            self._show_single_line_result(final_result)
            # Hiển thị encoded coefficients nếu có
            encoded_coeffs = self.equation_service.get_encoded_coefficients_display()
            self._display_encoded_coefficients(encoded_coeffs)
            # Update state
            self.has_result = bool(final_result and final_result.strip())
            if self.has_result:
                self._show_copy_button()
                self.status_label.config(text="✅ Đã sinh Keylog (phân tích rank hoàn tất)", fg="#2E7D32", anchor="w", justify="left")
            else:
                self.status_label.config(text=f"❌ {status_msg}", fg="#F44336", anchor="w", justify="left")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý phương trình: {str(e)}")
            self.status_label.config(text="❌ Lỗi xử lý", fg="#F44336", anchor="w", justify="left")

    def _refresh_solution_display(self):
        """Cập nhật lại hiển thị nghiệm theo mode hiện tại (basic/detailed)"""
        try:
            if self.show_detailed_analysis:
                display_text = self.equation_service.get_enhanced_solutions_text()
            else:
                display_text = self.equation_service.get_solutions_text()
            
            self.entry_nghiem.config(state='normal')
            self.entry_nghiem.delete(0, tk.END)
            self.entry_nghiem.insert(0, display_text)
            
            # Color coding
            if "vô nghiệm" in display_text.lower() and "vô số" not in display_text.lower():
                self.entry_nghiem.config(bg="#FFEBEE", fg="#C62828")
            elif "vô số nghiệm" in display_text.lower():
                self.entry_nghiem.config(bg="#FFF3E0", fg="#F57C00")
            elif "=" in display_text and any(var in display_text for var in ['x', 'y', 'z', 't']):
                self.entry_nghiem.config(bg="#E8F5E8", fg="#2E7D32")
            else:
                self.entry_nghiem.config(bg="#FFF9E6", fg="#FF6F00")
                
            self.entry_nghiem.config(state='readonly')
        except Exception as e:
            print(f"Lỗi refresh solution display: {e}")

    def _show_single_line_result(self, result_text: str):
        self.entry_tong.config(state='normal')
        self.entry_tong.delete(1.0, tk.END)
        one_line = (result_text or "").strip().splitlines()[0] if result_text else ""
        self.entry_tong.insert(tk.END, one_line)
        try:
            self.entry_tong.config(font=("Flexio Fx799VN", 11, "bold"), fg="#000000", bg="#E8F5E8")
        except Exception:
            self.entry_tong.config(font=("Courier New", 11, "bold"), fg="#000000", bg="#E8F5E8")
        self.entry_tong.config(state='disabled')

    def _display_encoded_coefficients(self, encoded_coeffs):
        for i, entry in enumerate(self.result_entries):
            if i < len(encoded_coeffs):
                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, encoded_coeffs[i])
                entry.config(state='readonly', bg="#E8F5E8")

    # ========== EXCEL METHODS ==========
    def _on_create_template(self):
        try:
            n = int(self.so_an_var.get())
            path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")], initialfile=f"equation_template_{n}x{n}.xlsx")
            if not path:
                return
            EquationTemplateGenerator.create_template(n, path)
            messagebox.showinfo("Thành công", f"Đã tạo template:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo template: {e}")

    def _on_import_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel","*.xlsx *.xls")])
        if not path:
            return
        try:
            size_mb = os.path.getsize(path) / (1024 * 1024)
        except Exception:
            size_mb = 0.0
        if size_mb > 100:
            proceed = messagebox.askyesno("⚠️ File Excel lớn", f"File này {size_mb:.1f}MB.\n\n• RAM có thể tăng >1GB\n• Xử lý có thể mất vài phút\n• Ứng dụng có thể đơ tạm thời\n\nBạn có muốn tiếp tục?")
            if not proceed:
                return
        self.imported_file_path = path
        self.imported_file_name = os.path.basename(path)
        self.imported_file_size_mb = size_mb
        self.is_imported_mode = True
        self.imported_data = True
        self.has_manual_data = False
        self._update_button_visibility()
        size_info = f" ({size_mb:.1f}MB)" if size_mb else ""
        messagebox.showinfo("Import", f"Đã chọn file:\n{self.imported_file_name}{size_info}\nSẵn sàng xử lý.")
        if hasattr(self, 'excel_status_label'):
            self.excel_status_label.config(text=f"Excel: 📁 {self.imported_file_name[:15]}...")

    def _on_process_excel(self):
        if not self.imported_file_path:
            messagebox.showwarning("Thiếu file", "Hãy import file Excel trước.")
            return
        try:
            n = int(self.so_an_var.get())
            version = self.phien_ban_var.get()
            original = os.path.splitext(self.imported_file_name)[0]
            suffix = "_large" if self.imported_file_size_mb > 100 else ""
            default_name = f"{original}{suffix}_equation_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            output = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")], initialfile=default_name)
            if not output:
                return
            progress = self._create_progress_window("Đang xử lý file Excel...")
            def worker():
                try:
                    result = self.batch_processor.process_file_smart(self.imported_file_path, n, version, output)
                    progress.destroy()
                    messagebox.showinfo("Hoàn tất", f"Đã xử lý xong. File kết quả:\n{result}")
                except Exception as e:
                    progress.destroy()
                    messagebox.showerror("Lỗi", f"Không thể xử lý: {e}")
            t = threading.Thread(target=worker, daemon=True)
            t.start()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xử lý: {e}")

    def _create_progress_window(self, title):
        progress_window = tk.Toplevel(self.window)
        progress_window.title(title)
        progress_window.geometry("450x180")
        progress_window.resizable(False, False)
        progress_window.grab_set()
        progress_window.transient(self.window)
        tk.Label(progress_window, text=title, font=("Arial", 12, "bold"), anchor='w', justify='left').pack(pady=10, fill='x')
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=self.progress_var, maximum=100, length=350, mode='indeterminate')
        progress_bar.pack(pady=10)
        progress_bar.start()
        self.progress_label = tk.Label(progress_window, text="Chuẩn bị...", font=("Arial", 10), anchor='w', justify='left')
        self.progress_label.pack(pady=5, fill='x')
        warning_label = tk.Label(progress_window, text="⚠️ Đừng đóng cửa sổ! Đang xử lý .", font=("Arial", 8), fg="#FF9800", anchor='w', justify='left')
        warning_label.pack(pady=5, fill='x')
        def cancel_processing():
            self.processing_cancelled = True
            messagebox.showinfo("Đã hủy", "Đã yêu cầu hủy xử lý. Vui lòng đợi...")
            progress_window.after(2000, progress_window.destroy)
        tk.Button(progress_window, text="🛑 Hủy", command=cancel_processing, bg="#F44336", fg="white", font=("Arial", 10)).pack(pady=10)
        return progress_window

    def _export_excel(self):
        try:
            if not self.equation_service:
                messagebox.showwarning("Cảnh báo", "Chưa sẵn sàng dịch vụ.")
                return
            default_name = f"equation_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
            output_path = filedialog.asksaveasfilename(title="Xuất kết quả Equation ra Excel", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], initialfile=default_name)
            if not output_path:
                return
            import pandas as pd
            input_data = [entry.get() for entry in self.input_entries]
            
            # Lấy cả basic và enhanced solutions
            basic_solutions = self.equation_service.get_solutions_text()
            enhanced_solutions = self.equation_service.get_enhanced_solutions_text()
            final_result = self.entry_tong.get(1.0, tk.END).strip()
            encoded_coeffs = self.equation_service.get_encoded_coefficients_display()
            
            export_data = {
                'Variable_Count': [self.so_an_var.get()],
                'Calculator_Version': [self.phien_ban_var.get()],
                'Input_Equations': [' | '.join(input_data)],
                'Basic_Solutions': [basic_solutions],
                'Detailed_Analysis': [enhanced_solutions],
                'Encoded_Coefficients': [' '.join(encoded_coeffs)],
                'Final_Keylog': [final_result],
                'Export_Time': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            }
            pd.DataFrame(export_data).to_excel(output_path, index=False, sheet_name='Equation_Results')
            messagebox.showinfo("Xuất thành công", f"Kết quả Equation Mode đã xuất tại:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Lỗi Xuất", f"Lỗi xuất Excel: {str(e)}")

    def _copy_result(self):
        try:
            result_text = self.entry_tong.get(1.0, tk.END).strip()
            if result_text:
                self.window.clipboard_clear()
                self.window.clipboard_append(result_text)
                messagebox.showinfo("Đã copy", f"Đã copy kết quả Equation vào clipboard:\n\n{result_text}")
            else:
                messagebox.showwarning("Cảnh báo", "Không có kết quả để copy!")
        except Exception as e:
            messagebox.showerror("Lỗi Copy", f"Lỗi copy kết quả: {str(e)}")

    def _quit_import_mode(self):
        result = messagebox.askyesno("Thoát chế độ import", "Bạn có chắc muốn thoát chế độ import Excel và quay lại nhập thủ công?")
        if result:
            self.is_imported_mode = False
            self.imported_data = False
            self.has_manual_data = False
            self.has_result = False
            for entry in self.input_entries:
                entry.delete(0, tk.END)
            for entry in self.result_entries:
                entry.config(state='normal'); entry.delete(0, tk.END); entry.config(state='readonly')
            self.entry_nghiem.config(state='normal'); self.entry_nghiem.delete(0, tk.END); self.entry_nghiem.insert(0, "Chưa có kết quả nghiệm"); self.entry_nghiem.config(bg="#FFF9E6", fg="#FF6F00", state='readonly')
            self.entry_tong.config(state='normal'); self.entry_tong.delete(1.0, tk.END)
            service_status = "Service Ready" if self.equation_service else "Service Failed"; config_info = "Config loaded" if self.config else "Fallback config"
            self.entry_tong.insert(tk.END, f"Equation Mode v2.2 - {service_status} | {config_info}"); self.entry_tong.config(bg="#F1F8E9", font=("Courier New", 9), state='disabled')
            self.btn_copy_result.grid_remove(); self._update_button_visibility()
            self.status_label.config(text="🟢 Đã quay lại chế độ thủ công", fg="#2E7D32")

if __name__ == "__main__":
    root = tk.Tk()
    app = EquationView(root)
    root.mainloop()
