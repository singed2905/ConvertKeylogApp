import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import os

from services.polynomial.polynomial_excel_processor import PolynomialExcelProcessor

class PolynomialExcelUI:
    """Helpers to integrate batch Excel processing into PolynomialEquationView"""
    
    def __init__(self):
        pass

    @staticmethod
    def run_batch(window, degree_getter, version_getter):
        try:
            # Ask input file
            file_path = filedialog.askopenfilename(
                title="Chọn file Excel Input (sheet 'Input')",
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )
            if not file_path:
                return
            degree = int(degree_getter())
            default_version = version_getter()
            processor = PolynomialExcelProcessor(degree=degree, default_version=default_version)
            results_df = processor.process_batch(file_path)
            # Ask output file
            default_name = f"polynomial_results_deg{degree}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            out_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=default_name,
                title="Lưu kết quả batch"
            )
            if not out_path:
                return
            processor.export_results(results_df, out_path, meta={"Source_File": os.path.basename(file_path)})
            messagebox.showinfo("Thành công", f"Đã xử lý batch và xuất kết quả:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Lỗi batch", str(e))
