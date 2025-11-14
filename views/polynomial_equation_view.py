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
        # ... (rest giữ nguyên như cũ) ...
        self._setup_ui()
        self._update_input_fields()
        self._update_button_visibility()
        self.window.after(300, self._setup_input_bindings)

    # ... (other methods giữ nguyên, không đổi) ...

    def _create_control_buttons(self, parent):
        self.btn_copy_result = tk.Button(parent, text="📋 Copy Kết Quả", command=self._copy_result, bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), width=20)
        self.btn_copy_result.pack(pady=5); self.btn_copy_result.pack_forget()
        self.frame_buttons_manual = tk.Frame(parent, bg="#F0F8FF"); self.frame_buttons_manual.pack(fill="x", pady=10)
        # PATCH: Split buttons - encode and solve
        tk.Button(self.frame_buttons_manual, text="🔑 Mã hóa Keylog", command=self._encode_only, bg="#13A05D", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_manual, text="🚀 Tính nghiệm & Mã hóa", command=self._process_polynomial, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_manual, text="💾 Xuất Excel", command=self._export_excel, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.frame_buttons_import = tk.Frame(parent, bg="#F0F8FF"); self.frame_buttons_import.pack(fill="x", pady=10)
        tk.Button(self.frame_buttons_import, text="📁 Import File Khác", command=self._on_import_excel, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_import, text="🔥 Xử lý File Excel", command=self._on_process_excel, bg="#F44336", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_import, text="↩️ Quay lại", command=self._quit_import_mode, bg="#607D8B", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        self.frame_buttons_import.pack_forget()

    # PATCH: Encode only button logic
    def _encode_only(self):
        try:
            if not self.polynomial_service:
                messagebox.showerror("Lỗi", "PolynomialService chưa được khởi tạo!")
                return
            coeff_inputs = [e.get().strip() for e in self.coefficient_entries]
            if not any(x for x in coeff_inputs):
                messagebox.showwarning("Thiếu dữ liệu", "Bạn chưa nhập hệ số nào!")
                return
            keylog = self.polynomial_service.get_keylog_preview(coeff_inputs)
            self._show_final_result(keylog)
            self.roots_text.config(state="normal")
            self.roots_text.delete("1.0", tk.END)
            self.roots_text.insert("1.0", "Chưa tính nghiệm. Nhấn 'Tính nghiệm & Mã hóa' để giải!")
            self.roots_text.config(bg="#fff", fg="#AAA", state="disabled")
            self.status_label.config(text="✅ Đã mã hóa, chưa giải nghiệm", fg="#13A05D")
            self._show_copy_button()
            self.has_result = True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi mã hóa hệ số: {e}")
            self.status_label.config(text=f"❌ Lỗi mã hóa", fg="#F44336")

    # ... (rest giữ nguyên như cũ) ...

if __name__ == "__main__":
    root = tk.Tk(); app = PolynomialEquationView(root); root.mainloop()
