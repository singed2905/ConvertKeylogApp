# Vector View - Giao diện Vector Mode cho ConvertKeylogApp
# Tích hợp với VectorService và UI style đồng bộ (FULL IMPLEMENTATION)

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from services.vector import VectorService

class VectorView:
    """Giao diện Vector Mode với VectorService integration và UI style đồng bộ"""
    
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.root.title("Vector Mode v1.0 - ConvertKeylogApp")
        self.root.geometry("980x780")
        self.root.configure(bg="#F0F8FF")
        self.root.resizable(True, True)
        self.root.minsize(860, 600)
        
        # State/UI variables
        self.calc_type_var = tk.StringVar(value="scalar_vector")
        self.dimension_var = tk.StringVar(value="2")
        self.operation_var = tk.StringVar()
        self.version_var = tk.StringVar(value="fx799")
        
        self.current_result = ""
        self.has_result = False
        
        # Service
        try:
            self.vector_service = VectorService()
            self.service_ready = True
        except Exception as e:
            print(f"VectorService init error: {e}")
            self.vector_service = None
            self.service_ready = False
        
        # Ops map (label -> code)
        self.operations_map = {
            "scalar_vector": {
                "Nhân scalar": "multiply",
                "Chia scalar": "divide",
                "Cộng scalar": "add",
                "Trừ scalar": "subtract"
            },
            "vector_vector": {
                "Tích vô hướng": "dot_product",
                "Tích có hướng": "cross_product",
                "Cộng vector": "add",
                "Trừ vector": "subtract",
                "Góc giữa 2 vector": "angle",
                "Khoảng cách": "distance"
            }
        }
        
        # Build UI
        self._setup_ui()
        self._update_operation_dropdown()
        self._normalize_visible_inputs()
    
    # ===================== UI =====================
    def _setup_ui(self):
        main = tk.Frame(self.root, bg="#F0F8FF")
        main.pack(fill="both", expand=True, padx=15, pady=10)
        
        self._create_header(main)
        self._create_control_panel(main)
        self._create_guide_section(main)
        self._create_input_section(main)
        self._create_results_section(main)
        self._create_buttons(main)
        self._create_status_bar(main)
    
    def _create_header(self, parent):
        header = tk.Frame(parent, bg="#1E3A8A", height=80)
        header.pack(fill="x", pady=(0, 12))
        header.pack_propagate(False)
        
        bar = tk.Frame(header, bg="#1E3A8A")
        bar.pack(expand=True, fill="both")
        
        icon = tk.Label(bar, text="🔢", font=("Arial", 24), bg="#1E3A8A", fg="white")
        icon.pack(side="left", padx=(20, 10), pady=20)
        
        title = tk.Label(bar, text="VECTOR MODE v1.0", font=("Arial", 18, "bold"), bg="#1E3A8A", fg="white")
        title.pack(side="left", pady=20)
        
        status = "✅ Ready" if self.service_ready else "⚠️ Error"
        subtitle = tk.Label(bar, text=f"Service: {status} • Encoding với fixed values", font=("Arial", 11), bg="#1E3A8A", fg="#B3D9FF")
        subtitle.pack(side="right", padx=(0, 20), pady=(25, 15))
    
    def _create_control_panel(self, parent):
        panel = tk.LabelFrame(parent, text="⚙️ THIẾT LẬP VECTOR", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#1E3A8A", bd=2, relief="groove")
        panel.pack(fill="x", pady=10)
        
        r1 = tk.Frame(panel, bg="#FFFFFF")
        r1.pack(fill="x", padx=20, pady=(12, 10))
        
        tk.Label(r1, text="Kiểu tính:", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333", width=15, anchor="w").pack(side="left")
        cb_calc = ttk.Combobox(r1, textvariable=self.calc_type_var, values=["scalar_vector", "vector_vector"], state="readonly", width=20, font=("Arial", 11))
        cb_calc.pack(side="left", padx=10)
        cb_calc.bind("<<ComboboxSelected>>", self._on_calc_type_changed)
        
        tk.Label(r1, text="Kích thước:", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333", width=15, anchor="w").pack(side="left", padx=(20,0))
        cb_dim = ttk.Combobox(r1, textvariable=self.dimension_var, values=["2", "3"], state="readonly", width=6, font=("Arial", 11))
        cb_dim.pack(side="left", padx=10)
        cb_dim.bind("<<ComboboxSelected>>", self._on_dimension_changed)
        
        tk.Label(r1, text="Phiên bản:", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333", width=15, anchor="w").pack(side="left", padx=(20,0))
        cb_ver = ttk.Combobox(r1, textvariable=self.version_var, values=["fx799", "fx991", "fx570"], state="readonly", width=10, font=("Arial", 11))
        cb_ver.pack(side="left", padx=10)
        cb_ver.bind("<<ComboboxSelected>>", self._on_version_changed)
        
        r2 = tk.Frame(panel, bg="#FFFFFF")
        r2.pack(fill="x", padx=20, pady=(0, 14))
        tk.Label(r2, text="Phép toán:", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333", width=15, anchor="w").pack(side="left")
        self.operation_combo = ttk.Combobox(r2, textvariable=self.operation_var, state="readonly", width=28, font=("Arial", 11))
        self.operation_combo.pack(side="left", padx=10)
    
    def _create_guide_section(self, parent):
        guide = tk.LabelFrame(parent, text="💡 HƯỚNG DẪN NHẬP LIỆU", font=("Arial", 10, "bold"), bg="#E8F4FD", fg="#1565C0", bd=1)
        guide.pack(fill="x", pady=6)
        text = (
            "• Scalar: 3.14, sqrt(2), pi/2, sin(pi/6)\n"
            "• Vector: 1,2 (2D) hoặc 1,2,3 (3D)\n"
            "• Vector-Vector: Cross chỉ hỗ trợ 3D\n"
            "• Kết quả keylog: prefix + vectorA + C + {scalar? + op + fixed} + ="
        )
        tk.Label(guide, text=text, font=("Arial", 9), bg="#E8F4FD", fg="#333", justify="left", anchor="w").pack(side="left", padx=15, pady=8)
    
    def _create_input_section(self, parent):
        self.input_frame = tk.LabelFrame(parent, text="📝 NHẬP DỮ LIỆU", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#1E3A8A", bd=2, relief="groove")
        self.input_frame.pack(fill="x", pady=10)
        
        self.scalar_row = tk.Frame(self.input_frame, bg="#FFFFFF")
        self.scalar_row.pack(fill="x", padx=20, pady=6)
        tk.Label(self.scalar_row, text="Số thực:", font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#1E3A8A", width=18, anchor="w").pack(side="left")
        self.scalar_entry = tk.Entry(self.scalar_row, width=28, font=("Arial", 10), bd=2, relief="groove")
        self.scalar_entry.pack(side="left", padx=10)
        tk.Label(self.scalar_row, text="Ví dụ: 3.14 hoặc sqrt(2)", font=("Arial", 9, "italic"), bg="#FFFFFF", fg="#666").pack(side="left", padx=10)
        
        row_a = tk.Frame(self.input_frame, bg="#FFFFFF")
        row_a.pack(fill="x", padx=20, pady=6)
        tk.Label(row_a, text="Vector A:", font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#1E3A8A", width=18, anchor="w").pack(side="left")
        self.vector_a_entry = tk.Entry(row_a, width=28, font=("Arial", 10), bd=2, relief="groove")
        self.vector_a_entry.pack(side="left", padx=10)
        self.vector_a_example = tk.Label(row_a, text="Ví dụ: 1,2 (2D) hoặc 1,2,3 (3D)", font=("Arial", 9, "italic"), bg="#FFFFFF", fg="#666")
        self.vector_a_example.pack(side="left", padx=10)
        
        self.row_b = tk.Frame(self.input_frame, bg="#FFFFFF")
        self.row_b.pack(fill="x", padx=20, pady=6)
        tk.Label(self.row_b, text="Vector B:", font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#1E3A8A", width=18, anchor="w").pack(side="left")
        self.vector_b_entry = tk.Entry(self.row_b, width=28, font=("Arial", 10), bd=2, relief="groove")
        self.vector_b_entry.pack(side="left", padx=10)
        self.vector_b_example = tk.Label(self.row_b, text="Ví dụ: 4,5 (2D) hoặc 4,5,6 (3D)", font=("Arial", 9, "italic"), bg="#FFFFFF", fg="#666")
        self.vector_b_example.pack(side="left", padx=10)
    
    def _create_results_section(self, parent):
        self.roots_frame = tk.LabelFrame(parent, text="🎯 KẾT QUẢ TÍNH TOÁN", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#D35400", bd=2, relief="groove")
        self.roots_frame.pack(fill="x", pady=10)
        
        t1c = tk.Frame(self.roots_frame, bg="#FFFFFF")
        t1c.pack(fill="x", padx=15, pady=10)
        
        self.calc_result_text = tk.Text(t1c, width=90, height=5, font=("Courier New", 10), wrap=tk.WORD, bg="#FFF9E6", fg="#D35400")
        self.calc_result_text.pack(fill="x")
        self.calc_result_text.insert("1.0", "Chưa có kết quả")
        self.calc_result_text.config(state='disabled')
        
        self.encoded_frame = tk.LabelFrame(parent, text="🔗 GIÁ TRỊ MÃ HÓA + FIXED VALUES", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#1565C0", bd=2, relief="groove")
        self.encoded_frame.pack(fill="x", pady=10)
        
        t2c = tk.Frame(self.encoded_frame, bg="#FFFFFF")
        t2c.pack(fill="x", padx=15, pady=10)
        
        self.encoded_text = tk.Text(t2c, width=90, height=5, font=("Courier New", 10), wrap=tk.WORD, bg="#E8F4FD", fg="#1565C0")
        self.encoded_text.pack(fill="x")
        self.encoded_text.insert("1.0", "Chưa có dữ liệu mã hóa")
        self.encoded_text.config(state='disabled')
        
        self.final_frame = tk.LabelFrame(parent, text="📦 KEYLOG CUỐI (CHO MÁY TÍNH)", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#2E7D32", bd=2, relief="groove")
        self.final_frame.pack(fill="x", pady=10)
        
        t3c = tk.Frame(self.final_frame, bg="#FFFFFF")
        t3c.pack(fill="x", padx=15, pady=10)
        
        self.keylog_text = tk.Text(t3c, width=90, height=3, font=("Courier New", 11, "bold"), wrap=tk.WORD, bg="#F1F8E9", fg="#2E7D32")
        self.keylog_text.pack(fill="x")
        self.keylog_text.insert("1.0", "")
        self.keylog_text.config(state='disabled')
    
    def _create_buttons(self, parent):
        bar = tk.Frame(parent, bg="#F0F8FF")
        bar.pack(fill="x", pady=12)
        
        self.btn_process = tk.Button(bar, text="🚀 Tính toán & Mã hóa", command=self._process, bg="#2196F3", fg="white", font=("Arial", 10, "bold"), width=18, height=2)
        self.btn_process.pack(side="left", padx=8)
        
        self.btn_copy = tk.Button(bar, text="📋 Copy Keylog", command=self._copy, bg="#9C27B0", fg="white", font=("Arial", 10, "bold"), width=16, height=2, state='disabled')
        self.btn_copy.pack(side="left", padx=8)
        
        self.btn_clear = tk.Button(bar, text="🧹 Xóa tất cả", command=self._clear, bg="#607D8B", fg="white", font=("Arial", 10, "bold"), width=14, height=2)
        self.btn_clear.pack(side="left", padx=8)
        
        self.btn_export = tk.Button(bar, text="💾 Xuất Excel", command=self._export, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=14, height=2, state='disabled')
        self.btn_export.pack(side="right", padx=8)
    
    def _create_status_bar(self, parent):
        self.status_label = tk.Label(self.root, text="🟢 Sẵn sàng - Vector Mode v1.0", font=("Arial", 10, "bold"), bg="#F0F8FF", fg="#2E7D32", relief="sunken", bd=1, anchor="w", pady=4)
        self.status_label.pack(side="bottom", fill="x")
    
    # ===================== EVENTS =====================
    def _on_calc_type_changed(self, event=None):
        self._update_operation_dropdown()
        self._sync_service_config()
        self._normalize_visible_inputs()
        self._set_status("Đã chuyển kiểu tính")
    
    def _on_dimension_changed(self, event=None):
        d = self.dimension_var.get()
        if d == "2":
            self.vector_a_example.config(text="Ví dụ: 1,2 (2D)")
            self.vector_b_example.config(text="Ví dụ: 4,5 (2D)")
        else:
            self.vector_a_example.config(text="Ví dụ: 1,2,3 (3D)")
            self.vector_b_example.config(text="Ví dụ: 4,5,6 (3D)")
        self._update_operation_dropdown()
        self._sync_service_config()
        self._set_status(f"Đã chuyển sang {d}D")
    
    def _on_version_changed(self, event=None):
        self._sync_service_config()
        self._set_status(f"Đã chọn phiên bản: {self.version_var.get()}")
    
    def _update_operation_dropdown(self):
        t = self.calc_type_var.get()
        d = self.dimension_var.get()
        ops = list(self.operations_map[t].keys())
        if t == "vector_vector" and d == "2":
            ops = [o for o in ops if o != "Tích có hướng"]
        self.operation_combo['values'] = ops
        if ops:
            self.operation_var.set(ops[0])
    
    def _sync_service_config(self):
        if not self.vector_service:
            return
        try:
            self.vector_service.set_calculation_type(self.calc_type_var.get())
            self.vector_service.set_dimension(int(self.dimension_var.get()))
            self.vector_service.set_version(self.version_var.get())
        except Exception as e:
            print(f"Service config error: {e}")
    
    # ===================== VISIBILITY CONTROL =====================
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
            pass
    
    # ===================== PROCESS =====================
    def _process(self):
        if not self.vector_service:
            messagebox.showerror("Lỗi", "VectorService không sẵn sàng")
            return
        if not self._validate_inputs():
            return
        self._sync_service_config()
        op_name = self.operation_var.get()
        op_code = self.operations_map[self.calc_type_var.get()][op_name]
        self.vector_service.set_operation(op_code)
        if self.calc_type_var.get() == "scalar_vector":
            if not self.vector_service.process_scalar_input(self.scalar_entry.get().strip()):
                messagebox.showerror("Lỗi", "Không thể xử lý số thực")
                return
        if not self.vector_service.process_vector_A(self.vector_a_entry.get().strip()):
            messagebox.showerror("Lỗi", "Không thể xử lý Vector A")
            return
        if self.calc_type_var.get() == "vector_vector":
            if not self.vector_service.process_vector_B(self.vector_b_entry.get().strip()):
                messagebox.showerror("Lỗi", "Không thể xử lý Vector B")
                return
        success, msg, result = self.vector_service.process_complete_workflow()
        if not success:
            messagebox.showerror("Lỗi", msg)
            self._set_status("❌ Lỗi xử lý")
            return
        self._render_results(result)
        self.btn_copy.config(state='normal')
        self.btn_export.config(state='disabled')
        self.has_result = True
        self._set_status("✅ Tính toán & mã hóa thành công")
    
    def _validate_inputs(self):
        t = self.calc_type_var.get()
        if not self.vector_a_entry.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập Vector A")
            return False
        if t == "scalar_vector" and not self.scalar_entry.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập số thực")
            return False
        if t == "vector_vector" and not self.vector_b_entry.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập Vector B")
            return False
        if not self.operation_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn phép toán")
            return False
        return True
    
    def _render_results(self, result):
        self.calc_result_text.config(state='normal')
        self.calc_result_text.delete("1.0", tk.END)
        self.calc_result_text.insert("1.0", result['calculation_display'])
        self.calc_result_text.config(state='disabled')
        encoded = []
        if result.get('encoded_scalar'):
            encoded.append(f"Scalar: {result['encoded_scalar']}")
        if result.get('encoded_vector_A'):
            encoded.append(f"Vector A: {' = '.join(result['encoded_vector_A'])}")
        if result.get('encoded_vector_B'):
            encoded.append(f"Vector B: {' = '.join(result['encoded_vector_B'])}")
        fv = result['fixed_value']
        encoded.append(f"Fixed value: {fv['fixed_value']} ({fv['description']})")
        self.encoded_text.config(state='normal')
        self.encoded_text.delete("1.0", tk.END)
        self.encoded_text.insert("1.0", "\n".join(encoded))
        self.encoded_text.config(state='disabled')
        self.current_result = result['final_keylog']
        self.keylog_text.config(state='normal')
        self.keylog_text.delete("1.0", tk.END)
        try:
            self.keylog_text.config(font=("Flexio Fx799VN", 11, "bold"))
        except Exception:
            self.keylog_text.config(font=("Courier New", 11, "bold"))
        self.keylog_text.insert("1.0", self.current_result)
        self.keylog_text.config(state='disabled')
    
    # ===================== ACTIONS =====================
    def _copy(self):
        if not self.current_result:
            messagebox.showwarning("Cảnh báo", "Chưa có kết quả để copy")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_result)
        messagebox.showinfo("Thành công", "Đã copy keylog vào clipboard!")
        self._set_status("Đã copy keylog")
    
    def _clear(self):
        self.scalar_entry.delete(0, tk.END)
        self.vector_a_entry.delete(0, tk.END)
        self.vector_b_entry.delete(0, tk.END)
        self.calc_result_text.config(state='normal')
        self.calc_result_text.delete("1.0", tk.END)
        self.calc_result_text.insert("1.0", "Chưa có kết quả")
        self.calc_result_text.config(state='disabled')
        self.encoded_text.config(state='normal')
        self.encoded_text.delete("1.0", tk.END)
        self.encoded_text.insert("1.0", "Chưa có dữ liệu mã hóa")
        self.encoded_text.config(state='disabled')
        self.keylog_text.config(state='normal')
        self.keylog_text.delete("1.0", tk.END)
        self.keylog_text.config(state='disabled')
        if self.vector_service:
            self.vector_service.reset_state()
        self.current_result = ""
        self.has_result = False
        self.btn_copy.config(state='disabled')
        self.btn_export.config(state='disabled')
        self._set_status("Đã xóa tất cả dữ liệu")
    
    def _export(self):
        messagebox.showinfo("Thông báo", "Export Excel sẽ bổ sung sau khi hoàn tất VectorExcelProcessor")
    
    # ===================== UTIL =====================
    def _set_status(self, text):
        self.status_label.config(text=text)


if __name__ == "__main__":
    root = tk.Tk(); root.withdraw()
    VectorView(root)
    root.mainloop()
