import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

from services.polynomial.polynomial_service import PolynomialService
from services.polynomial.polynomial_template_generator import PolynomialTemplateGenerator
from services.polynomial.polynomial_excel_processor import PolynomialExcelProcessor

class PolynomialEquationView:
    """Full Polynomial Mode View: manual input, separated Excel import/process, export, and keylog display"""

    def __init__(self, window, config=None):
        # Window setup
        self.window = window
        self.window.title("Polynomial Equation Mode v2.1")
        self.window.geometry("900x1200")
        self.window.configure(bg="#F0F8FF")
        self.window.resizable(True, True)
        self.window.minsize(800, 600)

        # State
        self.config = config or {}
        self.manual_data_entered = False
        self.has_result = False
        self.is_imported_mode = False
        self.imported_file_path = ""

        # Variables
        self.bac_phuong_trinh_var = tk.StringVar(value="2")
        self.phien_ban_var = tk.StringVar()
        self.coefficient_entries = []

        # Versions
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var.set(self.phien_ban_list[0] if self.phien_ban_list else "fx799")

        # Service
        self.polynomial_service = None
        self._initialize_service()

        # UI
        self._setup_ui()
        self._update_input_fields()
        self._update_button_visibility()
        self.window.after(300, self._setup_input_bindings)

    # ===================== HELPERS =====================
    def _initialize_service(self):
        try:
            self.polynomial_service = PolynomialService(self.config)
            self.polynomial_service.set_degree(int(self.bac_phuong_trinh_var.get()))
            self.polynomial_service.set_version(self.phien_ban_var.get())
        except Exception as e:
            print(f"Warning: init PolynomialService failed: {e}")
            self.polynomial_service = None

    def _get_available_versions(self):
        try:
            if self.config and 'common' in self.config and 'versions' in self.config['common']:
                versions_data = self.config['common']['versions']
                if 'versions' in versions_data:
                    return versions_data['versions']
        except Exception:
            pass
        return ["fx799", "fx991", "fx570", "fx580", "fx115"]

    def _get_polynomial_config(self):
        try:
            if self.config and 'polynomial' in self.config:
                return self.config['polynomial']
        except Exception:
            pass
        return None

    # ===================== UI =====================
    def _setup_ui(self):
        main = tk.Frame(self.window, bg="#F0F8FF"); main.pack(fill="both", expand=True, padx=15, pady=10)
        self._create_header(main)
        self._create_control_panel(main)
        self._create_quick_actions(main)
        self._create_guide_section(main)
        self._create_input_section(main)
        self._create_roots_section(main)
        self._create_final_result_section(main)
        self._create_control_buttons(main)
        self._create_status_bar(main)

    def _create_header(self, parent):
        header = tk.Frame(parent, bg="#1E3A8A", height=80); header.pack(fill="x", pady=(0,12)); header.pack_propagate(False)
        bar = tk.Frame(header, bg="#1E3A8A"); bar.pack(expand=True, fill="both")
        tk.Label(bar, text="📈", font=("Arial", 24), bg="#1E3A8A", fg="white").pack(side="left", padx=(20,10), pady=20)
        tk.Label(bar, text="POLYNOMIAL EQUATION MODE v2.1", font=("Arial", 18, "bold"), bg="#1E3A8A", fg="white").pack(side="left", pady=20)
        status = "✅ Ready" if self.polynomial_service else "⚠️ Error"
        tk.Label(bar, text=f"Service: {status}", font=("Arial", 11), bg="#1E3A8A", fg="#B3D9FF").pack(side="right", padx=(0,20), pady=(25, 15))

    def _create_control_panel(self, parent):
        frame = tk.LabelFrame(parent, text="⚙️ THIẾT LẬP PHƯƠNG TRÌNH", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#1E3A8A", bd=2, relief="groove"); frame.pack(fill="x", pady=10)
        r1 = tk.Frame(frame, bg="#FFFFFF"); r1.pack(fill="x", padx=20, pady=12)
        tk.Label(r1, text="Bậc phương trình:", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333", width=15).pack(side="left")
        cb_bac = ttk.Combobox(r1, textvariable=self.bac_phuong_trinh_var, values=["2","3","4"], state="readonly", width=20, font=("Arial", 11)); cb_bac.pack(side="left", padx=10); cb_bac.bind("<<ComboboxSelected>>", self._on_bac_changed)
        self.equation_form_label = tk.Label(r1, text="ax² + bx + c = 0", font=("Arial", 11, "italic"), bg="#FFFFFF", fg="#666"); self.equation_form_label.pack(side="left", padx=20)
        r2 = tk.Frame(frame, bg="#FFFFFF"); r2.pack(fill="x", padx=20, pady=(0,12))
        tk.Label(r2, text="Phiên bản máy:", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333", width=15).pack(side="left")
        cb_ver = ttk.Combobox(r2, textvariable=self.phien_ban_var, values=self.phien_ban_list, state="readonly", width=20, font=("Arial", 11)); cb_ver.pack(side="left", padx=10); cb_ver.bind("<<ComboboxSelected>>", self._on_phien_ban_changed)
        poly_cfg = self._get_polynomial_config(); solver = poly_cfg.get('solver', {}).get('method', 'numpy') if poly_cfg else 'numpy'
        tk.Label(r2, text=f"Solver: {solver}", font=("Arial", 9), bg="#FFFFFF", fg="#666").pack(side="right", padx=20)

    def _create_quick_actions(self, parent):
        quick = tk.Frame(parent, bg="#F0F8FF"); quick.pack(fill="x", pady=5)
        tk.Button(quick, text="📝 Tạo Template", command=self._create_template, bg="#1565C0", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Button(quick, text="📁 Import Excel", command=self._on_import_excel, bg="#2196F3", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Button(quick, text="🔥 Xử lý File Excel", command=self._on_process_excel, bg="#F44336", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)

    def _create_guide_section(self, parent):
        guide = tk.LabelFrame(parent, text="💡 HƯỚNG DẪN NHẬP LIỆU", font=("Arial", 10, "bold"), bg="#E8F4FD", fg="#1565C0", bd=1); guide.pack(fill="x", pady=5)
        text = ("• Nhập hệ số theo thứ tự từ cao đến thấp (a, b, c cho bậc 2)\n"
                "• Hỗ trợ biểu thức: sqrt(5), sin(pi/2), 1/2, 2^3, log(10)\n"
                "• Ô trống sẽ tự động điền số 0\n"
                "• Phương trình dạng: ax^n + bx^(n-1) + ... + k = 0")
        tk.Label(guide, text=text, font=("Arial", 9), bg="#E8F4FD", fg="#333", justify="left", anchor="w").pack(side="left", padx=15, pady=10)

    def _create_input_section(self, parent):
        self.input_frame = tk.LabelFrame(parent, text="📝 NHẬP HỆ SỐ PHƯƠNG TRÌNH", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#1E3A8A", bd=2, relief="groove"); self.input_frame.pack(fill="x", pady=10)

    def _create_roots_section(self, parent):
        self.roots_frame = tk.LabelFrame(parent, text="🎯 NGHIỆM PHƯƠNG TRÌNH", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#D35400", bd=2, relief="groove"); self.roots_frame.pack(fill="x", pady=10)
        t = tk.Frame(self.roots_frame, bg="#FFFFFF"); t.pack(fill="x", padx=15, pady=12)
        self.roots_text = tk.Text(t, width=80, height=8, font=("Courier New", 10), wrap=tk.WORD, bg="#FFF9E6", fg="#D35400"); self.roots_text.pack(fill="x")
        self.roots_text.insert("1.0", "Chưa có nghiệm được tính")

    def _create_final_result_section(self, parent):
        self.final_frame = tk.LabelFrame(parent, text="📦 KẾT QUẢ TỔNG (CHO MÁY TÍNH)", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#2E7D32", bd=2, relief="groove"); self.final_frame.pack(fill="x", pady=10)
        self.final_result_text = tk.Text(self.final_frame, width=80, height=3, font=("Courier New", 9, "bold"), wrap=tk.WORD, bg="#F1F8E9", fg="#2E7D32"); self.final_result_text.pack(padx=15, pady=12, fill="x")
        service_status = "Service Ready" if self.polynomial_service else "Service Failed"; config_info = "Config loaded" if self.config else "Fallback config"
        self.final_result_text.insert("1.0", f"Polynomial Mode v2.1 - {service_status} | {config_info}")

    def _create_control_buttons(self, parent):
        self.btn_copy_result = tk.Button(parent, text="📋 Copy Kết Quả", command=self._copy_result, bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), width=20)
        self.btn_copy_result.pack(pady=5); self.btn_copy_result.pack_forget()
        self.frame_buttons_manual = tk.Frame(parent, bg="#F0F8FF"); self.frame_buttons_manual.pack(fill="x", pady=10)
        tk.Button(self.frame_buttons_manual, text="🚀 Giải & Mã hóa", command=self._process_polynomial, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_manual, text="💾 Xuất Excel", command=self._export_excel, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.frame_buttons_import = tk.Frame(parent, bg="#F0F8FF"); self.frame_buttons_import.pack(fill="x", pady=10)
        tk.Button(self.frame_buttons_import, text="📁 Import File Khác", command=self._on_import_excel, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_import, text="🔥 Xử lý File Excel", command=self._on_process_excel, bg="#F44336", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_import, text="↩️ Quay lại", command=self._quit_import_mode, bg="#607D8B", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.frame_buttons_import.pack_forget()

    def _create_status_bar(self, parent):
        self.status_label = tk.Label(parent, text="🟢 Sẵn sàng nhập liệu phương trình bậc 2", font=("Arial", 10, "bold"), bg="#F0F8FF", fg="#2E7D32", relief="sunken", bd=1, anchor="w"); self.status_label.pack(fill="x", pady=(10,0))
        tk.Label(parent, text="Polynomial Mode v2.1 • Hỗ trợ giải phương trình bậc cao • Mã hóa tự động", font=("Arial", 8), bg="#F0F8FF", fg="#666").pack(pady=5)

    # ===================== EVENTS =====================
    def _on_bac_changed(self, event=None):
        try:
            bac = int(self.bac_phuong_trinh_var.get())
            forms = {2: "ax² + bx + c = 0", 3: "ax³ + bx² + cx + d = 0", 4: "ax⁴ + bx³ + cx² + dx + e = 0"}
            self.equation_form_label.config(text=forms[bac])
            if self.polynomial_service: self.polynomial_service.set_degree(bac)
            self._update_input_fields(); self.has_result=False; self._hide_copy_button()
            self.status_label.config(text=f"Đã chọn phương trình bậc {bac}", fg="#2E7D32")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đổi bậc phương trình: {e}")

    def _on_phien_ban_changed(self, event=None):
        try:
            if self.polynomial_service: self.polynomial_service.set_version(self.phien_ban_var.get())
            poly_cfg = self._get_polynomial_config(); precision = poly_cfg.get('solver', {}).get('precision', 6) if poly_cfg else 6
            self.status_label.config(text=f"Đã chọn phiên bản: {self.phien_ban_var.get()} (precision: {precision})")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đổi phiên bản: {e}")

    # ===================== INPUT MGMT =====================
    def _setup_input_bindings(self):
        for e in self.coefficient_entries:
            if hasattr(e, 'bind'): e.bind('<KeyRelease>', self._on_manual_input)

    def _on_manual_input(self, event=None):
        if self.is_imported_mode:
            messagebox.showerror("Lỗi", "Đã ở chế độ import, không thể nhập thủ công!")
            if event and hasattr(event, 'widget'): event.widget.delete(0, tk.END)
            return
        has_data = self._check_manual_data()
        if has_data and not self.manual_data_entered:
            self.manual_data_entered = True; self._update_button_visibility(); self.status_label.config(text="✏️ Đang nhập liệu thủ công...", fg="#FF9800")
        elif not has_data and self.manual_data_entered:
            self.manual_data_entered = False; self._update_button_visibility(); self.status_label.config(text=f"🟢 Sẵn sàng nhập liệu phương trình bậc {self.bac_phuong_trinh_var.get()}", fg="#2E7D32")

    def _check_manual_data(self):
        for e in self.coefficient_entries:
            try:
                if e.get().strip(): return True
            except Exception:
                pass
        return False

    def _update_input_fields(self):
        try:
            bac = int(self.bac_phuong_trinh_var.get())
            for w in self.input_frame.winfo_children(): w.destroy()
            self.coefficient_entries = []
            self._create_coefficient_inputs(bac)
            self.window.after(100, self._setup_input_bindings)
        except Exception as e:
            print(f"Lỗi cập nhật input fields: {e}")

    def _create_coefficient_inputs(self, bac):
        tk.Label(self.input_frame, text=f"Nhập {bac + 1} hệ số cho phương trình bậc {bac}:", font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#333").pack(anchor="w", padx=20, pady=10)
        container = tk.Frame(self.input_frame, bg="#FFFFFF"); container.pack(fill="x", padx=20, pady=10)
        for label, var in self._get_coefficient_labels(bac):
            row = tk.Frame(container, bg="#FFFFFF"); row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#1E3A8A", width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=30, font=("Arial", 10), relief="groove", bd=2); entry.pack(side="left", padx=10)
            entry.bind('<KeyRelease>', self._on_manual_input)
            tk.Label(row, text=f"(hệ số {var})", font=("Arial", 9, "italic"), bg="#FFFFFF", fg="#666").pack(side="left", padx=10)
            self.coefficient_entries.append(entry)

    def _get_coefficient_labels(self, bac):
        cfg = {2: [("Hệ số a (x²):", "a"), ("Hệ số b (x):", "b"), ("Hệ số c (hằng số):", "c")], 3: [("Hệ số a (x³):", "a"), ("Hệ số b (x²):", "b"), ("Hệ số c (x):", "c"), ("Hệ số d (hằng số):", "d")], 4: [("Hệ số a (x⁴):", "a"), ("Hệ số b (x³):", "b"), ("Hệ số c (x²):", "c"), ("Hệ số d (x):", "d"), ("Hệ số e (hằng số):", "e")]}
        return cfg.get(bac, cfg[2])

    # ===================== VISIBILITY & MODES =====================
    def _update_button_visibility(self):
        try:
            if self.is_imported_mode:
                self.frame_buttons_import.pack(fill="x", pady=10); self.frame_buttons_manual.pack_forget()
                for e in self.coefficient_entries:
                    try: e.config(state='disabled')
                    except Exception: pass
            else:
                self.frame_buttons_manual.pack(fill="x", pady=10); self.frame_buttons_import.pack_forget()
                for e in self.coefficient_entries:
                    try: e.config(state='normal')
                    except Exception: pass
        except Exception:
            pass

    def _quit_import_mode(self):
        self.is_imported_mode = False
        self.imported_file_path = ""
        self.final_result_text.config(state='normal'); self.final_result_text.delete("1.0", tk.END)
        service_status = "Service Ready" if self.polynomial_service else "Service Failed"; config_info = "Config loaded" if self.config else "Fallback config"
        self.final_result_text.insert("1.0", f"Polynomial Mode v2.1 - {service_status} | {config_info}")
        self.final_result_text.config(state='disabled')
        self._update_button_visibility()
        self.status_label.config(text="↩️ Đã quay lại chế độ nhập tay")

    # ===================== PROCESS =====================
    def _process_polynomial(self):
        try:
            if not self.polynomial_service: messagebox.showerror("Lỗi", "PolynomialService chưa được khởi tạo!"); return
            coeff_inputs = [e.get().strip() for e in self.coefficient_entries]
            is_valid, msg = self.polynomial_service.validate_input(coeff_inputs)
            if not is_valid: messagebox.showwarning("Dữ liệu không hợp lệ", msg); return
            self.status_label.config(text="🔄 Đang giải phương trình...", fg="#FF9800"); self.window.update()
            success, status_msg, roots_display, final_keylog = self.polynomial_service.process_complete_workflow(coeff_inputs)
            if success:
                self.roots_text.config(state='normal'); self.roots_text.delete("1.0", tk.END); self.roots_text.insert("1.0", roots_display); self.roots_text.config(bg="#E8F5E8", fg="#2E7D32", state='disabled')
                self._show_final_result(final_keylog); self.has_result=True; self._show_copy_button(); self.status_label.config(text="✅ Giải phương trình thành công!", fg="#2E7D32")
            else:
                messagebox.showerror("Lỗi Xử lý", status_msg); self.status_label.config(text=f"❌ {status_msg}", fg="#F44336")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý polynomial: {str(e)}"); self.status_label.config(text="❌ Lỗi xử lý", fg="#F44336")

    def _show_copy_button(self):
        try:
            self.btn_copy_result.pack(pady=5, before=self.frame_buttons_manual)
        except Exception:
            try:
                self.btn_copy_result.pack(pady=5)
            except Exception:
                pass

    def _hide_copy_button(self):
        try:
            self.btn_copy_result.pack_forget()
        except Exception:
            pass

    def _show_final_result(self, keylog: str):
        self.final_result_text.config(state='normal'); self.final_result_text.delete("1.0", tk.END); self.final_result_text.insert("1.0", keylog)
        try: self.final_result_text.config(font=("Flexio Fx799VN", 11, "bold"), fg="#000", bg="#E8F5E8")
        except Exception: self.final_result_text.config(font=("Courier New", 11, "bold"), fg="#000", bg="#E8F5E8")
        self.final_result_text.config(state='disabled')

    def _copy_result(self):
        try:
            if not self.has_result: messagebox.showwarning("Cảnh báo", "Chưa có kết quả để copy!"); return
            text = self.final_result_text.get("1.0", tk.END).strip()
            if text: self.window.clipboard_clear(); self.window.clipboard_append(text); messagebox.showinfo("Đã copy", f"Đã copy kết quả Polynomial vào clipboard:\n\n{text}")
            else: messagebox.showwarning("Cảnh báo", "Không có kết quả để copy!")
        except Exception as e:
            messagebox.showerror("Lỗi Copy", f"Lỗi copy kết quả: {str(e)}")

    # ===================== EXCEL (Template/Import/Process/Export) =====================
    def _create_template(self):
        try:
            degree = int(self.bac_phuong_trinh_var.get())
            path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], initialfile=f"polynomial_template_degree_{degree}.xlsx", title=f"Tạo Template cho Bậc {degree}")
            if not path: return
            if PolynomialTemplateGenerator.create_template(degree, path):
                messagebox.showinfo("Thành công", f"Đã tạo template bậc {degree}:\n{path}\n\nGồm 3 sheet: Input • Examples • Instructions")
            else:
                messagebox.showerror("Lỗi", "Không thể tạo template: Unknown error")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo template: {e}")

    def _on_import_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel","*.xlsx *.xls")], title="Chọn file Excel (sheet 'Input')")
        if not path: return
        self.imported_file_path = path
        self.is_imported_mode = True
        self._update_button_visibility()
        self.final_result_text.config(state='normal'); self.final_result_text.delete("1.0", tk.END); self.final_result_text.insert("1.0", f"Excel: {os.path.basename(path)}"); self.final_result_text.config(state='disabled')
        self.status_label.config(text=f"📁 Đã import: {os.path.basename(path)}. Nhấn '🔥 Xử lý File Excel' để chạy.")

    def _on_process_excel(self):
        if not self.imported_file_path:
            messagebox.showwarning("Thiếu file", "Hãy import Excel trước."); return
        default_name = f"polynomial_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        out_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")], initialfile=default_name, title="Lưu file kết quả")
        if not out_path: return
        try:
            degree = int(self.bac_phuong_trinh_var.get()); version = self.phien_ban_var.get()
            processor = PolynomialExcelProcessor(degree, default_version=version)
            results_df = processor.process_batch(self.imported_file_path)
            processor.export_results(results_df, out_path, meta={"Source_File": os.path.basename(self.imported_file_path)})
            self.status_label.config(text="✅ Đã xử lý xong và lưu kết quả", fg="#2E7D32")
            messagebox.showinfo("Hoàn tất", f"Đã xuất kết quả:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xử lý: {e}")

    def _export_excel(self):
        try:
            if not self.has_result or not self.polynomial_service: messagebox.showwarning("Cảnh báo", "Chưa có kết quả để xuất!\n\nVui lòng giải phương trình trước."); return
            output_path = filedialog.asksaveasfilename(title="Xuất kết quả Polynomial ra Excel", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], initialfile=f"polynomial_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            if not output_path: return
            import pandas as pd
            input_data = [e.get() for e in self.coefficient_entries]
            roots_text = self.roots_text.get("1.0", tk.END).strip(); final_result = self.final_result_text.get("1.0", tk.END).strip(); info = self.polynomial_service.get_polynomial_info()
            df = pd.DataFrame({'Polynomial_Degree':[self.bac_phuong_trinh_var.get()], 'Calculator_Version':[self.phien_ban_var.get()], 'Polynomial_Form':[self.polynomial_service.get_polynomial_form_display()], 'Input_Coefficients':[' | '.join(input_data)], 'Encoded_Coefficients':[' | '.join(self.polynomial_service.get_last_encoded_coefficients())], 'Roots_Solution':[roots_text.replace('\n',' | ')], 'Final_Keylog':[final_result], 'Solver_Method':[info.get('solver_method','unknown')], 'Real_Roots_Count':[len(self.polynomial_service.get_real_roots_only())], 'Export_Time':[datetime.now().strftime('%Y-%m-%d %H:%M:%S')]})
            df.to_excel(output_path, index=False, sheet_name='Polynomial_Results')
            messagebox.showinfo("Xuất thành công", f"Kết quả đã xuất tại:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Lỗi Xuất", f"Lỗi xuất Excel: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk(); app = PolynomialEquationView(root); root.mainloop()
