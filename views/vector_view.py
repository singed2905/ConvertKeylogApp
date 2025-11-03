# Vector View - Giao diện Vector Mode cho ConvertKeylogApp
# ... (file truncated for brevity in commit preview)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
from services.vector import VectorService

class VectorView:
    def __init__(self, parent):
        # ... original init content ...
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.root.title("Vector Mode v1.0 - ConvertKeylogApp")
        self.root.geometry("980x780")
        self.root.configure(bg="#F0F8FF")
        self.root.resizable(True, True)
        self.root.minsize(860, 600)
        
        self.calc_type_var = tk.StringVar(value="scalar_vector")
        self.dimension_var = tk.StringVar(value="2")
        self.operation_var = tk.StringVar()
        self.version_var = tk.StringVar(value="fx799")
        
        self.current_result = ""
        self.has_result = False
        
        try:
            self.vector_service = VectorService()
            self.service_ready = True
        except Exception as e:
            print(f"VectorService init error: {e}")
            self.vector_service = None
            self.service_ready = False
        
        self.operations_map = {
            "scalar_vector": {"Nhân scalar": "multiply", "Chia scalar": "divide", "Cộng scalar": "add", "Trừ scalar": "subtract"},
            "vector_vector": {"Tích vô hướng": "dot_product", "Tích có hướng": "cross_product", "Cộng vector": "add", "Trừ vector": "subtract", "Góc giữa 2 vector": "angle", "Khoảng cách": "distance"}
        }
        
        self._setup_ui()
        self._update_operation_dropdown()
        # NEW: normalize visibility immediately so only 2 inputs show initially
        self._normalize_visible_inputs()

    # ... keep rest of original methods ...

    def _on_calc_type_changed(self, event=None):
        t = self.calc_type_var.get()
        # remove immediate pack/forget and delegate to normalizer
        self._update_operation_dropdown()
        self._sync_service_config()
        self._normalize_visible_inputs()
        self._set_status("Đã chuyển kiểu tính")

    # NEW: central visibility controller to ensure never 3 inputs at once
    def _normalize_visible_inputs(self):
        try:
            t = self.calc_type_var.get()
            if t == "scalar_vector":
                if self.row_b.winfo_ismapped():
                    self.row_b.pack_forget()
                if not self.scalar_row.winfo_ismapped():
                    self.scalar_row.pack(fill="x", padx=20, pady=6)
            else:
                if self.scalar_row.winfo_ismapped():
                    self.scalar_row.pack_forget()
                if not self.row_b.winfo_ismapped():
                    self.row_b.pack(fill="x", padx=20, pady=6)
        except Exception:
            # In case widgets not yet created when called early
            pass

    # keep rest of file unchanged
