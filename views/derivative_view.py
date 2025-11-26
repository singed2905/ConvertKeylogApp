import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from services.derivative.derivative_encoding_service import DerivativeEncodingService
# from services.derivative.excel_service import ExcelService  # TODO: Create this


class DerivativeView:

    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.root.title("Đạo hàm Mode - ConvertKeylogApp")
        self.root.geometry("800x600")
        self.root.configure(bg="#F0F8FF")
        self.root.resizable(False, False)

        self.service = DerivativeEncodingService()
        # self.excel_service = ExcelService()  # TODO: Create excel service
        self.mode_var = tk.StringVar(value="1")
        self.latex_entry = None
        self.keylog_output = None
        self.batch_results = []
        self.batch_rows = []
        self.current_file_path = None
        self.output_file_path = None

        self.mode_data = {
            "1": {
                "title": "Mode 1: Đạo hàm bậc 1",
                "description": "Đạo hàm của hàm số tại điểm x. Format: qv{function},{x=value})",
                "example": r"\frac{d}{dx}{x^2}{x=3}"
            }
        }

        self._setup_ui()

    def _setup_ui(self):
        main = tk.Frame(self.root, bg="#F0F8FF")
        main.pack(fill="both", expand=True, padx=15, pady=10)

        header = tk.Frame(main, bg="#E67E22", height=60)
        header.pack(fill="x", pady=(0, 12))
        header.pack_propagate(False)

        bar = tk.Frame(header, bg="#E67E22")
        bar.pack(expand=True, fill="both")
        icon = tk.Label(bar, text="d/dx", font=("Arial", 24), bg="#E67E22", fg="white")
        icon.pack(side="left", padx=(20, 10))
        title = tk.Label(bar, text="DERIVATIVE MODE", font=("Arial", 16, "bold"), bg="#E67E22", fg="white")
        title.pack(side="left")
        subtitle = tk.Label(bar, text="LaTeX → Keylog (Simplified Format)", font=("Arial", 10), bg="#E67E22", fg="#FEF5E7")
        subtitle.pack(side="right", padx=(0, 20))

        mode_label = tk.Label(main, text="Chọn Mode Keylog Format:", font=("Arial", 12, "bold"), bg="#F0F8FF",
                              fg="#E67E22")
        mode_label.pack(anchor="w", padx=10, pady=(10, 3))

        mode_dropdown = ttk.Combobox(main, textvariable=self.mode_var, state="readonly", font=("Arial", 11), width=75)
        mode_dropdown['values'] = (
            "1 - First Derivative (qv format)",
        )
        mode_dropdown.current(0)
        mode_dropdown.pack(padx=10, pady=5)
        mode_dropdown.bind("<<ComboboxSelected>>", self._on_mode_change)

        self.info_frame = tk.Frame(main, bg="#FEF5E7", bd=2, relief="solid")
        self.info_frame.pack(fill="x", padx=10, pady=(10, 5))

        mode1_info = self.mode_data["1"]
        self.info_title = tk.Label(self.info_frame, text="📌 " + mode1_info["title"],
                                   font=("Arial", 11, "bold"), bg="#FEF5E7", fg="#E67E22", anchor="w")
        self.info_title.pack(fill="x", padx=10, pady=(8, 3))

        self.info_desc = tk.Label(self.info_frame, text=mode1_info["description"],
                                  font=("Arial", 10), bg="#FEF5E7", fg="#5A6C7D", anchor="w")
        self.info_desc.pack(fill="x", padx=10, pady=(0, 8))

        label = tk.Label(main, text="Nhập LaTeX:", font=("Arial", 12, "bold"), bg="#F0F8FF", fg="#E67E22")
        label.pack(anchor="w", padx=10, pady=(10, 3))
        self.latex_entry = tk.Entry(main, font=("Courier New", 13), bd=2, relief="groove", width=80)
        self.latex_entry.pack(padx=10, pady=5)
        self.latex_entry.insert(0, mode1_info["example"])

        # Frame chứa các nút
        self.btn_frame = tk.Frame(main, bg="#F0F8FF")
        self.btn_frame.pack(fill="x", pady=12)

        # Buttons cho mode ENCODE MANUAL (hiển thị mặc định)
        self.btn_import = tk.Button(self.btn_frame, text="📁 Import Excel", command=self._on_import_click,
                                    bg="#16A085", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_import.pack(side="left", padx=5)

        self.btn_encode = tk.Button(self.btn_frame, text="🚀 Encode", command=self._encode,
                                    bg="#E67E22", fg="white", font=("Arial", 10, "bold"), width=15)
        self.btn_encode.pack(side="left", padx=5)

        self.btn_copy = tk.Button(self.btn_frame, text="📋 Copy", command=self._copy,
                                  bg="#D35400", fg="white", font=("Arial", 10, "bold"), width=12)
        self.btn_copy.pack(side="left", padx=5)

        self.btn_clear = tk.Button(self.btn_frame, text="🧹 Clear", command=self._clear,
                                   bg="#607D8B", fg="white", font=("Arial", 10, "bold"), width=10)
        self.btn_clear.pack(side="left", padx=5)

        # Buttons cho mode BATCH PROCESSING (ẩn mặc định)
        self.btn_process = tk.Button(self.btn_frame, text="⚙️ Process Excel", command=self._process_batch_direct,
                                     bg="#E67E22", fg="white", font=("Arial", 10, "bold"), width=15)

        self.btn_back = tk.Button(self.btn_frame, text="◀ Back", command=self._go_back,
                                  bg="#95A5A6", fg="white", font=("Arial", 10, "bold"), width=12)

        output_label = tk.Label(main, text="Keylog Output:", font=("Arial", 12, "bold"), bg="#F0F8FF", fg="#E67E22")
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
        messagebox.showinfo("Coming Soon", "Excel import tính năng sẽ được hoàn thiện sau!")
        # TODO: Implement when excel_service is ready
        return

    def _display_file_ready(self):
        """Hiển thị file sẵn sàng xử lý"""
        # TODO: Implement when excel_service is ready
        pass

    def _process_batch_direct(self):
        """Khi click nút Process Excel"""
        # TODO: Implement when excel_service is ready
        messagebox.showinfo("Coming Soon", "Batch processing sẽ được hoàn thiện sau!")

    def _display_batch_results(self):
        """Hiển thị kết quả sau khi xử lý"""
        # TODO: Implement when excel_service is ready
        pass

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
        result = self.service.encode_derivative(latex, selected_mode)

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


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    DerivativeView(root)
    root.mainloop()
