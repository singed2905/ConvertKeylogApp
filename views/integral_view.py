# Integral View - UI chỉ 1 ô nhập liệu chuỗi LaTeX về tích phân + validate tích phân
import tkinter as tk
from tkinter import messagebox
from services.integral_service import IntegralService

class IntegralView:
    """Giao diện Integral Mode - 1 ô nhập liệu chuỗi LaTeX tích phân + kiểm tra valid"""
    
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.root.title("Integral Mode v1.2 - ConvertKeylogApp")
        self.root.geometry("700x340")
        self.root.configure(bg="#F0F8FF")
        self.root.resizable(False, False)
        
        self.latex_entry = None
        self.current_result = ""
        self._setup_ui()
        
    def _setup_ui(self):
        main = tk.Frame(self.root, bg="#F0F8FF")
        main.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Header
        header = tk.Frame(main, bg="#8E44AD", height=60)
        header.pack(fill="x", pady=(0, 12))
        header.pack_propagate(False)
        
        bar = tk.Frame(header, bg="#8E44AD")
        bar.pack(expand=True, fill="both")
        icon = tk.Label(bar, text="∫", font=("Arial", 28), bg="#8E44AD", fg="white")
        icon.pack(side="left", padx=(20, 10))
        title = tk.Label(bar, text="INTEGRAL MODE - LaTeX", font=("Arial", 16, "bold"), bg="#8E44AD", fg="white")
        title.pack(side="left")
        subtitle = tk.Label(bar, text="Chỉ nhập 1 chuỗi LaTeX mô tả tích phân", font=("Arial", 10), bg="#8E44AD", fg="#E8DAEF")
        subtitle.pack(side="right", padx=(0, 20))
        
        # Input section
        label = tk.Label(main, text="Nhập chuỗi LaTeX cho tích phân:", font=("Arial", 12, "bold"), bg="#F0F8FF", fg="#8E44AD")
        label.pack(anchor="w", padx=10, pady=(10, 3))
        self.latex_entry = tk.Entry(main, font=("Courier New", 13), bd=2, relief="groove", width=60)
        self.latex_entry.pack(padx=10, pady=5)
        self.latex_entry.insert(0, "\\int_{0}^{1} x^2 dx")
        
        # Action buttons
        btn_frame = tk.Frame(main, bg="#F0F8FF")
        btn_frame.pack(fill="x", pady=12)
        self.btn_process = tk.Button(btn_frame, text="🚀 Kiểm tra tích phân", command=self._process, bg="#8E44AD", fg="white", font=("Arial", 10, "bold"), width=20)
        self.btn_process.pack(side="left", padx=10)
        self.btn_copy = tk.Button(btn_frame, text="📋 Copy chuỗi", command=self._copy, bg="#9C27B0", fg="white", font=("Arial", 10, "bold"), width=14)
        self.btn_copy.pack(side="left", padx=10)
        self.btn_clear = tk.Button(btn_frame, text="🧹 Xóa", command=self._clear, bg="#607D8B", fg="white", font=("Arial", 10, "bold"), width=10)
        self.btn_clear.pack(side="left", padx=10)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="⚠️ UI LaTeX - Chưa kiểm tra", font=("Arial", 10, "bold"), bg="#F0F8FF", fg="#E67E22", relief="sunken", bd=1, anchor="w", pady=4)
        self.status_label.pack(side="bottom", fill="x")
    
    # ===================== Process + Validate =====================
    def _process(self):
        latex = self.latex_entry.get().strip()
        if not latex:
            messagebox.showerror("Lỗi", "Vui lòng nhập chuỗi LaTeX cho tích phân")
            self._set_status("Chưa nhập chuỗi LaTeX.")
            return
        is_valid, msg = IntegralService.validate_integral_latex(latex)
        if is_valid:
            messagebox.showinfo("✓ Hợp lệ", "Đây là chuỗi LaTeX của tích phân!\n\n" + msg)
            self._set_status("✅ Chuỗi hợp lệ tích phân LaTeX")
        else:
            messagebox.showerror("Không hợp lệ", msg)
            self._set_status("❌ Chuỗi không phải tích phân LaTeX.")
    
    def _copy(self):
        latex = self.latex_entry.get().strip()
        if not latex:
            messagebox.showwarning("Cảnh báo", "Không có chuỗi để copy")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(latex)
        messagebox.showinfo("Thành công", "Đã copy chuỗi LaTeX vào clipboard!")
        self._set_status("Đã copy chuỗi LaTeX")
    
    def _clear(self):
        self.latex_entry.delete(0, tk.END)
        self.status_label.config(text="⚠️ UI LaTeX - Chưa kiểm tra")
        self._set_status("Đã xóa dữ liệu")
    
    def _set_status(self, text):
        self.status_label.config(text=text)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    IntegralView(root)
    root.mainloop()
