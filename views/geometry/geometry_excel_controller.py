"""Geometry View Components - Excel Controller"""
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import threading
import os
from datetime import datetime

class GeometryExcelController:
    """Quản lý các thao tác Excel"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
    
    def import_excel(self):
        """Chỉ chọn file và lưu lại TÊN FILE, KHÔNG đọc nội dung"""
        try:
            file_path = filedialog.askopenfilename(
                title="Chọn file Excel",
                filetypes=[("Excel files", "*.xlsx *.xls")]
            )
            
            if not file_path:
                return False
            
            # Kiểm tra extension
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in ['.xlsx', '.xls']:
                messagebox.showerror("Lỗi", "Chỉ hỗ trợ file Excel (.xlsx, .xls)!")
                return False
            
            # Kiểm tra file tồn tại
            if not os.path.exists(file_path):
                messagebox.showerror("Lỗi", "File không tồn tại!")
                return False
            
            # Cập nhật state manager
            file_name = os.path.basename(file_path)
            if hasattr(self.parent, 'state_manager'):
                self.parent.state_manager.set_import_mode(file_path, file_name)
            
            # Cập nhật Excel status
            if hasattr(self.parent, 'ui_manager'):
                self.parent.ui_manager.excel_status_label.config(text=f"Excel: 📁 {file_name[:15]}...")
            
            # Cập nhật result display
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            status_message = f"📁 Đã import file: {file_name}\n"
            
            if hasattr(self.parent, 'result_display'):
                self.parent.result_display.update_result_display(status_message)
            
            return True
        
        except Exception as e:
            messagebox.showerror("Lỗi Import", f"Lỗi import Excel: {str(e)}")
            return False
    
    def process_excel_batch(self):
        """Đọc và xử lý file Excel (chỉ đọc ở bước này)"""
        try:
            if not hasattr(self.parent, 'state_manager') or not self.parent.state_manager.is_import_mode():
                messagebox.showwarning("Cảnh báo", "Chưa import file Excel nào!")
                return
            
            if not hasattr(self.parent, 'service_adapter') or not self.parent.service_adapter.is_service_ready():
                messagebox.showerror("Lỗi", "GeometryService chưa sẵn sàng!")
                return
            
            import_info = self.parent.state_manager.get_import_info()
            file_path = import_info['file_path']
            file_name = import_info['file_name']
            
            # Kiểm tra file vẫn tồn tại
            if not os.path.exists(file_path):
                messagebox.showerror("Lỗi", f"File không tồn tại: {file_path}")
                return
            
            original_name = os.path.splitext(file_name)[0]
            default_output = f"{original_name}_encoded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            output_path = filedialog.asksaveasfilename(
                title="Chọn nơi lưu kết quả",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=default_output
            )
            if not output_path:
                return
            
            # Lấy setting hiện tại
            shape_a = self.parent.dropdown1_var.get()
            shape_b = self.parent.dropdown2_var.get() if hasattr(self.parent, 'operation_manager') and \
                     self.parent.operation_manager.needs_shape_B() else None
            operation = self.parent.pheptoan_var.get()
            dimension_a = self.parent.kich_thuoc_A_var.get()
            dimension_b = self.parent.kich_thuoc_B_var.get()
            
            # Tạo progress window
            progress_window = self._create_progress_window("Đang xử lý file Excel...")
            
            def progress_callback(progress, processed, total, errors):
                if hasattr(self, 'progress_var') and not self.parent.state_manager.processing_cancelled:
                    try:
                        self.progress_var.set(progress)
                        memory_usage = self.parent.memory_monitor.get_current_memory() if hasattr(self.parent, 'memory_monitor') else 0
                        progress_text = f"Đang xử lý: {processed:,}/{total:,} dòng"
                        self.progress_label.config(text=progress_text)
                        progress_window.update()
                    except Exception:
                        pass
            
            def process_thread():
                try:
                    results, output_file, success_count, error_count = self.parent.service_adapter.process_excel_batch(
                        file_path, shape_a, shape_b, operation,
                        dimension_a, dimension_b, output_path, progress_callback
                    )
                    
                    if not self.parent.state_manager.processing_cancelled:
                        progress_window.destroy()
                        
                        result_message = (
                            f"🎉 Hoàn thành xử lý Excel!\n\n"
                            f"📁 File gốc: {file_name}\n"
                            f"📁 Output: {os.path.basename(output_file)}\n"
                            f"✅ Success: {success_count:,} rows\n"
                            f"❌ Errors: {error_count:,} rows\n"
                            f"💾 Peak memory: {self.parent.memory_monitor.get_current_memory():.1f}MB\n\n"
                        )
                        if isinstance(results, list) and len(results) > 0:
                            result_message += f"📝 Sample result:\n{results[0][:80]}..."
                        else:
                            result_message += "📝 Results written directly to file for memory efficiency"
                        
                        if hasattr(self.parent, 'result_display'):
                            self.parent.result_display.update_result_display(result_message)
                        
                        messagebox.showinfo("Hoàn thành", 
                            f"🎉 Xử lý Excel thành công!\n\n"
                            f"✅ Processed: {success_count:,} rows\n"
                            f"❌ Errors: {error_count:,} rows\n\n"
                            f"File đã lưu:\n{output_file}")
                
                except Exception as e:
                    if not self.parent.state_manager.processing_cancelled:
                        progress_window.destroy()
                        messagebox.showerror("Lỗi Xử lý", f"Lỗi xử lý Excel: {str(e)}")
            
            # Start processing thread
            thread = threading.Thread(target=process_thread)
            thread.daemon = True
            thread.start()
        
        except Exception as e:
            messagebox.showerror("Lỗi Xử lý", f"Lỗi xử lý Excel: {str(e)}")
    
    def _create_progress_window(self, title):
        """Tạo cửa sổ progress dialog"""
        progress_window = tk.Toplevel(self.parent.window)
        progress_window.title(title)
        progress_window.geometry("450x180")
        progress_window.resizable(False, False)
        progress_window.grab_set()
        progress_window.transient(self.parent.window)
        
        tk.Label(progress_window, text=title, font=("Arial", 12, "bold")).pack(pady=10)
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            progress_window, variable=self.progress_var, 
            maximum=100, length=350, mode='determinate'
        )
        progress_bar.pack(pady=10)
        
        self.progress_label = tk.Label(progress_window, text="Chuẩn bị...", font=("Arial", 10))
        self.progress_label.pack(pady=5)
        
        warning_label = tk.Label(
            progress_window, 
            text="⚠️ Đừng đóng cửa sổ! Đang xử lý .",
            font=("Arial", 8), fg="#FF9800"
        )
        warning_label.pack(pady=5)
        
        def cancel_processing():
            self.parent.state_manager.set_processing_cancelled(True)
            messagebox.showinfo("Đã hủy", "Đã yêu cầu hủy xử lý. Vui lòng đợi...")
            progress_window.after(2000, progress_window.destroy)
        
        tk.Button(progress_window, text="🛑 Hủy", command=cancel_processing,
                 bg="#F44336", fg="white", font=("Arial", 10)).pack(pady=10)
        
        return progress_window
    
    def create_template(self):
        """Tạo Excel template"""
        try:
            shape_a = self.parent.dropdown1_var.get()
            shape_b = self.parent.dropdown2_var.get() if hasattr(self.parent, 'operation_manager') and \
                     self.parent.operation_manager.needs_shape_B() else None
            
            if not shape_a:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn hình dạng trước!")
                return
            
            template_name = f"template_{shape_a}" + (f"_{shape_b}" if shape_b else "") + f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            output_path = filedialog.asksaveasfilename(
                title="Lưu template Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=template_name
            )
            
            if not output_path:
                return
            
            if hasattr(self.parent, 'service_adapter'):
                template_file = self.parent.service_adapter.create_excel_template_for_geometry(shape_a, shape_b, output_path)
                
                messagebox.showinfo("Tạo template thành công", 
                    f"Template Excel đã tạo tại:\n{template_file}\n\n"
                    f"Bạn có thể điền dữ liệu vào template này rồi import lại.\n\n"
                    f"💡 Tip: Template hỗ trợ đến 250,000 dòng với anti-crash system!")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tạo template: {str(e)}")
    
    def quit_import_mode(self):
        """Thoát chế độ import và quay lại manual"""
        try:
            result = messagebox.askyesno("Thoát chế độ import", 
                "Bạn có chắc muốn thoát chế độ import Excel và quay lại nhập thủ công?")
            
            if result:
                # Reset state
                if hasattr(self.parent, 'state_manager'):
                    self.parent.state_manager.set_manual_mode()
                
                # Cập nhật UI
                if hasattr(self.parent, 'result_display'):
                    self.parent.result_display.show_single_line_result("")
                
                if hasattr(self.parent, 'ui_manager'):
                    self.parent.ui_manager.excel_status_label.config(text="📊 Excel: ✅ Ready")
        
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi thoát chế độ import: {str(e)}")