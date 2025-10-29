"""Equation View Components - Button Manager"""
import tkinter as tk
from tkinter import messagebox

class EquationButtonManager:
    """Quản lý các nút chức năng và trạng thái"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
        self.buttons = {}
    
    def create_buttons(self, button_frame):
        """Tạo các nút chức năng"""
        # Nút Import Excel (ban đầu hiển thị)
        self.buttons['import'] = tk.Button(
            button_frame,
            text="📁 Import Excel",
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            width=14,
            height=1,
            command=self._import_excel
        )
        self.buttons['import'].pack(side="left", padx=5)
        
        # Nút Xử lý (luôn hiển thị)
        self.buttons['process'] = tk.Button(
            button_frame,
            text="🔄 Xử lý & Giải nghiệm",
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            width=16,
            height=1,
            command=self._process_equations
        )
        self.buttons['process'].pack(side="left", padx=5)
        
        # Nút Import File Excel Khác (ban đầu ẩn)
        self.buttons['import_other'] = tk.Button(
            button_frame,
            text="📂 Import File Khác",
            bg="#9C27B0",
            fg="white",
            font=("Arial", 10, "bold"),
            width=14,
            height=1,
            command=self._import_other_excel
        )
        
        # Nút Quay lại (ban đầu ẩn)
        self.buttons['back'] = tk.Button(
            button_frame,
            text="↩️ Quay lại",
            bg="#607D8B",
            fg="white",
            font=("Arial", 10, "bold"),
            width=14,
            height=1,
            command=self._back_to_manual
        )
        
        # Nút Export Excel
        self.buttons['export'] = tk.Button(
            button_frame,
            text="💾 Export Excel",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=14,
            height=1,
            command=self._export_excel
        )
        
        # Nút Copy Kết quả
        self.buttons['copy'] = tk.Button(
            button_frame,
            text="📋 Copy Kết quả",
            bg="#FF5722",
            fg="white",
            font=("Arial", 10, "bold"),
            width=14,
            height=1,
            command=self._copy_result
        )
    
    def update_button_visibility(self):
        """Cập nhật hiển thị nút dựa trên trạng thái"""
        # Ẩn tất cả các nút trước
        for button_name, button in self.buttons.items():
            if button_name != 'process':  # Nút process luôn hiển thị
                button.pack_forget()
        
        if self.parent.is_imported_mode:
            # Trạng thái import từ Excel
            self.buttons['import_other'].pack(side="left", padx=5)
            self.buttons['back'].pack(side="left", padx=5)
            self.buttons['process'].pack(side="left", padx=5)
            self.buttons['export'].pack(side="left", padx=5)
        elif self.parent.has_manual_data:
            # Trạng thái nhập liệu thủ công
            self.buttons['process'].pack(side="left", padx=5)
            self.buttons['export'].pack(side="left", padx=5)
            self.buttons['copy'].pack(side="left", padx=5)
        else:
            # Trạng thái ban đầu
            self.buttons['import'].pack(side="left", padx=5)
            self.buttons['process'].pack(side="left", padx=5)
    
    def _import_excel(self):
        """Xử lý import Excel"""
        try:
            messagebox.showinfo("Thông báo", "Chức năng Import Excel đang phát triển!\n\nSẽ tích hợp với Excel processor tương tự Geometry mode.")
            
            # Placeholder logic - sẽ thay thế bằng Excel service
            self.parent.is_imported_mode = True
            self.parent.has_manual_data = False
            self.update_button_visibility()
            
            # Cập nhật trạng thái
            if hasattr(self.parent, 'status_label'):
                self.parent.status_label.config(
                    text="📁 Đã import dữ liệu từ Excel - Sẵn sàng xử lý",
                    fg="#1565C0"
                )
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi import Excel: {str(e)}")
    
    def _import_other_excel(self):
        """Xử lý import file Excel khác"""
        self._import_excel()  # Tạm thời dùng chức năng giống nhau
    
    def _process_equations(self):
        """Xử lý giải hệ phương trình"""
        try:
            messagebox.showinfo("Thông báo", "Chức năng giải phương trình đang phát triển!\n\nSẽ tích hợp:\n- Equation Service\n- Matrix solver\n- Encoding logic")
            
            # Placeholder - hiển thị kết quả mẫu
            if hasattr(self.parent, 'input_handler'):
                input_data = self.parent.input_handler.get_input_data()
                if any(data.strip() for data in input_data):
                    # Giả lập xử lý thành công
                    if hasattr(self.parent, 'result_handler'):
                        # Kết quả mã hóa mẫu
                        sample_results = ["0.5", "1.2", "3.0", "-2.1", "0.8", "4.5"]
                        self.parent.result_handler.update_results(sample_results)
                        
                        # Kết quả nghiệm mẫu
                        sample_solutions = {"x": "2.5", "y": "-1.3"}
                        if hasattr(self.parent, 'solution_entry'):
                            self.parent.result_handler.update_solution_display(
                                self.parent.solution_entry, sample_solutions
                            )
                        
                        # Kết quả tổng mẫu
                        encoded_string = ",".join(sample_results)
                        if hasattr(self.parent, 'final_entry'):
                            self.parent.result_handler.update_final_result(
                                self.parent.final_entry, encoded_string, 
                                {"version": self.parent.phien_ban_var.get()}
                            )
                    
                    # Cập nhật trạng thái
                    if hasattr(self.parent, 'status_label'):
                        self.parent.status_label.config(
                            text="✅ Đã giải xong hệ phương trình - Kết quả hiển thị phía trên",
                            fg="#2E7D32"
                        )
                else:
                    messagebox.showwarning("Cảnh báo", "Vui lòng nhập hệ số phương trình trước!")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý: {str(e)}")
    
    def _back_to_manual(self):
        """Quay lại chế độ nhập thủ công"""
        try:
            result = messagebox.askyesno(
                "Xác nhận", 
                "Bạn có chắc muốn quay lại chế độ nhập thủ công?\n\nDữ liệu hiện tại sẽ bị xóa."
            )
            
            if result:
                # Reset trạng thái
                self.parent.is_imported_mode = False
                self.parent.has_manual_data = False
                
                # Xóa dữ liệu nhập
                if hasattr(self.parent, 'input_handler'):
                    self.parent.input_handler.clear_inputs()
                    self.parent.input_handler.unlock_inputs()
                
                # Xóa kết quả
                if hasattr(self.parent, 'result_handler'):
                    self.parent.result_handler.clear_results()
                
                # Cập nhật hiển thị nút
                self.update_button_visibility()
                
                # Cập nhật trạng thái
                if hasattr(self.parent, 'status_label'):
                    self.parent.status_label.config(
                        text="🟢 Đã quay lại chế độ nhập thủ công",
                        fg="#2E7D32"
                    )
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi quay lại: {str(e)}")
    
    def _export_excel(self):
        """Xuất kết quả ra Excel"""
        try:
            messagebox.showinfo("Thông báo", "Chức năng Export Excel đang phát triển!\n\nSẽ xuất:\n- Kết quả mã hóa\n- Nghiệm phương trình\n- Mẫu template")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xuất Excel: {str(e)}")
    
    def _copy_result(self):
        """Copy kết quả vào clipboard"""
        try:
            if hasattr(self.parent, 'result_handler'):
                encoded_string = self.parent.result_handler.get_encoded_string()
                if encoded_string:
                    # Copy vào clipboard
                    self.parent.window.clipboard_clear()
                    self.parent.window.clipboard_append(encoded_string)
                    
                    messagebox.showinfo(
                        "Đã copy", 
                        f"Đã copy kết quả vào clipboard:\n\n{encoded_string[:50]}{'...' if len(encoded_string) > 50 else ''}"
                    )
                else:
                    messagebox.showwarning("Cảnh báo", "Chưa có kết quả để copy!")
            else:
                messagebox.showwarning("Cảnh báo", "Không thể truy cập kết quả!")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi copy kết quả: {str(e)}")
    
    def enable_button(self, button_name):
        """Kích hoạt nút"""
        if button_name in self.buttons:
            self.buttons[button_name].config(state='normal')
    
    def disable_button(self, button_name):
        """Vô hiệu hóa nút"""
        if button_name in self.buttons:
            self.buttons[button_name].config(state='disabled')
    
    def get_button(self, button_name):
        """Lấy tham chiếu đến nút"""
        return self.buttons.get(button_name)