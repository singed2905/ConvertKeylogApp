import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os

from services.polynomial.polynomial_service import PolynomialService
from services.polynomial.polynomial_template_generator import PolynomialTemplateGenerator
from views.polynomial_excel_ui import PolynomialExcelUI

class PolynomialEquationView:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Polynomial Equation Mode v2.1 - Fully Functional! 💪")
        self.window.geometry("900x1200")
        self.window.configure(bg="#F0F8FF")
        self.window.resizable(True, True)
        self.window.minsize(800, 600)

        self.config = config or {}
        self.manual_data_entered = False
        self.has_result = False
        self.is_imported_mode = False

        self.bac_phuong_trinh_var = tk.StringVar(value="2")
        self.phien_ban_var = tk.StringVar()
        self.coefficient_entries = []
        self.root_entries = []

        # Load configuration
        self.phien_ban_list = self._get_available_versions()
        self.phien_ban_var.set(self.phien_ban_list[0] if self.phien_ban_list else "fx799")
        
        # Initialize polynomial service
        self.polynomial_service = None
        self._initialize_service()

        # Setup UI
        self._setup_ui()
        self._update_input_fields()
        self._update_button_visibility()
        self.window.after(1000, self._setup_input_bindings)

    # ========== HELPERS RESTORED ==========
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

    # ========== UI SETUP (unchanged body trimmed) ==========
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

    # keep rest of file content as previous version (methods: _create_header ... _reset_all)
