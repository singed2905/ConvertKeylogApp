"""Geometry View Components - State Manager"""
import tkinter as tk
from tkinter import messagebox

class GeometryStateManager:
    """Quản lý trạng thái cho Geometry View"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
        
        # Excel processing state
        self.imported_data = False
        self.imported_file_path = ""
        self.imported_file_name = ""  # Store only file name after import
        self.manual_data_entered = False
        self.processing_cancelled = False
        self.is_large_file = False  # Track if current file is large
        self.has_result = False  # Track if manual result is available
    
    def set_import_mode(self, file_path, file_name):
        """Thiết lập chế độ import"""
        self.imported_data = True
        self.imported_file_path = file_path
        self.imported_file_name = file_name
        self.manual_data_entered = False
        self.is_large_file = False  # Will be detected during processing
        
        # Clear và khóa inputs
        self._clear_and_lock_inputs()
        
        # Hiện thị import buttons
        self._show_import_buttons()
        
        # Ẩn nút copy vì đang ở import mode
        if hasattr(self.parent, 'result_display'):
            self.parent.result_display.hide_copy_button()
    
    def set_manual_mode(self):
        """Thiết lập chế độ thủ công"""
        self.imported_data = False
        self.imported_file_path = ""
        self.imported_file_name = ""
        self.manual_data_entered = False
        self.is_large_file = False
        
        # Mở khóa và clear inputs
        self._unlock_and_clear_inputs()
        
        # Ẩn tất cả action buttons
        self._hide_action_buttons()
        
        # Ẩn nút copy
        if hasattr(self.parent, 'result_display'):
            self.parent.result_display.hide_copy_button()
    
    def set_manual_data_entered(self, has_data):
        """Cập nhật trạng thái nhập dữ liệu thủ công"""
        if self.imported_data:
            # Không cho phép nhập thủ công khi đã import
            return False
        
        if has_data and not self.manual_data_entered:
            self.manual_data_entered = True
            self._show_manual_buttons()
            return True
        elif not has_data and self.manual_data_entered:
            self.manual_data_entered = False
            self._hide_action_buttons()
            # Ẩn copy button khi clear dữ liệu
            if hasattr(self.parent, 'result_display'):
                self.parent.result_display.hide_copy_button()
            return True
        
        return False
    
    def set_has_result(self, has_result):
        """Cập nhật trạng thái có kết quả"""
        self.has_result = has_result
        
        # Hiện/ẩn nút copy tương ứng
        if hasattr(self.parent, 'result_display'):
            if has_result and not self.imported_data:  # Chỉ hiện cho manual mode
                self.parent.result_display.show_copy_button()
            else:
                self.parent.result_display.hide_copy_button()
    
    def set_processing_cancelled(self, cancelled=True):
        """Thiết lập trạng thái hủy xử lý"""
        self.processing_cancelled = cancelled
    
    def _get_all_input_entries(self):
        """Lấy tất cả input entry widgets"""
        entries = []
        
        # Collect all entry widgets
        for attr_name in dir(self.parent):
            if attr_name.startswith('entry_') and hasattr(self.parent, attr_name):
                entry = getattr(self.parent, attr_name)
                if hasattr(entry, 'get'):  # It's an Entry widget
                    entries.append(entry)
        
        return entries
    
    def _clear_and_lock_inputs(self):
        """Clear và khóa tất cả input fields khi Excel được import"""
        entries = self._get_all_input_entries()
        for entry in entries:
            try:
                entry.delete(0, tk.END)
                entry.config(state='disabled', bg='#E0E0E0')
            except:
                pass
    
    def _unlock_and_clear_inputs(self):
        """Mở khóa và clear tất cả input fields cho nhập thủ công"""
        entries = self._get_all_input_entries()
        for entry in entries:
            try:
                entry.config(state='normal', bg='white')
                entry.delete(0, tk.END)
            except:
                pass
    
    def _show_manual_buttons(self):
        """Hiện thị buttons cho chế độ thủ công"""
        if hasattr(self.parent, 'frame_buttons_manual'):
            self.parent.frame_buttons_manual.grid()
        if hasattr(self.parent, 'frame_buttons_import'):
            self.parent.frame_buttons_import.grid_remove()
    
    def _show_import_buttons(self):
        """Hiện thị buttons cho chế độ import"""
        if hasattr(self.parent, 'frame_buttons_import'):
            self.parent.frame_buttons_import.grid()
        if hasattr(self.parent, 'frame_buttons_manual'):
            self.parent.frame_buttons_manual.grid_remove()
    
    def _hide_action_buttons(self):
        """Chẻ̂ giấu tất cả̂ action buttons"""
        if hasattr(self.parent, 'frame_buttons_manual'):
            self.parent.frame_buttons_manual.grid_remove()
        if hasattr(self.parent, 'frame_buttons_import'):
            self.parent.frame_buttons_import.grid_remove()
    
    def check_manual_data(self):
        """Kiểm tra xem có dữ liệu thủ công được nhập không"""
        entries = self._get_all_input_entries()
        for entry in entries:
            try:
                if entry.get().strip():
                    return True
            except:
                pass
        return False
    
    def on_input_data_changed(self, event):
        """Xử lý khi dữ liệu nhập thay đổi"""
        if self.imported_data:
            messagebox.showerror("Đã import Excel", "Đã import Excel, không thể nhập dữ liệu thủ công!")
            event.widget.delete(0, tk.END)
            return
        
        has_data = self.check_manual_data()
        self.set_manual_data_entered(has_data)
    
    def is_import_mode(self):
        """Kiểm tra xem có đang ở chế độ import không"""
        return self.imported_data
    
    def is_manual_mode(self):
        """Kiểm tra xem có đang ở chế độ thủ công không"""
        return not self.imported_data and self.manual_data_entered
    
    def get_import_info(self):
        """Lấy thông tin file import"""
        return {
            'file_path': self.imported_file_path,
            'file_name': self.imported_file_name,
            'is_large_file': self.is_large_file
        }
    
    def reset_state(self):
        """Reset toàn bộ trạng thái"""
        self.imported_data = False
        self.imported_file_path = ""
        self.imported_file_name = ""
        self.manual_data_entered = False
        self.processing_cancelled = False
        self.is_large_file = False
        self.has_result = False
        
        # Mở khóa và clear inputs
        self._unlock_and_clear_inputs()
        
        # Ẩn tất cả buttons
        self._hide_action_buttons()
        
        # Ẩn copy button
        if hasattr(self.parent, 'result_display'):
            self.parent.result_display.hide_copy_button()