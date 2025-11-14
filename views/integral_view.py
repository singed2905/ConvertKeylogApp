# Integral View - Giao diện Integral Mode cho ConvertKeylogApp
# UI Only - Logic sẽ được implement sau

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class IntegralView:
    """Giao diện Integral Mode - Chuyển đổi và mã hóa tích phân"""
    
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.root.title("Integral Mode v1.0 - ConvertKeylogApp")
        self.root.geometry("980x780")
        self.root.configure(bg="#F0F8FF")
        self.root.resizable(True, True)
        self.root.minsize(860, 600)
        
        # State/UI variables
        self.integral_type_var = tk.StringVar(value="definite")
        self.version_var = tk.StringVar(value="fx799")
        self.variable_var = tk.StringVar(value="x")
        
        self.current_result = ""
        self.has_result = False
        
        # Service placeholder
        self.integral_service = None
        self.service_ready = False
        
        # Build UI
        self._setup_ui()
    
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
        header = tk.Frame(parent, bg="#8E44AD", height=80)
        header.pack(fill="x", pady=(0, 12))
        header.pack_propagate(False)
        
        bar = tk.Frame(header, bg="#8E44AD")
        bar.pack(expand=True, fill="both")
        
        icon = tk.Label(bar, text="∫", font=("Arial", 32), bg="#8E44AD", fg="white")
        icon.pack(side="left", padx=(20, 10), pady=20)
        
        title = tk.Label(bar, text="INTEGRAL MODE v1.0", font=("Arial", 18, "bold"), bg="#8E44AD", fg="white")
        title.pack(side="left", pady=20)
        
        status = "⚠️ UI Only - Logic chưa implement"
        subtitle = tk.Label(bar, text=f"{status}", font=("Arial", 11), bg="#8E44AD", fg="#E8DAEF")
        subtitle.pack(side="right", padx=(0, 20), pady=(25, 15))
    
    def _create_control_panel(self, parent):
        panel = tk.LabelFrame(parent, text="⚙️ THIẾT LẬP TÍCH PHÂN", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#8E44AD", bd=2, relief="groove")
        panel.pack(fill="x", pady=10)
        
        r1 = tk.Frame(panel, bg="#FFFFFF")
        r1.pack(fill="x", padx=20, pady=(12, 10))
        
        tk.Label(r1, text="Loại tích phân:", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333", width=15, anchor="w").pack(side="left")
        cb_type = ttk.Combobox(r1, textvariable=self.integral_type_var, values=["definite", "indefinite"], state="readonly", width=20, font=("Arial", 11))
        cb_type.pack(side="left", padx=10)
        cb_type.bind("<<ComboboxSelected>>", self._on_integral_type_changed)
        
        tk.Label(r1, text="Biến số:", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333", width=15, anchor="w").pack(side="left", padx=(20,0))
        cb_var = ttk.Combobox(r1, textvariable=self.variable_var, values=["x", "t", "u", "θ"], state="readonly", width=8, font=("Arial", 11))
        cb_var.pack(side="left", padx=10)
        
        tk.Label(r1, text="Phiên bản:", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#333", width=15, anchor="w").pack(side="left", padx=(20,0))
        cb_ver = ttk.Combobox(r1, textvariable=self.version_var, values=["fx799", "fx991", "fx570"], state="readonly", width=10, font=("Arial", 11))
        cb_ver.pack(side="left", padx=10)
    
    def _create_guide_section(self, parent):
        guide = tk.LabelFrame(parent, text="💡 HƯỚNG DẪN NHẬP LIỆU", font=("Arial", 10, "bold"), bg="#F4ECF7", fg="#6C3483", bd=1)
        guide.pack(fill="x", pady=6)
        text = (
            "• Hàm số: x^2, sin(x), cos(x), sqrt(x), ln(x), exp(x)\n"
            "• Tích phân xác định: cần nhập cận dưới và cận trên\n"
            "• Tích phân bất định: chỉ cần nhập hàm số\n"
            "• Kết quả keylog: prefix + encoded_function + bounds + ="
        )
        tk.Label(guide, text=text, font=("Arial", 9), bg="#F4ECF7", fg="#333", justify="left", anchor="w").pack(side="left", padx=15, pady=8)
    
    def _create_input_section(self, parent):
        self.input_frame = tk.LabelFrame(parent, text="📝 NHẬP DỮ LIỆU", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#8E44AD", bd=2, relief="groove")
        self.input_frame.pack(fill="x", pady=10)
        
        # Hàm số
        row_func = tk.Frame(self.input_frame, bg="#FFFFFF")
        row_func.pack(fill="x", padx=20, pady=8)
        tk.Label(row_func, text="Hàm số f(x):", font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#8E44AD", width=18, anchor="w").pack(side="left")
        self.function_entry = tk.Entry(row_func, width=35, font=("Arial", 11), bd=2, relief="groove")
        self.function_entry.pack(side="left", padx=10)
        tk.Label(row_func, text="Ví dụ: x^2 + 2*x + 1", font=("Arial", 9, "italic"), bg="#FFFFFF", fg="#666").pack(side="left", padx=10)
        
        # Cận dưới
        self.lower_bound_row = tk.Frame(self.input_frame, bg="#FFFFFF")
        self.lower_bound_row.pack(fill="x", padx=20, pady=6)
        tk.Label(self.lower_bound_row, text="Cận dưới (a):", font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#8E44AD", width=18, anchor="w").pack(side="left")
        self.lower_bound_entry = tk.Entry(self.lower_bound_row, width=20, font=("Arial", 11), bd=2, relief="groove")
        self.lower_bound_entry.pack(side="left", padx=10)
        tk.Label(self.lower_bound_row, text="Ví dụ: 0, pi/2, sqrt(2)", font=("Arial", 9, "italic"), bg="#FFFFFF", fg="#666").pack(side="left", padx=10)
        
        # Cận trên
        self.upper_bound_row = tk.Frame(self.input_frame, bg="#FFFFFF")
        self.upper_bound_row.pack(fill="x", padx=20, pady=6)
        tk.Label(self.upper_bound_row, text="Cận trên (b):", font=("Arial", 10, "bold"), bg="#FFFFFF", fg="#8E44AD", width=18, anchor="w").pack(side="left")
        self.upper_bound_entry = tk.Entry(self.upper_bound_row, width=20, font=("Arial", 11), bd=2, relief="groove")
        self.upper_bound_entry.pack(side="left", padx=10)
        tk.Label(self.upper_bound_row, text="Ví dụ: 1, pi, 2", font=("Arial", 9, "italic"), bg="#FFFFFF", fg="#666").pack(side="left", padx=10)
    
    def _create_results_section(self, parent):
        # Tích phân được format
        self.integral_display_frame = tk.LabelFrame(parent, text="🧮 TÍCH PHÂN", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#D35400", bd=2, relief="groove")
        self.integral_display_frame.pack(fill="x", pady=10)
        
        t1c = tk.Frame(self.integral_display_frame, bg="#FFFFFF")
        t1c.pack(fill="x", padx=15, pady=10)
        
        self.integral_display_text = tk.Text(t1c, width=90, height=4, font=("Arial", 11), wrap=tk.WORD, bg="#FFF9E6", fg="#D35400")
        self.integral_display_text.pack(fill="x")
        self.integral_display_text.insert("1.0", "Chưa có tích phân")
        self.integral_display_text.config(state='disabled')
        
        # Giá trị mã hóa
        self.encoded_frame = tk.LabelFrame(parent, text="🔗 GIÁ TRỊ MÃ HÓA", font=("Arial", 12, "bold"), bg="#FFFFFF", fg="#1565C0", bd=2, relief="groove")
        self.encoded_frame.pack(fill="x", pady=10)
        
        t2c = tk.Frame(self.encoded_frame, bg="#FFFFFF")
        t2c.pack(fill="x", padx=15, pady=10)
        
        self.encoded_text = tk.Text(t2c, width=90, height=5, font=("Courier New", 10), wrap=tk.WORD, bg="#E8F4FD", fg="#1565C0")
        self.encoded_text.pack(fill="x")
        self.encoded_text.insert("1.0", "Chưa có dữ liệu mã hóa")
        self.encoded_text.config(state='disabled')
        
        # Keylog cuối
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
        
        self.btn_process = tk.Button(bar, text="🚀 Mã hóa tích phân", command=self._process, bg="#8E44AD", fg="white", font=("Arial", 10, "bold"), width=18, height=2)
        self.btn_process.pack(side="left", padx=8)
        
        self.btn_copy = tk.Button(bar, text="📋 Copy Keylog", command=self._copy, bg="#9C27B0", fg="white", font=("Arial", 10, "bold"), width=16, height=2, state='disabled')
        self.btn_copy.pack(side="left", padx=8)
        
        self.btn_clear = tk.Button(bar, text="🧹 Xóa tất cả", command=self._clear, bg="#607D8B", fg="white", font=("Arial", 10, "bold"), width=14, height=2)
        self.btn_clear.pack(side="left", padx=8)
        
        self.btn_export = tk.Button(bar, text="💾 Xuất Excel", command=self._export, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=14, height=2, state='disabled')
        self.btn_export.pack(side="right", padx=8)
    
    def _create_status_bar(self, parent):
        self.status_label = tk.Label(self.root, text="⚠️ UI Only - Logic chưa được implement", font=("Arial", 10, "bold"), bg="#F0F8FF", fg="#E67E22", relief="sunken", bd=1, anchor="w", pady=4)
        self.status_label.pack(side="bottom", fill="x")
    
    # ===================== EVENTS =====================
    def _on_integral_type_changed(self, event=None):
        """Xử lý khi đổi loại tích phân"""
        integral_type = self.integral_type_var.get()
        
        if integral_type == "definite":
            # Hiện cận
            if not self.lower_bound_row.winfo_ismapped():
                self.lower_bound_row.pack(fill="x", padx=20, pady=6)
            if not self.upper_bound_row.winfo_ismapped():
                self.upper_bound_row.pack(fill="x", padx=20, pady=6)
            self._set_status("Đã chọn tích phân xác định")
        else:
            # Ẩn cận
            if self.lower_bound_row.winfo_ismapped():
                self.lower_bound_row.pack_forget()
            if self.upper_bound_row.winfo_ismapped():
                self.upper_bound_row.pack_forget()
            self._set_status("Đã chọn tích phân bất định")
    
    # ===================== PROCESS (PLACEHOLDER) =====================
    def _process(self):
        """Xử lý mã hóa - Hiện tại chỉ là placeholder"""
        if not self._validate_inputs():
            return
        
        messagebox.showinfo(
            "Thông báo",
            "Logic mã hóa tích phân chưa được implement.\n\n"
            "Hiện tại chỉ có giao diện UI."
        )
        self._set_status("⚠️ Chưa có logic xử lý")
    
    def _validate_inputs(self):
        """Validate input - Placeholder"""
        if not self.function_entry.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập hàm số")
            return False
        
        if self.integral_type_var.get() == "definite":
            if not self.lower_bound_entry.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng nhập cận dưới")
                return False
            if not self.upper_bound_entry.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng nhập cận trên")
                return False
        
        return True
    
    # ===================== ACTIONS =====================
    def _copy(self):
        """Copy keylog - Placeholder"""
        if not self.current_result:
            messagebox.showwarning("Cảnh báo", "Chưa có kết quả để copy")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.current_result)
        messagebox.showinfo("Thành công", "Đã copy keylog vào clipboard!")
        self._set_status("Đã copy keylog")
    
    def _clear(self):
        """Xóa tất cả dữ liệu"""
        self.function_entry.delete(0, tk.END)
        self.lower_bound_entry.delete(0, tk.END)
        self.upper_bound_entry.delete(0, tk.END)
        
        self.integral_display_text.config(state='normal')
        self.integral_display_text.delete("1.0", tk.END)
        self.integral_display_text.insert("1.0", "Chưa có tích phân")
        self.integral_display_text.config(state='disabled')
        
        self.encoded_text.config(state='normal')
        self.encoded_text.delete("1.0", tk.END)
        self.encoded_text.insert("1.0", "Chưa có dữ liệu mã hóa")
        self.encoded_text.config(state='disabled')
        
        self.keylog_text.config(state='normal')
        self.keylog_text.delete("1.0", tk.END)
        self.keylog_text.config(state='disabled')
        
        self.current_result = ""
        self.has_result = False
        self.btn_copy.config(state='disabled')
        self.btn_export.config(state='disabled')
        self._set_status("Đã xóa tất cả dữ liệu")
    
    def _export(self):
        """Export Excel - Placeholder"""
        messagebox.showinfo("Thông báo", "Export Excel sẽ được implement sau")
    
    # ===================== UTIL =====================
    def _set_status(self, text):
        """Cập nhật status bar"""
        self.status_label.config(text=text)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    IntegralView(root)
    root.mainloop()
