import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

from services.polynomial.polynomial_service import PolynomialService
from services.polynomial.polynomial_template_generator import PolynomialTemplateGenerator
from views.polynomial_excel_ui import PolynomialExcelUI

class PolynomialEquationView:
    def __init__(self, window, config=None):
        # Window
        self.window = window
        self.window.title("Polynomial Equation Mode v2.1 - Fully Functional! 💪")
        self.window.geometry("900x1200")
        self.window.configure(bg="#F0F8FF")
        self.window.resizable(True, True)
        self.window.minsize(800, 600)

        # State & config
        self.config = config or {}
        self.manual_data_entered = False
        self.has_result = False
        self.is_imported_mode = False

        # Variables
        self.bac_phuong_trinh_var = tk.StringVar(value="2")
        self.phien_ban_var = tk.StringVar()
        self.coefficient_entries = []
        self.root_entries = []

        # Load versions from config
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var.set(self.phien_ban_list[0] if self.phien_ban_list else "fx799")

        # Service
        self.polynomial_service = None
        self._initialize_service()

        # UI
        self._setup_ui()
        self._update_input_fields()
        self._update_button_visibility()
        self.window.after(500, self._setup_input_bindings)

    # ===================== HELPERS =====================
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

    # ===================== UI SETUP =====================
    def _setup_ui(self):
        main_container = tk.Frame(self.window, bg="#F0F8FF")
        main_container.pack(fill="both", expand=True, padx=15, pady=10)

        self._create_header(main_container)
        self._create_control_panel(main_container)
        self._create_quick_actions(main_container)
        self._create_guide_section(main_container)
        self._create_input_section(main_container)
        self._create_roots_section(main_container)
        self._create_final_result_section(main_container)
        self._create_control_buttons(main_container)
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
        bar = tk.Frame(parent, bg="#F0F8FF"); bar.pack(fill="x", pady=20)
        self.btn_process = tk.Button(bar, text="🚀 Giải & Mã hóa", bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=15, height=2, command=self._process_polynomial); self.btn_process.pack(side="left", padx=10)
        self.btn_export = tk.Button(bar, text="💾 Export Excel", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=15, height=2, command=self._export_excel); self.btn_export.pack(side="left", padx=10)
        self.btn_reset = tk.Button(bar, text="🔄 Reset", bg="#607D8B", fg="white", font=("Arial", 10, "bold"), width=12, height=2, command=self._reset_all); self.btn_reset.pack(side="left", padx=10)
        self.btn_close = tk.Button(bar, text="❌ Đóng", bg="#F44336", fg="white", font=("Arial", 10, "bold"), width=12, height=2, command=self.window.destroy); self.btn_close.pack(side="right", padx=10)

    def _create_status_bar(self, parent):
        self.status_label = tk.Label(parent, text="🟢 Sẵn sàng nhập liệu phương trình bậc 2", font=("Arial", 10, "bold"), bg="#F0F8FF", fg="#2E7D32", relief="sunken", bd=1, anchor="w")
        self.status_label.pack(fill="x", pady=(10,0))
        tk.Label(parent, text="Polynomial Mode v2.1 • Hỗ trợ giải phương trình bậc cao • Mã hóa tự động • Config-driven", font=("Arial", 8), bg="#F0F8FF", fg="#666").pack(pady=5)

    # ===================== EVENTS =====================
    def _on_bac_changed(self, event=None):
        try:
            bac = int(self.bac_phuong_trinh_var.get())
            forms = {2: "ax² + bx + c = 0", 3: "ax³ + bx² + cx + d = 0", 4: "ax⁴ + bx³ + cx² + dx + e = 0"}
            self.equation_form_label.config(text=forms[bac])
            if self.polynomial_service:
                self.polynomial_service.set_degree(bac)
            self._update_input_fields()
            self.has_result = False
            self._hide_copy_button()
            self.status_label.config(text=f"Đã chọn phương trình bậc {bac}", fg="#2E7D32")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đổi bậc phương trình: {e}")

    def _on_phien_ban_changed(self, event=None):
        try:
            phien_ban = self.phien_ban_var.get()
            if self.polynomial_service:
                self.polynomial_service.set_version(phien_ban)
            poly_config = self._get_polynomial_config()
            precision = poly_config.get('solver', {}).get('precision', 6) if poly_config else 6
            self.status_label.config(text=f"Đã chọn phiên bản: {phien_ban} (precision: {precision})")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đổi phiên bản: {e}")

    # ===================== INPUT MANAGEMENT =====================
    def _setup_input_bindings(self):
        for entry in self.coefficient_entries:
            if hasattr(entry, 'bind'):
                entry.bind('<KeyRelease>', self._on_manual_input)

    def _on_manual_input(self, event=None):
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
        for entry in self.coefficient_entries:
            try:
                if entry.get().strip():
                    return True
            except Exception:
                pass
        return False

    def _update_input_fields(self):
        try:
            bac = int(self.bac_phuong_trinh_var.get())
            for widget in self.input_frame.winfo_children():
                widget.destroy()
            self.coefficient_entries = []
            self._create_coefficient_inputs(bac)
            self.window.after(100, self._setup_input_bindings)
        except Exception as e:
            print(f"Lỗi khi cập nhật input fields: {e}")

    def _create_coefficient_inputs(self, bac):
        tk.Label(self.input_frame, text=f"Nhập {bac + 1} hệ số cho phương trình bậc {bac}:", font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#333").pack(anchor="w", padx=20, pady=10)
        input_container = tk.Frame(self.input_frame, bg="#FFFFFF"); input_container.pack(fill="x", padx=20, pady=10)
        labels = self._get_coefficient_labels(bac)
        for label, var_name in labels:
            row = tk.Frame(input_container, bg="#FFFFFF"); row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#1E3A8A", width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=30, font=("Arial", 10), relief="groove", bd=2); entry.pack(side="left", padx=10)
            entry.bind('<KeyRelease>', self._on_manual_input)
            tk.Label(row, text=f"(hệ số {var_name})", font=("Arial", 9, "italic"), bg="#FFFFFF", fg="#666").pack(side="left", padx=10)
            self.coefficient_entries.append(entry)

    def _get_coefficient_labels(self, bac):
        labels_config = {
            2: [("Hệ số a (x²):", "a"), ("Hệ số b (x):", "b"), ("Hệ số c (hằng số):", "c")],
            3: [("Hệ số a (x³):", "a"), ("Hệ số b (x²):", "b"), ("Hệ số c (x):", "c"), ("Hệ số d (hằng số):", "d")],
            4: [("Hệ số a (x⁴):", "a"), ("Hệ số b (x³):", "b"), ("Hệ số c (x²):", "c"), ("Hệ số d (x):", "d"), ("Hệ số e (hằng số):", "e")]
        }
        return labels_config.get(bac, labels_config[2])

    # ===================== BUTTON VISIBILITY =====================
    def _update_button_visibility(self):
        pass
    def _show_copy_button(self):
        self.btn_copy_result.pack(pady=5, before=self.btn_process.master)
    def _hide_copy_button(self):
        self.btn_copy_result.pack_forget()

    # ===================== PROCESS =====================
    def _process_polynomial(self):
        try:
            if not self.polynomial_service:
                messagebox.showerror("Lỗi", "PolynomialService chưa được khởi tạo!"); return
            coefficient_inputs = [entry.get().strip() for entry in self.coefficient_entries]
            is_valid, validation_msg = self.polynomial_service.validate_input(coefficient_inputs)
            if not is_valid:
                messagebox.showwarning("Dữ liệu không hợp lệ", validation_msg); return
            self.status_label.config(text="🔄 Đang giải phương trình...", fg="#FF9800"); self.window.update()
            success, status_msg, roots_display, final_keylog = self.polynomial_service.process_complete_workflow(coefficient_inputs)
            if success:
                self.roots_text.config(state='normal'); self.roots_text.delete("1.0", tk.END); self.roots_text.insert("1.0", roots_display); self.roots_text.config(bg="#E8F5E8", fg="#2E7D32", state='disabled')
                self._show_final_result(final_keylog)
                self.has_result = True; self._show_copy_button(); self.status_label.config(text="✅ Giải phương trình thành công!", fg="#2E7D32")
            else:
                messagebox.showerror("Lỗi Xử lý", status_msg); self.status_label.config(text=f"❌ {status_msg}", fg="#F44336")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý polynomial: {str(e)}"); self.status_label.config(text="❌ Lỗi xử lý", fg="#F44336")

    def _show_final_result(self, keylog: str):
        self.final_result_text.config(state='normal'); self.final_result_text.delete("1.0", tk.END); self.final_result_text.insert("1.0", keylog)
        try:
            self.final_result_text.config(font=("Flexio Fx799VN", 11, "bold"), fg="#000", bg="#E8F5E8")
        except Exception:
            self.final_result_text.config(font=("Courier New", 11, "bold"), fg="#000", bg="#E8F5E8")
        self.final_result_text.config(state='disabled')

    def _copy_result(self):
        try:
            if not self.has_result:
                messagebox.showwarning("Cảnh báo", "Chưa có kết quả để copy!"); return
            result_text = self.final_result_text.get("1.0", tk.END).strip()
            if result_text:
                self.window.clipboard_clear(); self.window.clipboard_append(result_text)
                messagebox.showinfo("Đã copy", f"Đã copy kết quả Polynomial vào clipboard:\n\n{result_text}")
            else:
                messagebox.showwarning("Cảnh báo", "Không có kết quả để copy!")
        except Exception as e:
            messagebox.showerror("Lỗi Copy", f"Lỗi copy kết quả: {str(e)}")

    # ===================== EXCEL =====================
    def _create_template(self):
        try:
            degree = int(self.bac_phuong_trinh_var.get())
            default_name = f"polynomial_template_degree_{degree}.xlsx"
            path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], initialfile=default_name, title=f"Tạo Template cho Phương trình Bậc {degree}")
            if not path: return
            success = PolynomialTemplateGenerator.create_template(degree, path)
            if success:
                messagebox.showinfo("Thành công", f"Đã tạo template bậc {degree}:\n{path}\n\nTemplate gồm 3 sheet:\n• Input: Nhập dữ liệu\n• Examples: Ví dụ mẫu\n• Instructions: Hướng dẫn sử dụng")
            else:
                messagebox.showerror("Lỗi", "Không thể tạo template: Unknown error")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo template: {e}")

    def _import_excel(self):
        messagebox.showinfo("Import Excel", "Dùng nút '🔥 Xử lý File Excel' để chọn file Input và xuất kết quả.")

    def _export_excel(self):
        try:
            if not self.has_result or not self.polynomial_service:
                messagebox.showwarning("Cảnh báo", "Chưa có kết quả để xuất!\n\nVui lòng giải phương trình trước."); return
            default_name = f"polynomial_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            output_path = filedialog.asksaveasfilename(title="Xuất kết quả Polynomial ra Excel", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], initialfile=default_name)
            if not output_path: return
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
        try:
            for entry in self.coefficient_entries: entry.delete(0, tk.END)
            self.roots_text.config(state='normal'); self.roots_text.delete("1.0", tk.END); self.roots_text.insert("1.0", "Chưa có nghiệm được tính"); self.roots_text.config(bg="#FFF9E6", fg="#D35400", state='disabled')
            self.final_result_text.config(state='normal'); self.final_result_text.delete("1.0", tk.END)
            service_status = "Service Ready" if self.polynomial_service else "Service Failed"; config_info = "Config loaded" if self.config else "Fallback config"
            self.final_result_text.insert("1.0", f"Polynomial Mode v2.1 - {service_status} | {config_info}"); self.final_result_text.config(bg="#F1F8E9", font=("Courier New", 9), state='disabled')
            self.manual_data_entered = False; self.has_result = False; self.is_imported_mode = False; self._hide_copy_button()
            if self.polynomial_service: self.polynomial_service.reset_state()
            bac = self.bac_phuong_trinh_var.get(); self.status_label.config(text=f"🔄 Đã reset - Sẵn sàng nhập phương trình bậc {bac}", fg="#2E7D32")
        except Exception as e:
            messagebox.showerror("Lỗi Reset", f"Lỗi khi reset: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk(); app = PolynomialEquationView(root); root.mainloop()
