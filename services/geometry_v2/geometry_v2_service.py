"""
Geometry V2 Service - Core Service
Xử lý 7 shapes, 10 operations
"""

class GeometryV2Service:
    def __init__(self, config=None):
        self.config = config or {}
        self.current_operation = None
        self.current_shape_a = None
        self.current_shape_b = None
        self.dimension_a = "3"
        self.dimension_b = "3"
        self.version = "fx799"

        # Khởi tạo encoder
        self._init_encoder()

    def _init_encoder(self):
        """Khởi tạo encoder"""
        try:
            from .geometry_encoder import GeometryEncoder
            self.encoder = GeometryEncoder(self.config)
        except Exception as e:
            print(f"⚠️ Warning: Could not init encoder: {e}")
            self.encoder = None

    # ========== CONFIGURATION ==========
    def set_dimension(self, dim_a, dim_b):
        """Set kích thước cho nhóm A và B"""
        self.dimension_a = str(dim_a)
        self.dimension_b = str(dim_b)

    def set_operation(self, operation):
        """Set phép toán hiện tại"""
        self.current_operation = operation

    def set_shapes(self, shape_a, shape_b=None):
        """Set shapes hiện tại"""
        self.current_shape_a = shape_a
        self.current_shape_b = shape_b

    def set_version(self, version):
        """Set phiên bản máy tính"""
        self.version = version

    # ========== AVAILABLE OPTIONS ==========
    def get_available_operations(self):
        """Trả về danh sách phép toán"""
        if self.encoder:
            return list(self.encoder.operation_codes.keys())
        return [
            "Tương giao", "Khoảng cách", "Diện tích", "Thể tích",
            "PT đường thẳng", "PT mặt phẳng", "Góc",
            "Tích vô hướng 2 vecto", "Vecto đơn vị", "Phép tính tam giác"
        ]

    def get_available_shapes(self):
        """Trả về danh sách shapes"""
        if self.encoder:
            return list(self.encoder.shape_codes.keys())
        return [
            "Điểm", "Vecto", "Đường thẳng", "Mặt phẳng",
            "Đường tròn", "Mặt cầu", "Tam giác"
        ]

    # ========== MANUAL PROCESSING ==========
    def process_manual_data(self, data_a, data_b=None):

        try:
            if not self.encoder:
                return {
                    'success': False,
                    'error': 'Encoder chưa khởi tạo'
                }

            # Validate input
            validation_a = self.encoder.validate_data(self.current_shape_a, data_a)
            if not validation_a['valid']:
                return {
                    'success': False,
                    'error': validation_a['error']
                }

            if self.current_shape_b and data_b:
                validation_b = self.encoder.validate_data(self.current_shape_b, data_b)
                if not validation_b['valid']:
                    return {
                        'success': False,
                        'error': validation_b['error']
                    }

            # Encode
            encoded = self.encoder.encode(
                operation=self.current_operation,
                shape_a=self.current_shape_a,
                shape_b=self.current_shape_b,
                data_a=data_a,
                data_b=data_b,
                version=self.version
            )

            return {
                'success': True,
                'encoded': encoded
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Lỗi encode: {str(e)}'
            }

    def encode_manual_data(self, data_a, data_b=None):
        """Alias for process_manual_data (backward compatibility)"""
        return self.process_manual_data(data_a, data_b)
