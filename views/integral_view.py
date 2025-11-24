import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from services.integral.integral_encoding_service import IntegralEncodingService
from services.integral.excel_service import ExcelService


class IntegralView:

    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.root.title("Integral Mode - ConvertKeylogApp")
        self.root.geometry("800x600")
        self.root.configure(bg="#F0F8FF")
        self.root.resizable(False, False)

        self.service = IntegralEncodingService()
        self.excel_service = ExcelService()
        self.mode_var = tk.StringVar(value="3")
        self.latex_entry = None
        self.keylog_output = None
        self.batch_results = []
        self.batch_rows = []
        self.current_file_path = None
        self.output_file_path = None

        self.mode_data = {
            "1": {
                "title": "Mode 1: Tích phân xác định",
                "description": "Tích phân có cận trên và cận dưới. Format: y{function})${lower}${upper})",
                "example": "\\int_{0}^{1} x^2 dx"
            },
            "2": {
                "title": "Mode 2: Tích phân xác định",
                "description": "Tích phân có cận trên và cận dưới. Format: y{function})${lower}${upper})",
                "example": "\\int_{a}^{b} x^3 dx"
            },
            "3": {
                "title": "Mode 3: Tích phân xác định",
                "description": "Tích phân có cận trên và cận dưới. Format: y{function}),{lower},{upper})",
                "example": "\\int_{0}^{1} \\sin(x) dx"
            },
            "4": {
                "title": "Mode 4: Tích phân xác định",
                "description": "Tích phân có cận trên và cận dưới. Format: y{function}),{lower},{upper})",
                "example": "\\int_{1}^{2} \\frac{1}{x} dx"
            }
        }

        self._setup_ui()

    def _setup_ui(self):
        main = tk.Frame(self.root, bg="#F0F8FF")
        main.pack(fill="both", expand=True, padx=15, pady=10)

        header = tk.Frame(main, bg="#8E44AD", height=60)
        header.pack(fill="x", pady=(0, 12))
        header.pack_propagate(False)

        bar = tk.Frame(header, bg="#8E44AD")
        bar.pack(expand=True, fill="both")
        icon = tk.Label(bar, text="∫", font=("Arial", 28), bg="#8E44AD", fg="white")
        icon.pack(side="left", padx=(20, 10))
        title = tk.Label(bar, text="INTEGRAL MODE", font=("Arial", 16, "bold"), bg="#8E44AD", fg="white")
        title.pack(side="left")
        subtitle = tk.Label(bar, text="LaTeX → Keylog (4 Format Modes)", font=("Arial", 10), bg="#8E44AD", fg="#E8DAEF")
        subtitle.pack(side="right", padx=(0, 20))

        mode_label = tk.Label(main, text="Chọn Mode Keylog Format:", font=("Arial", 12, "bold"), bg="#F0F8FF",
                              fg="#8E44AD")
        mode_label.pack(anchor="w", padx=10, pady=(10, 3))

        mode_dropdown = ttk.Combobox(main, textvariable=self.mode_var, state="readonly", font=("Arial", 11), width=75)
        mode_dropdown['values'] = (
            "1 - MathI /MathO",
            "2 - MathI /DecimalO",
            "3 - LineI /LineO",
            "4 - LineI /DecimalO"
        )
        mode_dropdown.current(2)
        mode_dropdown.pack(padx=10, pady=5)
        mode_dropdown.bind("<<ComboboxSelected>>", self._on_mode_change)

        self.info_frame = tk.Frame(main, bg="#E8F4F8", bd=2, relief="solid")
        self.info_frame.pack(fill="x", padx=10, pady=(10, 5))

        mode3_info = self.mode_data["3"]
        self.info_title = tk.Label(self.info_frame, text="📌 " + mode3_info["title"],
                                   font=("Arial", 11, "bold"), bg="#E8F4F8", fg="#8E44AD", anchor="w")
        self.info_title.pack(fill="x", padx=10, pady=(8, 3))

        self.info_desc = tk.Label(self.info_frame, text=mode3_info["description"],
                                  font=("Arial", 10), bg="#E8F4F8", fg="#5A6C7D", anchor="w")
        self.info_desc.pack(fill="x", padx=10, pady=(0, 8))

        label = tk.Label(main, text="Nhập LaTeX:", font=("Arial", 12, "bold"), bg="#F0F8FF", fg="#8E44AD")
        label.pack(anchor="w", padx=10, pady=(10, 3))
        self.latex_entry = tk.Entry(main, font=("Courier New", 13), bd=2, relief="groove", width=80)
        self.latex_entry.pack(padx=10, pady=5)
        self.latex_entry.insert(0, mode3_info["example"])

        # Frame chứa các nút
        self.btn_frame = tk.Frame(main, bg="#F0F8FF")
        self.btn_frame.pack(fill="x", pady=12)

        # Buttons cho mode ENCODE MANUAL (hiển thị mặc định)
        self.btn_import = tk.Button(self.btn_frame, text="📁 Import Excel", command=self._on_import_click,
                                    bg="#16A085", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_import.pack(side="left", padx=5)

        self.btn_encode = tk.Button(self.btn_frame, text="🚀 Encode", command=self._encode,
                                    bg="#8E44AD", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_encode.pack(side="left", padx=5)

        self.btn_copy = tk.Button(self.btn_frame, text="📋 Copy", command=self._copy,
                                  bg="#9C27B0", fg="white", font=("Arial", 10, "bold"), width=12)
        self.btn_copy.pack(side="left", padx=5)

        self.btn_clear = tk.Button(self.btn_frame, text="🧹 Clear", command=self._clear,
                                   bg="#607D8B", fg="white", font=("Arial", 10, "bold"), width=10)
        self.btn_clear.pack(side="left", padx=5)

        # Buttons cho mode BATCH PROCESSING (ẩn mặc định)
        self.btn_process = tk.Button(self.btn_frame, text="⚙️ Process Excel", command=self._process_batch_direct,
                                     bg="#E67E22", fg="white", font=("Arial", 10, "bold"), width=15)

        self.btn_back = tk.Button(self.btn_frame, text="◀ Back", command=self._go_back,
                                  bg="#95A5A6", fg="white", font=("Arial", 10, "bold"), width=12)

        output_label = tk.Label(main, text="Keylog Output:", font=("Arial", 12, "bold"), bg="#F0F8FF", fg="#8E44AD")
        output_label.pack(anchor="w", padx=10, pady=(10, 3))
        self.keylog_output = tk.Text(main, font=("Flexio Fx799VN", 11), height=6, bd=2, relief="groove", wrap="word")
        self.keylog_output.pack(padx=10, pady=5, fill="both", expand=True)
        self.keylog_output.config(state="disabled")

        self.status_label = tk.Label(self.root, text="⚠️ Chưa encode", font=("Arial", 10, "bold"), bg="#F0F8FF",
                                     fg="#E67E22", relief="sunken", bd=1, anchor="w", pady=4)
        self.status_label.pack(side="bottom", fill="x")

    def _on_mode_change(self, event):
        selected = self.mode_var.get().split(" - ")[0]
        mode_info = self.mode_data.get(selected)

        if mode_info:
            self.info_title.config(text="📌 " + mode_info["title"])
            self.info_desc.config(text=mode_info["description"])
            self.latex_entry.delete(0, tk.END)
            self.latex_entry.insert(0, mode_info["example"])
            self._set_status(f"Đã chọn {mode_info['title']}")

    def _on_import_click(self):
        """Khi click nút Import Excel"""
        file_path = filedialog.askopenfilename(
            title="Chọn file Excel/CSV",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        self._set_status("🔄 Đang đọc file...")

        # Dùng service để đọc file
        success, rows, error = self.excel_service.read_excel_file(file_path)

        if not success:
            messagebox.showerror("Lỗi", error)
            self._set_status("❌ Lỗi đọc file")
            return

        self.batch_rows = rows
        self.current_file_path = file_path

        # Hiển thị thông tin file
        self._display_file_ready()
        self._show_batch_mode()

    def _display_file_ready(self):
        """Hiển thị file sẵn sàng xử lý"""
        self.keylog_output.config(state="normal")
        self.keylog_output.delete("1.0", tk.END)

        self.keylog_output.tag_configure("filepath", font=("Arial", 10, "bold"), foreground="#2980B9")

        file_info = self.excel_service.get_file_info()

        file_display = f"📁 File: {file_info['path']}\n"
        file_display += f"📊 Kích thước: {file_info['size_mb']} MB\n"
        file_display += f"📝 Số dòng: {len(self.batch_rows)}\n"
        file_display += "=" * 120 + "\n"
        file_display += "⏳ Chờ xử lý...\n"

        self.keylog_output.insert("1.0", file_display, "filepath")
        self.keylog_output.config(state="disabled")
        self._set_status(f"📁 File sẵn sàng: {len(self.batch_rows)} dòng")

    def _process_batch_direct(self):
        """Khi click nút Process Excel"""
        self.batch_results = []
        total = len(self.batch_rows)

        self._set_status("🔄 Đang xử lý...")

        for idx, (latex, mode) in enumerate(self.batch_rows):
            if not latex or mode not in ["1", "2", "3", "4"]:
                continue

            # Mã hóa LaTeX → keylog
            result = self.service.encode_integral(latex, mode)

            # Lưu kết quả: phải lưu keylog thực tế từ result
            self.batch_results.append({
                'latex': latex,
                'mode': mode,
                'keylog': result.get('keylog', 'ERROR'),  # ← Giá trị keylog thực tế
                'status': 'success' if result.get('success') else 'error'
            })

            self._set_status(f"🔄 Đã xử lý {idx + 1}/{total}")

        # Export kết quả ra file (dùng service)
        success, output_file, message = self.excel_service.export_results(self.batch_results)

        if success:
            self.output_file_path = output_file
            messagebox.showinfo("✅ Thành công", message)
        else:
            messagebox.showerror("Lỗi", message)

        self._display_batch_results()

    def _display_batch_results(self):
        """Hiển thị kết quả sau khi xử lý"""
        self.keylog_output.config(state="normal")
        self.keylog_output.delete("1.0", tk.END)

        self.keylog_output.tag_configure("filepath", font=("Arial", 10, "bold"), foreground="#2980B9")

        file_info = self.excel_service.get_file_info()

        # Xác định định dạng output
        output_extension = '.csv' if file_info['use_csv'] else '.xlsx'
        output_file = self.excel_service._get_output_file_path(output_extension)

        display_text = f"📁 File gốc: {file_info['path']}\n"
        display_text += f"📊 Kích thước: {file_info['size_mb']} MB\n"
        display_text += f"📝 Format: {'CSV (tối ưu file lớn)' if file_info['use_csv'] else 'Excel'}\n"
        display_text += f"📈 Số dòng xử lý: {len(self.batch_results)}\n"
        display_text += f"📁 File kết quả: {output_file}\n"
        display_text += "=" * 120 + "\n"
        display_text += "✅ Xử lý thành công!\n"

        self.keylog_output.insert("1.0", display_text, "filepath")
        self.keylog_output.config(state="disabled")
        self._set_status(f"✅ Hoàn thành: {len(self.batch_results)} kết quả")

    def _show_batch_mode(self):
        """Ẩn nút ENCODE, hiện nút PROCESS"""
        self.btn_import.pack_forget()
        self.btn_encode.pack_forget()
        self.btn_copy.pack_forget()
        self.btn_clear.pack_forget()

        self.btn_process.pack(side="left", padx=5)
        self.btn_back.pack(side="left", padx=5)

    def _show_encode_mode(self):
        """Hiện nút ENCODE, ẩn nút PROCESS"""
        self.btn_process.pack_forget()
        self.btn_back.pack_forget()

        self.btn_import.pack(side="left", padx=5)
        self.btn_encode.pack(side="left", padx=5)
        self.btn_copy.pack(side="left", padx=5)
        self.btn_clear.pack(side="left", padx=5)

    def _go_back(self):
        """Quay lại mode encode manual"""
        self.batch_rows = []
        self.batch_results = []
        self.current_file_path = None
        self.output_file_path = None

        self.keylog_output.config(state="normal")
        self.keylog_output.delete("1.0", tk.END)
        self.keylog_output.config(state="disabled")

        self._show_encode_mode()
        self._set_status("⚠️ Quay lại encode manual")

    def _encode(self):
        latex = self.latex_entry.get().strip()
        if not latex:
            messagebox.showerror("Lỗi", "Vui lòng nhập LaTeX")
            self._set_status("Chưa nhập LaTeX")
            return

        if not self.service.is_available():
            messagebox.showerror("Lỗi", "Service không khả dụng")
            self._set_status("❌ Service error")
            return

        selected_mode = self.mode_var.get().split(" - ")[0]
        result = self.service.encode_integral(latex, selected_mode)

        if result['success']:
            keylog = result['keylog']
            self.keylog_output.config(state="normal")
            self.keylog_output.delete("1.0", tk.END)
            self.keylog_output.insert("1.0", keylog)
            self.keylog_output.config(state="disabled")

            messagebox.showinfo("✓ Thành công", f"Đã encode thành công!\n\nKeylog: {keylog}")
            self._set_status("✅ Encode thành công")
        else:
            self.keylog_output.config(state="normal")
            self.keylog_output.delete("1.0", tk.END)
            self.keylog_output.insert("1.0", f"ERROR: {result['error']}")
            self.keylog_output.config(state="disabled")

            messagebox.showerror("Lỗi", result['error'])
            self._set_status("❌ Encode thất bại")

    def _copy(self):
        keylog = self.keylog_output.get("1.0", "end-1c")

        if not keylog or keylog.startswith("ERROR"):
            messagebox.showwarning("Cảnh báo", "Không có keylog để copy")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(keylog)
        messagebox.showinfo("Thành công", "Đã copy keylog!")
        self._set_status("Đã copy keylog")

    def _clear(self):
        selected = self.mode_var.get().split(" - ")[0]
        mode_info = self.mode_data.get(selected)

        if mode_info:
            self.latex_entry.delete(0, tk.END)
            self.latex_entry.insert(0, mode_info["example"])

        self.keylog_output.config(state="normal")
        self.keylog_output.delete("1.0", tk.END)
        self.keylog_output.config(state="disabled")
        self.current_file_path = None
        self._set_status("⚠️ Đã xóa dữ liệu")

    def _set_status(self, text):
        self.status_label.config(text=text)

    def _process_batch_direct(self):
        """Khi click nút Process Excel"""
        self.batch_results = []
        total = len(self.batch_rows)

        self._set_status("🔄 Đang xử lý...")

        print(f"DEBUG: Total rows = {total}")  # ← Debug
        print(f"DEBUG: batch_rows = {self.batch_rows[:3]}")  # ← Hiển thị 3 dòng đầu

        for idx, (latex, mode) in enumerate(self.batch_rows):
            if not latex or mode not in ["1", "2", "3", "4"]:
                print(f"DEBUG: Row {idx} skipped - latex='{latex}', mode='{mode}'")  # ← Debug
                continue

            result = self.service.encode_integral(latex, mode)
            print(f"DEBUG: Row {idx} - latex='{latex}', mode='{mode}', result={result}")  # ← Debug

            self.batch_results.append({
                'latex': latex,
                'mode': mode,
                'keylog': result.get('keylog', 'ERROR'),
                'status': 'success' if result.get('success') else 'error'
            })

            self._set_status(f"🔄 Đã xử lý {idx + 1}/{total}")

        print(f"DEBUG: Final batch_results = {self.batch_results[:3]}")  # ← Debug


        success, output_file, message = self.excel_service.export_results(self.batch_results)
        if success:
            self.output_file_path = output_file
            # Thông báo thành công
            messagebox.showinfo(
                "✅ Thành công",
                f"✅ Đã xử lý thành công toàn bộ file!\n\n"
                f"File output: {output_file}\n"
                f"{len(self.batch_results)} dòng đã được chuyển đổi."
            )
            self._set_status(f"✅ Xử lý thành công {len(self.batch_results)} dòng")
        else:
            messagebox.showerror("Lỗi", message)
            self._set_status("❌ Lỗi export")

        self._display_batch_results()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    IntegralView(root)
    root.mainloop()
