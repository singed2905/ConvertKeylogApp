import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

from services.polynomial.polynomial_service import PolynomialService
from services.polynomial.polynomial_template_generator import PolynomialTemplateGenerator
from views.polynomial_excel_ui import PolynomialExcelUI

class PolynomialEquationView:
    # ... existing class content ...

    def _create_quick_actions(self, parent):
        quick = tk.Frame(parent, bg="#F0F8FF"); quick.pack(fill="x", pady=5)
        tk.Button(quick, text="📝 Tạo Template", command=self._create_template, bg="#1565C0", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Button(quick, text="📁 Import Excel", command=self._on_import_excel, bg="#2196F3", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)
        tk.Button(quick, text="🔥 Xử lý File Excel", command=self._on_process_excel, bg="#F44336", fg="white", font=("Arial", 9, "bold")).pack(side="left", padx=2)

    # ===== Import/Process Excel separated logic =====
    def _on_import_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel","*.xlsx *.xls")], title="Chọn file Excel (sheet 'Input')")
        if not path:
            return
        self.imported_file_path = path
        self.is_imported_mode = True
        # Disable manual inputs
        for e in self.coefficient_entries:
            try:
                e.config(state='disabled')
            except Exception:
                pass
        # Show file name in final result area
        self.final_result_text.config(state='normal')
        self.final_result_text.delete("1.0", tk.END)
        self.final_result_text.insert("1.0", f"Excel: {os.path.basename(path)}")
        self.final_result_text.config(state='disabled')
        # Update buttons visibility
        self._update_button_visibility()
        self.status_label.config(text=f"📁 Đã import: {os.path.basename(path)}. Nhấn '🔥 Xử lý File Excel' để chạy.")

    def _on_process_excel(self):
        if not getattr(self, 'imported_file_path', None):
            messagebox.showwarning("Thiếu file", "Hãy import Excel trước.")
            return
        # Choose output path
        default_name = f"polynomial_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        out_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")], initialfile=default_name, title="Lưu file kết quả")
        if not out_path:
            return
        # Run processor via helper
        try:
            # Freeze UI
            self.status_label.config(text="🔄 Đang xử lý file Excel...", fg="#FF9800")
            self.window.update()
            # Use helper to process
            from services.polynomial.polynomial_excel_processor import PolynomialExcelProcessor
            degree = int(self.bac_phuong_trinh_var.get())
            version = self.phien_ban_var.get()
            processor = PolynomialExcelProcessor(degree, default_version=version)
            results_df = processor.process_batch(self.imported_file_path)
            processor.export_results(results_df, out_path, meta={"Source_File": os.path.basename(self.imported_file_path)})
            # Update UI
            self.status_label.config(text="✅ Đã xử lý xong và lưu kết quả", fg="#2E7D32")
            messagebox.showinfo("Hoàn tất", f"Đã xuất kết quả:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xử lý: {e}")
        finally:
            # Keep import mode, but allow user to change file or reset
            pass

    def _update_button_visibility(self):
        try:
            if getattr(self, 'is_imported_mode', False):
                self.frame_buttons_import.pack(fill="x", pady=10)
                self.frame_buttons_manual.pack_forget()
            else:
                self.frame_buttons_manual.pack(fill="x", pady=10)
                self.frame_buttons_import.pack_forget()
        except Exception:
            pass
