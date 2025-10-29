"""Geometry View Components - Result Display"""
import tkinter as tk
from tkinter import messagebox

class GeometryResultDisplay:
    """Quản lý hiển thị kết quả và copy clipboard"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
        self.entry_tong = None
        self.btn_copy_result = None
    
    def setup_result_display(self, main_container, entry_tong):
        """Thiết lập hiển thị kết quả"""
        self.entry_tong = entry_tong
        
        # Tạo nút copy kết quả (ẩn ban đầu)
        self.btn_copy_result = tk.Button(
            main_container, text="📋 Copy Kết Quả",
            command=self._copy_result,
            bg="#9C27B0", fg="white", font=("Arial", 9, "bold"),
            width=20
        )
        self.btn_copy_result.grid(row=10, column=0, sticky="w", padx=0, pady=5)
        self.btn_copy_result.grid_remove()  # Ẩn ban đầu
    
    def show_single_line_result(self, result_text: str):
        """Hiển thị duy nhất 1 dòng kết quả mã hóa với font Flexio Fx799VN"""
        if not self.entry_tong:
            return
        
        # Xóa toàn bộ và chèn đúng 1 dòng
        self.entry_tong.delete(1.0, tk.END)
        one_line = (result_text or "").strip().splitlines()[0] if result_text else ""
        self.entry_tong.insert(tk.END, one_line)
        
        # Thiết lập font Flexio Fx799VN nếu có, size 11, bold
        try:
            self.entry_tong.config(font=("Flexio Fx799VN", 11, "bold"), fg="#000000", bg="#F8F9FA")
        except Exception:
            # Fallback giữ nguyên nếu font không có
            self.entry_tong.config(font=("Courier New", 11, "bold"), fg="#000000", bg="#F8F9FA")
    
    def update_result_display(self, message):
        """Cập nhật hiển thị kết quả với màu sắc (dùng cho thông báo nhiều dòng)"""
        if not self.entry_tong:
            return
        
        self.entry_tong.delete(1.0, tk.END)
        self.entry_tong.insert(tk.END, message)
        
        # Giữ font mặc định cho thông báo
        try:
            self.entry_tong.config(font=("Courier New", 9), fg="black")
        except Exception:
            pass
        
        # Màu sắc theo loại thông báo
        if "Lỗi" in message or "lỗi" in message:
            self.entry_tong.config(bg="#FFEBEE", fg="#D32F2F")
        elif "Đã import" in message or "Hoàn thành" in message:
            self.entry_tong.config(bg="#E8F5E8", fg="#388E3C")
        elif "Đang xử lý" in message:
            self.entry_tong.config(bg="#FFF3E0", fg="#F57C00")
        else:
            self.entry_tong.config(bg="#F8F9FA", fg="#2E86AB")
    
    def show_ready_message(self):
        """Hiển thông báo sẵn sàng"""
        if not self.entry_tong:
            return
        
        if self.parent.geometry_service:
            message = " "
        else:
            message = "⚠️ GeometryService không khởi tạo được.\nVui lòng kiểm tra cài đặt!"
        
        self.entry_tong.insert(tk.END, message)
    
    def _copy_result(self):
        """Copy kết quả mã hóa vào clipboard"""
        try:
            if not self.entry_tong:
                messagebox.showwarning("Cảnh báo", "Không có kết quả để copy!")
                return
            
            result_text = self.entry_tong.get(1.0, tk.END).strip()
            if result_text:
                self.parent.window.clipboard_clear()
                self.parent.window.clipboard_append(result_text)
                messagebox.showinfo("Đã copy", f"Đã copy kết quả vào clipboard:\n\n{result_text}")
            else:
                messagebox.showwarning("Cảnh báo", "Không có kết quả để copy!")
        except Exception as e:
            messagebox.showerror("Lỗi Copy", f"Lỗi copy kết quả: {str(e)}")
    
    def show_copy_button(self):
        """Hiện thị nút copy khi có kết quả"""
        if self.btn_copy_result:
            self.btn_copy_result.grid()
    
    def hide_copy_button(self):
        """An nút copy khi không có kết quả"""
        if self.btn_copy_result:
            self.btn_copy_result.grid_remove()
    
    def clear_display(self):
        """Xóa hiển thị"""
        if self.entry_tong:
            self.entry_tong.delete(1.0, tk.END)