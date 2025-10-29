"""Geometry View Components - Service Adapter"""

class GeometryServiceAdapter:
    """Bọc GeometryService và các method chính"""
    
    def __init__(self, parent_view):
        self.parent = parent_view
        self.geometry_service = parent_view.geometry_service
    
    def initialize_service(self):
        """Khởi tạo GeometryService"""
        try:
            from services.geometry.geometry_service import GeometryService
            self.geometry_service = GeometryService(self.parent.config)
            self.parent.geometry_service = self.geometry_service
            return True
        except Exception as e:
            print(f"Warning: Could not initialize GeometryService: {e}")
            return False
    
    def set_current_operation(self, operation):
        """Thiết lập phép toán hiện tại"""
        if self.geometry_service:
            self.geometry_service.set_current_operation(operation)
    
    def set_current_shapes(self, shape_a, shape_b=None):
        """Thiết lập hình dạng hiện tại"""
        if self.geometry_service:
            self.geometry_service.set_current_shapes(shape_a, shape_b)
    
    def set_kich_thuoc(self, dimension_a, dimension_b):
        """Thiết lập kích thước"""
        if self.geometry_service:
            self.geometry_service.set_kich_thuoc(dimension_a, dimension_b)
    
    def thuc_thi_A(self, data_a):
        """Thực thi nhóm A"""
        if self.geometry_service:
            return self.geometry_service.thuc_thi_A(data_a)
        return None
    
    def thuc_thi_B(self, data_b):
        """Thực thi nhóm B"""
        if self.geometry_service:
            return self.geometry_service.thuc_thi_B(data_b)
        return None
    
    def thuc_thi_tat_ca(self, data_a, data_b):
        """Thực thi tất cả"""
        if self.geometry_service:
            return self.geometry_service.thuc_thi_tat_ca(data_a, data_b)
        return None, None
    
    def generate_final_result(self):
        """Sinh kết quả cuối cùng"""
        if self.geometry_service:
            return self.geometry_service.generate_final_result()
        return None
    
    def export_single_result(self, output_path):
        """Xuất kết quả đơn"""
        if self.geometry_service:
            return self.geometry_service.export_single_result(output_path)
        return None
    
    def process_excel_batch(self, input_path, shape_a, shape_b, operation, dimension_a, dimension_b, output_path, progress_callback):
        """Xử lý batch Excel"""
        if self.geometry_service:
            return self.geometry_service.process_excel_batch(
                input_path, shape_a, shape_b, operation, 
                dimension_a, dimension_b, output_path, progress_callback
            )
        return None, None, 0, 0
    
    def create_excel_template_for_geometry(self, shape_a, shape_b, output_path):
        """Tạo template Excel"""
        if self.geometry_service:
            return self.geometry_service.create_excel_template_for_geometry(shape_a, shape_b, output_path)
        return None
    
    def get_available_operations(self):
        """Lấy các phép toán khả dụng"""
        if self.geometry_service:
            return self.geometry_service.get_available_operations()
        return ["Tuương giao", "Khoảng cách", "Diện tích", "Thể tích", "PT đường thẳng"]
    
    def get_available_shapes(self):
        """Lấy các hình dạng khả dụng"""
        if self.geometry_service:
            return self.geometry_service.get_available_shapes()
        return ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"]
    
    def update_dropdown_options(self, operation):
        """Cập nhật tùy chọn dropdown theo phép toán"""
        if self.geometry_service:
            return self.geometry_service.update_dropdown_options(operation)
        return self.get_available_shapes()
    
    def is_service_ready(self):
        """Kiểm tra xem service có sẵn sàng không"""
        return self.geometry_service is not None