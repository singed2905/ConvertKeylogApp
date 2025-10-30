import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

from services.equation.equation_template_generator import EquationTemplateGenerator
from services.equation.equation_batch_processor import EquationBatchProcessor
from services.equation.equation_service import EquationService

class EquationView:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Equation Mode - Giải Hệ Phương Trình Thực")
        self.window.geometry("850x1100")
        self.window.configure(bg="#F5F5F5")

        # Lưu config được truyền vào
        self.config = config or {}

        # Khởi tạo biến
        self.so_an_var = tk.StringVar(value="2")
        self.phien_ban_var = tk.StringVar()

        # Biến lưu các ô nhập liệu và kết quả
        self.input_entries = []
        self.result_entries = []

        # Trạng thái hiện tại
        self.is_imported_mode = False
        self.has_manual_data = False
        self.has_result = False
        self.import_file_path = None

        # Load danh sách phiên bản từ config
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var.set(self.phien_ban_list[0] if self.phien_ban_list else "fx799")
        
        # Khởi tạo EquationService & batch processor
        self.equation_service = None
        self.batch_processor = EquationBatchProcessor()
        self._initialize_service()

        self._setup_ui()
        self._update_input_fields()
        self._update_button_visibility()
    
    def _initialize_service(self):
        """Khởi tạo EquationService"""
        try:
            self.equation_service = EquationService(self.config)
            self.equation_service.set_variables_count(int(self.so_an_var.get()))
            self.equation_service.set_version(self.phien_ban_var.get())
        except Exception as e:
            print(f"Warning: Không thể khởi tạo EquationService: {e}")
            messagebox.showwarning("Cảnh báo", 
                f"Không thể khởi tạo EquationService.\nMột số tính năng sẽ bị hạn chế.\n\nLỗi: {e}")
    
    def _get_available_versions(self):
        try:
            if self.config and 'common' in self.config and 'versions' in self.config['common']:
                versions_data = self.config['common']['versions']
                if 'versions' in versions_data:
                    return versions_data['versions']
        except Exception as e:
            print(f"Warning: Không thể load versions từ config: {e}")
        return ["fx799", "fx800", "fx801", "fx802", "fx803"]
    
    def _get_equation_prefixes(self):
        try:
            if self.config and 'equation' in self.config and 'prefixes' in self.config['equation']:
                prefixes_data = self.config['equation']['prefixes']
                if 'versions' in prefixes_data:
                    return prefixes_data['versions']
        except Exception as e:
            print(f"Warning: Không thể load equation prefixes từ config: {e}")
        return None

    def _setup_ui(self):
        main_frame = tk.Frame(self.window, bg="#F5F5F5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        title_label = tk.Label(
            main_frame,
            text="🧠 EQUATION MODE v2.0 - GIẢI HỆ PHƯƠNG TRÌNH",
            font=("Arial", 18, "bold"),
            bg="#F5F5F5",
            fg="#2E7D32"
        )
        title_label.pack(pady=(0, 15))

        control_frame = tk.LabelFrame(
            main_frame,
            text="⚙️ THIẾT LậP PHƯƠNG TRÌNH",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#1B5299",
            bd=2,
            relief="groove"
        )
        control_frame.pack(fill="x", pady=10, padx=10)

        row1 = tk.Frame(control_frame, bg="#FFFFFF")
        row1.pack(fill="x", padx=15, pady=10)

        tk.Label(row1, text="Số ẩn:", font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#333333", width=12).pack(side="left")
        so_an_menu = ttk.Combobox(row1, textvariable=self.so_an_var, values=["2","3","4"], state="readonly", width=15, font=("Arial", 10))
        so_an_menu.pack(side="left", padx=5)
        so_an_menu.bind("<<ComboboxSelected>>", self._on_so_an_changed)

        row2 = tk.Frame(control_frame, bg="#FFFFFF")
        row2.pack(fill="x", padx=15, pady=10)

        tk.Label(row2, text="Phiên bản máy:", font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#333333", width=12).pack(side="left")
        phien_ban_menu = ttk.Combobox(row2, textvariable=self.phien_ban_var, values=self.phien_ban_list, state="readonly", width=15, font=("Arial", 10))
        phien_ban_menu.pack(side="left", padx=5)
        phien_ban_menu.bind("<<ComboboxSelected>>", self._on_phien_ban_changed)

        service_status = "✅ Service Ready" if self.equation_service else "⚠️ Service Failed"
        config_status = "Config: ✅ Loaded" if self.config else "Config: ⚠️ Fallback"
        tk.Label(row2, text=f"{service_status} | {config_status}", font=("Arial", 8), bg="#FFFFFF", fg="#666666").pack(side="right", padx=20)

        # Excel action buttons
        excel_frame = tk.Frame(main_frame, bg="#F5F5F5")
        excel_frame.pack(fill="x", pady=(0,8))
        tk.Button(excel_frame, text="📝 Tạo Template", bg="#1565C0", fg="white", font=("Arial", 10, "bold"), command=self._on_create_template).pack(side="left")
        tk.Button(excel_frame, text="📁 Import Excel", bg="#FF9800", fg="white", font=("Arial", 10, "bold"), command=self._on_import_excel).pack(side="left", padx=6)
        tk.Button(excel_frame, text="🔥 Xử lý File Excel", bg="#2E7D32", fg="white", font=("Arial", 10, "bold"), command=self._on_process_excel).pack(side="left")

        guide_frame = tk.LabelFrame(
            main_frame,
            text="💡 HƯỚNG DẪN NHẬP LIỆU",
            font=("Arial", 10, "bold"),
            bg="#E3F2FD",
            fg="#1565C0",
            bd=1,
            relief="solid"
        )
        guide_frame.pack(fill="x", pady=5, padx=10)
        tk.Label(guide_frame, text=("• Hỗ trợ biểu thức: sqrt(5), sin(pi/2), 1/2, 2^3, log(10)\n"
                                    "• Nhập hệ số cách nhau bằng dấu phẩy\n"
                                    "• Ô trống sẽ tự động điền số 0"), font=("Arial", 9), bg="#E3F2FD", fg="#333333", justify="left").pack(padx=10, pady=8)

        self.input_frame = tk.LabelFrame(main_frame, text="📝 NHẬP HỆ SỐ PHƯƠNG TRÌNH", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#1B5299", bd=2, relief="groove")
        self.input_frame.pack(fill="x", pady=10, padx=10)

        self.result_frame = tk.LabelFrame(main_frame, text="🔐 KẾT QUẢ MÃ HÓA", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#7B1FA2", bd=2, relief="groove")
        self.result_frame.pack(fill="x", pady=10, padx=10)

        self.frame_nghiem = tk.LabelFrame(main_frame, text="🎯 KẾT QUẢ NGHIỆM", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#D35400", bd=2, relief="groove")
        self.frame_nghiem.pack(fill="x", pady=10, padx=10)
        self.entry_nghiem = tk.Entry(self.frame_nghiem, width=80, font=("Arial", 10), justify="center")
        self.entry_nghiem.pack(padx=15, pady=12, fill="x")
        self.entry_nghiem.insert(0, "Chưa có kết quả nghiệm")
        self.entry_nghiem.config(bg="#FFF9E6", fg="#FF6F00")

        self.frame_tong = tk.LabelFrame(main_frame, text="📦 KẾT QUẢ TỔNG (CHO MÁY TÍNH)", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#2E7D32", bd=2, relief="groove")
        self.frame_tong.pack(fill="x", pady=10, padx=10)
        self.entry_tong = tk.Text(self.frame_tong, width=80, height=2, font=("Courier New", 9, "bold"), wrap=tk.NONE, state='normal')
        self.entry_tong.pack(padx=15, pady=12, fill="x")
        service_status = "Service Ready" if self.equation_service else "Service Failed"
        config_info = "Config loaded" if self.config else "Fallback config"
        self.entry_tong.insert(tk.END, f"Equation Mode v2.0 - {service_status} | {config_info}")
        self.entry_tong.config(bg="#F1F8E9")

        self.btn_copy_result = tk.Button(main_frame, text="📋 Copy Kết Quả", command=self._copy_result, bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), width=20)
        self.btn_copy_result.pack(pady=5)
        self.btn_copy_result.pack_forget()

        button_frame = tk.Frame(main_frame, bg="#F5F5F5")
        button_frame.pack(fill="x", pady=20)
        self.btn_import = tk.Button(button_frame, text="📁 Import Excel", bg="#FF9800", fg="white", font=("Arial", 10, "bold"), width=14, height=1, command=self._import_excel)
        self.btn_import.pack(side="left", padx=5)
        self.btn_process_manual = tk.Button(button_frame, text="🚀 Xử lý & Giải nghiệm", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=18, height=1, command=self._process_equations)
        self.btn_process_manual.pack(side="left", padx=5)
        self.btn_import_other = tk.Button(button_frame, text="📂 Import File Khác", bg="#9C27B0", fg="white", font=("Arial", 10, "bold"), width=14, height=1, command=self._import_excel)
        self.btn_quay_lai = tk.Button(button_frame, text="↩️ Quay lại", bg="#607D8B", fg="white", font=("Arial", 10, "bold"), width=14, height=1, command=self._quit_import_mode)
        self.btn_export = tk.Button(button_frame, text="💾 Xuất Excel", bg="#FF9800", fg="white", font=("Arial", 10, "bold"), width=14, height=1, command=self._export_excel)

        self.status_label = tk.Label(main_frame, text="🟢 Sẵn sàng nhập liệu và giải hệ phương trình", font=("Arial", 10, "bold"), bg="#F5F5F5", fg="#2E7D32")
        self.status_label.pack(pady=10)

        close_btn = tk.Button(main_frame, text="Đóng", command=self.window.destroy, bg="#F44336", fg="white", font=("Arial", 10, "bold"), width=15, height=1)
        close_btn.pack(pady=10)
        tk.Label(main_frame, text="Phiên bản: v2.0 Giải nghiệm thực • Hỗ trợ biểu thức phức tạp • Config-driven", font=("Arial", 8), bg="#F5F5F5", fg="#666666").pack(side="bottom", pady=5)

    def _on_so_an_changed(self, event=None):
        self._update_input_fields()
        if self.equation_service:
            self.equation_service.set_variables_count(int(self.so_an_var.get()))
        self.status_label.config(text=f"Đã chọn hệ {self.so_an_var.get()} phương trình {self.so_an_var.get()} ẩn")
        self.has_result = False
        self._update_button_visibility()

    def _on_phien_ban_changed(self, event=None):
        selected_version = self.phien_ban_var.get()
        if self.equation_service:
            self.equation_service.set_version(selected_version)
        prefixes = self._get_equation_prefixes()
        prefix_info = ""
        if prefixes and selected_version in prefixes:
            prefix_info = f" - Prefix: {prefixes[selected_version].get('base_prefix','')}"
        self.status_label.config(text=f"Đã chọn phiên bản: {selected_version}{prefix_info}")

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
                tk.Label(row_frame, text=label_text, font=("Arial", 9), bg="#FFFFFF", fg="#333333", width=35).pack(side="left")
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
            4: ["Phương trình 1 (a₁₁, a₁₂, a₁₃, a₁₄, c₁):", "Phương trình 2 (a₂₁, a₂₂, a₂₃, a₂₄, c₂):", "Phương trình 3 (a₃₁, a₃₂, a₃₃, c₃):", "Phương trình 4 (a₄₁, a₄₂, a₄₃, a₄₄, c₄):"]
        }
        return config.get(so_an, config[2])

    def _get_result_count(self, so_an):
        return {2:6, 3:12, 4:20}.get(so_an, 6)

    def _on_manual_input(self, event=None):
        self.has_manual_data = True
        self.is_imported_mode = False
        self._update_button_visibility()

    def _update_button_visibility(self):
        self.btn_import.pack_forget()
        self.btn_import_other.pack_forget()
        self.btn_quay_lai.pack_forget()
        self.btn_export.pack_forget()
        if self.is_imported_mode:
            self.btn_import_other.pack(side="left", padx=5)
            self.btn_quay_lai.pack(side="left", padx=5)
            self.btn_process_manual.pack(side="left", padx=5)
            for entry in self.input_entries:
                entry.config(state='disabled', bg='#F0F0F0')
        elif self.has_manual_data:
            self.btn_process_manual.pack(side="left", padx=5)
            if self.has_result:
                self.btn_export.pack(side="left", padx=5)
            for entry in self.input_entries:
                entry.config(state='normal', bg='white')
        else:
            self.btn_import.pack(side="left", padx=5)
            self.btn_process_manual.pack(side="left", padx=5)
            for entry in self.input_entries:
                entry.config(state='normal', bg='white')

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
            self.status_label.config(text="🔄 Đang xử lý hệ phương trình...", fg="#FF9800")
            self.window.update()
            success, status_msg, solutions_text, final_result = self.equation_service.process_complete_workflow(equation_inputs)
            if success:
                encoded_coeffs = self.equation_service.get_encoded_coefficients_display()
                self._display_encoded_coefficients(encoded_coeffs)
                self.entry_nghiem.config(state='normal')
                self.entry_nghiem.delete(0, tk.END)
                self.entry_nghiem.insert(0, solutions_text)
                self.entry_nghiem.config(bg="#E8F5E8", fg="#2E7D32", state='readonly')
                self.entry_tong.config(state='normal')
                self.entry_tong.delete(1.0, tk.END)
                self.entry_tong.insert(tk.END, final_result)
                try:
                    self.entry_tong.config(font=("Flexio Fx799VN", 11, "bold"), bg="#E8F5E8")
                except:
                    self.entry_tong.config(font=("Courier New", 11, "bold"), bg="#E8F5E8")
                self.entry_tong.config(state='disabled')
                self.has_result = True
                self.btn_copy_result.pack(pady=5)
                self.status_label.config(text="✅ Giải hệ phương trình thành công!", fg="#2E7D32")
                self._update_button_visibility()
            else:
                messagebox.showerror("Lỗi Xử lý", status_msg)
                self.status_label.config(text=f"❌ {status_msg}", fg="#F44336")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý phương trình: {str(e)}")
            self.status_label.config(text="❌ Lỗi xử lý", fg="#F44336")

    def _display_encoded_coefficients(self, encoded_coeffs):
        for i, entry in enumerate(self.result_entries):
            if i < len(encoded_coeffs):
                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, encoded_coeffs[i])
                entry.config(state='readonly', bg="#E8F5E8")

    # ---------------- Excel actions ----------------
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
        path = filedialog.askopenfilename(filetypes=[("Excel","*.xlsx")])
        if not path:
            return
        self.import_file_path = path
        self.is_imported_mode = True
        self.has_manual_data = False
        self._update_button_visibility()
        messagebox.showinfo("Import", f"Đã chọn file:\n{os.path.basename(path)}\nSẵn sàng xử lý.")

    def _on_process_excel(self):
        if not self.import_file_path:
            messagebox.showwarning("Thiếu file", "Hãy import file Excel trước.")
            return
        try:
            n = int(self.so_an_var.get())
            version = self.phien_ban_var.get()
            out = self.batch_processor.process_file(self.import_file_path, n, version)
            messagebox.showinfo("Hoàn tất", f"Đã xử lý xong. File kết quả:\n{out}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xử lý: {e}")

    def _export_excel(self):
        try:
            if not self.has_result or not self.equation_service:
                messagebox.showwarning("Cảnh báo", "Chưa có kết quả để xuất!\n\nVui lòng giải hệ phương trình trước.")
                return
            default_name = f"equation_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            output_path = filedialog.asksaveasfilename(title="Xuất kết quả Equation ra Excel", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], initialfile=default_name)
            if not output_path:
                return
            import pandas as pd
            input_data = [entry.get() for entry in self.input_entries]
            solutions_text = self.entry_nghiem.get()
            final_result = self.entry_tong.get(1.0, tk.END).strip()
            encoded_coeffs = self.equation_service.get_encoded_coefficients_display()
            export_data = {
                'Variable_Count': [self.so_an_var.get()],
                'Calculator_Version': [self.phien_ban_var.get()],
                'Input_Equations': [' | '.join(input_data)],
                'Solutions': [solutions_text],
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
            if not self.has_result:
                messagebox.showwarning("Cảnh báo", "Chưa có kết quả để copy!")
                return
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
            self.has_manual_data = False
            self.has_result = False
            for entry in self.input_entries:
                entry.delete(0, tk.END)
            for entry in self.result_entries:
                entry.config(state='normal'); entry.delete(0, tk.END); entry.config(state='readonly')
            self.entry_nghiem.config(state='normal'); self.entry_nghiem.delete(0, tk.END); self.entry_nghiem.insert(0, "Chưa có kết quả nghiệm"); self.entry_nghiem.config(bg="#FFF9E6", fg="#FF6F00", state='readonly')
            self.entry_tong.config(state='normal'); self.entry_tong.delete(1.0, tk.END)
            service_status = "Service Ready" if self.equation_service else "Service Failed"; config_info = "Config loaded" if self.config else "Fallback config"
            self.entry_tong.insert(tk.END, f"Equation Mode v2.0 - {service_status} | {config_info}"); self.entry_tong.config(bg="#F1F8E9", font=("Courier New", 9), state='disabled')
            self.btn_copy_result.pack_forget(); self._update_button_visibility()
            self.status_label.config(text="🟢 Đã quay lại chế độ thủ công", fg="#2E7D32")

if __name__ == "__main__":
    root = tk.Tk()
    app = EquationView(root)
    root.mainloop()
