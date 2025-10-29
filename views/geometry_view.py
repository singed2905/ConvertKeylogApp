import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
import threading
import os
from datetime import datetime
import psutil

class GeometryView:
    def __init__(self, window, config=None):
        self.window = window
        self.window.title("Geometry Mode - Anti-Crash Excel! 💪")
        self.window.geometry("900x900")
        self.window.configure(bg="#F8F9FA")

        # Lưu config được truyền vào
        self.config = config or {}
        
        # Import và khởi tạo GeometryService (lazy loading)
        self.geometry_service = None
        self._initialize_service()
        
        # Excel processing state
        self.imported_data = False
        self.imported_file_path = ""
        self.imported_file_name = ""  # NEW: store only file name after import
        self.manual_data_entered = False
        self.processing_cancelled = False
        self.is_large_file = False  # Track if current file is large
        
        # Biến và trạng thái
        self._initialize_variables()
        self._setup_ui()
        
        # Đảm bảo hiển thị đúng ngay lần đầu
        self._on_operation_changed()
        self._on_shape_changed()

    def _initialize_service(self):
        """Khởi tạo GeometryService"""
        try:
            from services.geometry.geometry_service import GeometryService
            self.geometry_service = GeometryService(self.config)
        except Exception as e:
            print(f"Warning: Could not initialize GeometryService: {e}")
            self.geometry_service = None

    # ... (no changes to other helper methods above)

    # ========== ENHANCED EXCEL METHODS - IMPORT ONLY FILENAME ==========
    def _import_excel(self):
        """Chỉ chọn file và lưu lại TÊN FILE, KHÔNG đọc/validate nội dung ở bước import"""
        try:
            file_path = filedialog.askopenfilename(
                title="Chọn file Excel",
                filetypes=[("Excel files", "*.xlsx *.xls")]
            )
            
            if not file_path:
                return
            
            # Lưu chỉ thông tin tên file, không đọc file ở bước này
            self.imported_file_path = file_path
            self.imported_file_name = os.path.basename(file_path)
            self.imported_data = True
            self.manual_data_entered = False
            
            # Clear manual inputs and lock them
            self._clear_and_lock_inputs()
            
            # Show import buttons only
            self._show_import_buttons()
            
            # Cập nhật status đơn giản (chỉ tên file)
            status_message = (
                f"📁 Đã import file: {self.imported_file_name}\n"
                f"⚠️ Lưu ý: Chưa đọc nội dung file. Việc đọc và xử lý sẽ thực hiện ở bước 'Xử lý File Excel'."
            )
            self.excel_status_label.config(text=f"Excel: 📁 {self.imported_file_name[:15]}...")
            self._update_result_display(status_message)
        
        except Exception as e:
            messagebox.showerror("Lỗi Import", f"Lỗi import Excel: {str(e)}")

    def _process_excel_batch(self):
        """Đọc và xử lý file Excel SAU khi đã import (chỉ đọc ở bước này)"""
        try:
            if not self.imported_data or not self.imported_file_path:
                messagebox.showwarning("Cảnh báo", "Chưa import file Excel nào!")
                return
            
            if not self.geometry_service:
                messagebox.showerror("Lỗi", "GeometryService chưa sẵn sàng!")
                return
            
            # Hỏi lưu output trước khi đọc file
            original_name = os.path.splitext(os.path.basename(self.imported_file_path))[0]
            default_output = f"{original_name}_encoded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            output_path = filedialog.asksaveasfilename(
                title="Chọn nơi lưu kết quả",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialvalue=default_output
            )
            if not output_path:
                return
            
            # Lấy setting hiện tại
            shape_a = self.dropdown1_var.get()
            shape_b = self.dropdown2_var.get() if self.pheptoan_var.get() not in ["Diện tích", "Thể tích"] else None
            operation = self.pheptoan_var.get()
            dimension_a = self.kich_thuoc_A_var.get()
            dimension_b = self.kich_thuoc_B_var.get()
            
            # Tạo progress window
            progress_window = self._create_large_file_progress_window()
            
            def progress_callback(progress, processed, total, errors):
                if hasattr(self, 'progress_var') and not self.processing_cancelled:
                    try:
                        self.progress_var.set(progress)
                        memory_usage = self._get_memory_usage()
                        progress_text = f"Đang xử lý: {processed:,}/{total:,} dòng\nLỗi: {errors:,}\nMemory: {memory_usage:.1f}MB"
                        self.progress_label.config(text=progress_text)
                        progress_window.update()
                    except Exception:
                        pass
            
            def process_thread():
                try:
                    # CHỈ đọc và validate tại đây qua service (auto-detect large/normal bên dưới)
                    results, output_file, success_count, error_count = self.geometry_service.process_excel_batch(
                        self.imported_file_path, shape_a, shape_b, operation,
                        dimension_a, dimension_b, output_path, progress_callback
                    )
                    
                    if not self.processing_cancelled:
                        progress_window.destroy()
                        result_message = (
                            f"🎉 Hoàn thành xử lý Excel!\n\n"
                            f"📁 Output: {os.path.basename(output_file)}\n"
                            f"✅ Success: {success_count:,} rows\n"
                            f"❌ Errors: {error_count:,} rows\n"
                        )
                        self._update_result_display(result_message)
                        messagebox.showinfo("Hoàn thành", f"Xử lý thành công!\n\nFile đã lưu: {output_file}")
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("Lỗi Xử lý", f"Lỗi xử lý Excel: {str(e)}")
            
            thread = threading.Thread(target=process_thread)
            thread.daemon = True
            thread.start()
        
        except Exception as e:
            messagebox.showerror("Lỗi Xử lý", f"Lỗi xử lý Excel: {str(e)}")

    # ... (rest of the file remains unchanged)
