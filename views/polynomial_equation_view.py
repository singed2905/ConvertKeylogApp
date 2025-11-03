# Update buttons in Polynomial Mode to mirror Equation Mode styles and layout is already done in previous commit.
# This patch aligns button colors, labels, and order.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

from services.polynomial.polynomial_service import PolynomialService
from services.polynomial.polynomial_template_generator import PolynomialTemplateGenerator
from views.polynomial_excel_ui import PolynomialExcelUI

class PolynomialEquationView:
    # ... keep class header and previous methods ...
    def _create_control_buttons(self, parent):
        # Copy keylog (hidden until result)
        self.btn_copy_result = tk.Button(parent, text="📋 Copy Kết Quả", command=self._copy_result,
                                         bg="#9C27B0", fg="white", font=("Arial", 9, "bold"), width=20)
        self.btn_copy_result.pack(pady=5)
        self.btn_copy_result.pack_forget()

        # Action bars similar to Equation Mode
        self.frame_buttons_manual = tk.Frame(parent, bg="#F0F8FF")
        self.frame_buttons_manual.pack(fill="x", pady=10)
        tk.Button(self.frame_buttons_manual, text="🚀 Giải & Mã hóa", command=self._process_polynomial,
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_manual, text="💾 Xuất Excel", command=self._export_excel,
                  bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)

        self.frame_buttons_import = tk.Frame(parent, bg="#F0F8FF")
        self.frame_buttons_import.pack(fill="x", pady=10)
        tk.Button(self.frame_buttons_import, text="📁 Import File Khác", command=self._import_excel,
                  bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_import, text="🔥 Xử lý File Excel",
                  command=lambda: PolynomialExcelUI.run_batch(self.window, lambda: self.bac_phuong_trinh_var.get(), lambda: self.phien_ban_var.get()),
                  bg="#F44336", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Button(self.frame_buttons_import, text="↩️ Quay lại", command=self._reset_all,
                  bg="#607D8B", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=5)

        # Initial visibility (manual by default)
        self.frame_buttons_import.pack_forget()

    def _update_button_visibility(self):
        try:
            if self.is_imported_mode:
                self.frame_buttons_import.pack(fill="x", pady=10)
                self.frame_buttons_manual.pack_forget()
            elif self.manual_data_entered:
                self.frame_buttons_manual.pack(fill="x", pady=10)
                self.frame_buttons_import.pack_forget()
            else:
                self.frame_buttons_manual.pack_forget()
                self.frame_buttons_import.pack_forget()
        except Exception:
            pass
