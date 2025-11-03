# Hotfix: Always show manual action buttons in Polynomial Mode by default
# Buttons will be visible regardless of manual_data_entered; import mode still overrides.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

from services.polynomial.polynomial_service import PolynomialService
from services.polynomial.polynomial_template_generator import PolynomialTemplateGenerator
from views.polynomial_excel_ui import PolynomialExcelUI

class PolynomialEquationView:
    # ... existing methods remain unchanged ...

    def _update_button_visibility(self):
        try:
            if self.is_imported_mode:
                # Show import buttons
                self.frame_buttons_import.pack(fill="x", pady=10)
                self.frame_buttons_manual.pack_forget()
            else:
                # Always show manual buttons by default
                self.frame_buttons_manual.pack(fill="x", pady=10)
                self.frame_buttons_import.pack_forget()
        except Exception:
            pass
