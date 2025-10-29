"""Geometry View Components - Operation Manager"""
import tkinter as tk

class GeometryOperationManager:
    """Quản lý phép toán và ảnh hưởng đến dropdown"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
        
        # Bind events cho phép toán
        self.parent.pheptoan_var.trace('w', self._on_operation_changed)
    
    def _get_available_operations(self):
        """Lấy danh sách phép toán"""
        if self.parent.geometry_service:
            return self.parent.geometry_service.get_available_operations()
        else:
            return ["Tuương giao", "Khoảng cách", "Diện tích", "Thể tích", "PT đường thẳng"]
    
    def initialize_operations(self):
        """Khởi tạo các phép toán"""
        operations = self._get_available_operations()
        
        # Cập nhật menu phép toán trong UI
        if hasattr(self.parent, 'ui_manager'):
            self.parent.ui_manager.update_operation_menu(operations)
        
        # Đặt phép toán mặc định
        if operations:
            self.parent.pheptoan_var.set(operations[0] if "Khoảng cách" not in operations else "Khoảng cách")
    
    def _on_operation_changed(self, *args):
        """Xử lý khi thay đổi phép toán"""
        operation = self.parent.pheptoan_var.get()
        if not operation:
            return
        
        try:
            # Cập nhật service
            if self.parent.geometry_service:
                self.parent.geometry_service.set_current_operation(operation)
                
                # Lấy available shapes theo phép toán
                available_shapes = self.parent.geometry_service.update_dropdown_options(operation)
                
                # Cập nhật dropdown options
                if hasattr(self.parent, 'ui_manager') and available_shapes:
                    self.parent.ui_manager.update_shape_dropdowns(available_shapes)
            
            # Ẩn/hiện dropdown B tùy theo phép toán
            self._update_dropdown_B_visibility(operation)
            
            # Cập nhật input frames
            if hasattr(self.parent, 'input_panels'):
                self.parent.input_panels.update_input_frames()
        
        except Exception as e:
            print(f"Warning: Error handling operation change: {e}")
    
    def _update_dropdown_B_visibility(self, operation):
        """Cập nhật hiển thị dropdown B theo phép toán"""
        # Phép toán chỉ cần 1 hình (không cần B)
        single_shape_operations = ["Diện tích", "Thể tích"]
        
        show_B = operation not in single_shape_operations
        
        # Cập nhật UI
        if hasattr(self.parent, 'ui_manager'):
            self.parent.ui_manager.show_hide_dropdown_B(show_B)
    
    def get_current_operation(self):
        """Lấy phép toán hiện tại"""
        return self.parent.pheptoan_var.get()
    
    def set_operation(self, operation):
        """Thiết lập phép toán"""
        if operation in self._get_available_operations():
            self.parent.pheptoan_var.set(operation)
    
    def needs_shape_B(self, operation=None):
        """Kiểm tra xem phép toán có cần hình B không"""
        if operation is None:
            operation = self.get_current_operation()
        
        single_shape_operations = ["Diện tích", "Thể tích"]
        return operation not in single_shape_operations