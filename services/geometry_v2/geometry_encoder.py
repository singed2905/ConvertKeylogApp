"""
Geometry V2 Encoder - Mã hóa keylog cho máy Casio
Sử dụng expression_encoding.json để encode biểu thức
"""
import json
import os
import re
from typing import Dict, Any, Optional, List

class GeometryEncoder:
    def __init__(self, config=None):
        self.config = config or {}
        current_file = os.path.abspath(__file__)  # Đường dẫn file hiện tại
        current_dir = os.path.dirname(current_file)  # services/geometry_v2/
        parent_dir = os.path.dirname(current_dir)  # services/
        root_dir = os.path.dirname(parent_dir)  # ConvertKeylogApp/

        self.config_dir = os.path.join(root_dir, 'config', 'geometry_v2_mode')

        # Debug: In ra để kiểm tra
        print(f"🔍 Current file: {current_file}")
        print(f"🔍 Root directory: {root_dir}")
        print(f"🔍 Config directory: {self.config_dir}")
        print(f"🔍 Config dir exists: {os.path.exists(self.config_dir)}")

        # Load configs
        self.shape_codes = self._load_json('shape_codes.json')
        self.operation_codes = self._load_json('operation_codes.json')
        self.expression_mappings = self._load_json('expression_encoding.json')

        # Parse mappings
        self._parse_mappings()

        print("✅ GeometryEncoder initialized with expression mappings!")

    def _load_json(self, filename):
        """Load JSON config file"""
        try:
            filepath = os.path.join(self.config_dir, filename)


            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    return data
            else:

                # List files in config dir để debug
                if os.path.exists(self.config_dir):
                    files = os.listdir(self.config_dir)
                    print(f"   Files in config dir: {files}")
                return {}
        except Exception as e:
            print(f"⚠️ Warning: Could not load {filename}: {e}")
            return {}

    def _parse_mappings(self):
        """Parse mappings thành regex và literal lists"""
        self.regex_mappings = []
        self.literal_mappings = []

        mappings = self.expression_mappings.get('mappings', [])

        for mapping in mappings:
            if mapping.get('type') == 'regex':
                self.regex_mappings.append({
                    'pattern': re.compile(mapping['find']),
                    'replace': mapping['replace'],
                    'description': mapping.get('description', '')
                })
            elif mapping.get('type') == 'literal':
                self.literal_mappings.append({
                    'find': mapping['find'],
                    'replace': mapping['replace'],
                    'description': mapping.get('description', '')
                })



    # ========== MAIN ENCODE METHOD ==========
    def encode(self, operation, shape_a, shape_b, data_a, data_b, version="fx799"):
        try:
            op_config = self.operation_codes.get(operation, {})
            requires_two = op_config.get('requires_two_shapes', False)
            base_op_code = op_config.get('code', 'qT0')

            prefix = "wj"

            # ========== NHÓM A ==========

            # ✅ code_a_short: FIX CỨNG = "a1"
            code_a_short = self._get_shape_code_short('a',shape_a)

            # ✅ code_a_full: phụ thuộc vào operation + shape
            code_a_full = self._get_shape_code_custom(operation, 'a', shape_a)

            # Encode data A
            data_a_encoded = self._encode_shape(shape_a, data_a)

            if requires_two and shape_b and data_b:
                # ========== NHÓM B ==========

                # ✅ code_b_short: FIX CỨNG = "b2"
                code_b_short = self._get_shape_code_short('b', shape_b)

                # ✅ code_b_full: phụ thuộc vào operation + shape
                code_b_full = self._get_shape_code_custom(operation, 'b', shape_b)

                # Encode data B
                data_b_encoded = self._encode_shape(shape_b, data_b)

                # Op code = base_op + code_a_full + code_b_full
                op_code = f"{base_op_code}{code_a_full}R{code_b_full}"

                # Keylog: dùng code_a_short (a1) và code_b_short (b2)
                keylog = f"{prefix}{code_a_short}{data_a_encoded}C{prefix}{code_b_short}{data_b_encoded}C{op_code}= ="
            else:
                # Op code = base_op + code_a_full
                op_code = f"{base_op_code}{code_a_full}"

                # Keylog: dùng code_a_short (a1)
                keylog = f"{prefix}{code_a_short}{data_a_encoded}C{op_code}= ="

            return keylog
        except Exception as e:
            return {
                'success': False,
                'error': f"ERROR_ENCODE: {str(e)}"
            }

    def _get_shape_code_short(self, group, shape):
        order = 0
        if shape == 'Điểm':
            order = 1
        if shape == 'Vecto':
            order = 2
        if shape == 'Đường thẳng':
            order = 3
        if shape == 'Mặt phẳng':
            order = 4
        if shape == 'Đường tròn':
            order = 5
        if shape == 'Mặt cầu':
            order = 6
        if shape == 'Tam giác':
            order = 7

        if group == 'a':
            return f"{order}1"
        if group == 'b':
            return f"{order}2"

        return "0"

    def _get_shape_code_custom(self, operation, group, shape):

        # ===== TƯƠNG GIAO =====
        if operation == "Tương giao":
            if group == 'a':
                if shape == "Điểm": return "T1"
                if shape == "Vecto": return "T5"
                if shape == "Đường thẳng": return "Tz"
                if shape == "Mặt phẳng": return "Tl"
                if shape == "Đường tròn": return "TR1"
                if shape == "Mặt cầu": return "TR5"
            if group == 'b':
                if shape == "Điểm": return "T2"
                if shape == "Vecto": return "T6"
                if shape == "Đường thẳng": return "Tx"
                if shape == "Mặt phẳng": return "Tm"
                if shape == "Đường tròn": return "TR2"
                if shape == "Mặt cầu": return "TR6"

        # ===== KHOẢNG CÁCH =====
        if operation == "Khoảng cách":
            if group == 'a':
                if shape == "Điểm": return "T1"
                if shape == "Đường thẳng": return "T5"
                if shape == "Mặt phẳng": return "Tz"
            if group == 'b':
                if shape == "Điểm": return "T2"
                if shape == "Đường thẳng": return "T6"
                if shape == "Mặt phẳng": return "Tx"
            # ===== DIỆN TÍCH (chỉ nhóm A) =====
        if operation == "Diện tích":
            if group == 'a':
                if shape == "Đường tròn": return "T1"
                if shape == "Mặt cầu": return "T5"

            # ===== THỂ TÍCH (chỉ nhóm A) =====
        if operation == "Thể tích":
            if group == 'a':
                if shape == "Mặt cầu": return "T1"

            # ===== PT ĐƯỜNG THẲNG =====
        if operation == "PT đường thẳng":
            if group == 'a':
                if shape == "Điểm": return "T1"
                if shape == "Vecto": return "T5"
            if group == 'b':
                if shape == "Điểm": return "T2"
                if shape == "Vecto": return "T6"

            # ===== PT MẶT PHẲNG =====
        if operation == "PT mặt phẳng":
            if group == 'a':
                if shape == "Điểm": return "T1"
                if shape == "Vecto": return "T5"
            if group == 'b':
                if shape == "Điểm": return "T2"
                if shape == "Vecto": return "T6"

            # ===== GÓC =====
        if operation == "Góc":
            if group == 'a':
                if shape == "Vecto": return "T1"
                if shape == "Đường thẳng": return "T5"
                if shape == "Mặt phẳng": return "Tz"
            if group == 'b':
                if shape == "Vecto": return "T2"
                if shape == "Đường thẳng": return "T6"
                if shape == "Mặt phẳng": return "Tx"

            # ===== TÍCH VÔ HƯỚNG 2 VECTO =====
        if operation == "Tích vô hướng 2 vecto":
            if group == 'a':
                if shape == "Vecto": return "T1"
            if group == 'b':
                if shape == "Vecto": return "T2"

            # ===== VECTO ĐƠN VỊ (chỉ nhóm A) =====
        if operation == "Vecto đơn vị":
            if group == 'a':
                if shape == "Vecto": return "T1"

            # ===== PHÉP TÍNH TAM GIÁC (chỉ nhóm A) =====
        if operation == "Phép tính tam giác":
            if group == 'a':
                if shape == "Tam giác": return "T1"


        return f"{group}_{shape}_{operation}"

    # ========== SHAPE ENCODING ==========
    def _encode_shape(self, shape, data):

        if not shape or not data:
            return ""

        # Route to specific shape encoder - chỉ encode DATA
        if shape == "Điểm":
            return self._encode_point_data(data)
        elif shape == "Vecto":
            return self._encode_vector_data(data)
        elif shape == "Đường thẳng":
            return self._encode_line_data(data)
        elif shape == "Mặt phẳng":
            return self._encode_plane_data(data)
        elif shape == "Đường tròn":
            return self._encode_circle_data(data)
        elif shape == "Mặt cầu":
            return self._encode_sphere_data(data)
        elif shape == "Tam giác":
            return self._encode_triangle_data(data)
        else:
            return ""

    def _encode_point_data(self, data):
        """
        Encode DATA của Điểm
        Input: "1, 2, 3"
        Output: "1=2=3=" (encode từng tọa độ, nối bằng =)
        """
        point_str = data.get('point_input', '')

        # Split bằng dấu phẩy
        coords = [c.strip() for c in point_str.split(',') if c.strip()]

        # Encode từng tọa độ
        encoded_coords = [self._encode_expression(c) for c in coords]

        # Nối bằng dấu = và thêm = ở cuối
        return '='.join(encoded_coords) + '='

    def _encode_vector_data(self, data):
        """Encode DATA của Vecto"""
        vector_str = data.get('vecto_input', data.get('vector_input', ''))

        components = [c.strip() for c in vector_str.split(',') if c.strip()]
        encoded_comps = [self._encode_expression(c) for c in components]

        return '='.join(encoded_comps) + '='

    def _encode_line_data(self, data):

        # Lấy điểm
        point_str = data.get('line_A1', data.get('point', ''))
        point_coords = [c.strip() for c in point_str.split(',') if c.strip()]

        # Lấy vector
        vector_str = data.get('line_X1', data.get('vector', ''))
        vector_comps = [c.strip() for c in vector_str.split(',') if c.strip()]

        # Encode từng phần
        encoded_point = [self._encode_expression(c) for c in point_coords]
        encoded_vector = [self._encode_expression(c) for c in vector_comps]

        # Xen kẽ: x=vx=y=vy=z=vz=
        result = []
        for i in range(max(len(encoded_point), len(encoded_vector))):
            if i < len(encoded_point):
                result.append(encoded_point[i])
            if i < len(encoded_vector):
                result.append(encoded_vector[i])

        # Join bằng = và thêm = cuối
        return '='.join(result) + '='

    def _encode_plane_data(self, data):
        """
        Encode DATA của Mặt phẳng
        ax+by+cz+d=0 → a=b=c=d=
        """
        a = str(data.get('plane_a', '0'))
        b = str(data.get('plane_b', '0'))
        c = str(data.get('plane_c', '0'))
        d = str(data.get('plane_d', '0'))

        encoded_a = self._encode_expression(a)
        encoded_b = self._encode_expression(b)
        encoded_c = self._encode_expression(c)
        encoded_d = self._encode_expression(d)

        return f"{encoded_a}={encoded_b}={encoded_c}={encoded_d}="

    def _encode_circle_data(self, data):
        """
        Encode DATA của Đường tròn
        Center: (3,4) → 3=4=
        Radius: 5 → R5=
        """
        center_str = data.get('circle_center', data.get('center', ''))
        center_coords = [c.strip() for c in center_str.split(',') if c.strip()]

        radius = str(data.get('circle_radius', data.get('radius', '0')))

        encoded_center = [self._encode_expression(c) for c in center_coords]
        encoded_radius = self._encode_expression(radius)

        # Center: 3=4=  Radius: R5=
        center_part = '='.join(encoded_center) + '='

        return f"{center_part}{encoded_radius}="

    def _encode_sphere_data(self, data):

        center_str = data.get('sphere_center', data.get('center', ''))
        center_coords = [c.strip() for c in center_str.split(',') if c.strip()]

        radius = str(data.get('sphere_radius', data.get('radius', '0')))

        encoded_center = [self._encode_expression(c) for c in center_coords]
        encoded_radius = self._encode_expression(radius)

        center_part = '='.join(encoded_center) + '='

        return f"{center_part}{encoded_radius}="

    def _encode_triangle_data(self, data):
        """Encode DATA của Tam giác"""
        if 'triangle_a' in data and ',' not in str(data.get('triangle_a', '')):
            # Format: sides (a, b, angle)
            a = str(data.get('triangle_a', '0'))
            b = str(data.get('triangle_b', '0'))
            angle = str(data.get('triangle_c', '0'))

            encoded_a = self._encode_expression(a)
            encoded_b = self._encode_expression(b)
            encoded_angle = self._encode_expression(angle)

            return f"{encoded_a}={encoded_b}={encoded_angle}="
        else:
            # Format: vertices (mỗi đỉnh có tọa độ x,y,z)
            vertex_a = str(data.get('triangle_a', ''))
            vertex_b = str(data.get('triangle_b', ''))
            vertex_c = str(data.get('triangle_c', ''))

            # Split từng đỉnh
            coords_a = [c.strip() for c in vertex_a.split(',') if c.strip()]
            coords_b = [c.strip() for c in vertex_b.split(',') if c.strip()]
            coords_c = [c.strip() for c in vertex_c.split(',') if c.strip()]

            encoded_a = [self._encode_expression(c) for c in coords_a]
            encoded_b = [self._encode_expression(c) for c in coords_b]
            encoded_c = [self._encode_expression(c) for c in coords_c]

            # Mỗi đỉnh: x=y=z=
            part_a = '='.join(encoded_a) + '='
            part_b = '='.join(encoded_b) + '='
            part_c = '='.join(encoded_c) + '='

            return part_a + part_b + part_c

    # ========== EXPRESSION ENCODING (SỬ DỤNG MAPPING FILE) ==========
    def _encode_expression(self, expr_str):
        """
        Encode biểu thức toán học sử dụng expression_encoding.json

        Args:
            expr_str: String biểu thức (ví dụ: "sqrt(2)", "3.14", "-5", "sin(x)")

        Returns:
            String encoded
        """
        if not expr_str or not str(expr_str).strip():
            return "0"

        result = str(expr_str).strip()

        # Bước 1: Apply REGEX mappings trước
        for mapping in self.regex_mappings:
            result = mapping['pattern'].sub(mapping['replace'], result)

        # Bước 2: Apply LITERAL mappings sau
        for mapping in self.literal_mappings:
            result = result.replace(mapping['find'], mapping['replace'])

        return result

    # ========== UTILITY METHODS ==========
    def validate_data(self, shape, data):
        """Validate dữ liệu trước khi encode"""
        if not data:
            return {'valid': False, 'error': 'Dữ liệu trống'}

        # Basic validation
        if shape == "Điểm":
            if 'point_input' not in data or not data['point_input']:
                return {'valid': False, 'error': 'Thiếu tọa độ điểm'}
        elif shape == "Vecto":
            if 'vecto_input' not in data and 'vector_input' not in data:
                return {'valid': False, 'error': 'Thiếu thành phần vecto'}
        elif shape == "Đường thẳng":
            if not data.get('line_A1') or not data.get('line_X1'):
                return {'valid': False, 'error': 'Thiếu điểm hoặc vector chỉ phương'}
        elif shape == "Mặt phẳng":
            required = ['plane_a', 'plane_b', 'plane_c', 'plane_d']
            if not all(k in data for k in required):
                return {'valid': False, 'error': 'Thiếu hệ số phương trình mặt phẳng'}
        elif shape == "Đường tròn":
            if not data.get('circle_center') or not data.get('circle_radius'):
                return {'valid': False, 'error': 'Thiếu tâm hoặc bán kính đường tròn'}
        elif shape == "Mặt cầu":
            if not data.get('sphere_center') or not data.get('sphere_radius'):
                return {'valid': False, 'error': 'Thiếu tâm hoặc bán kính mặt cầu'}

        return {'valid': True}

    def get_encoding_info(self):
        """Get thông tin về encoder"""
        return {
            'shapes': list(self.shape_codes.keys()),
            'operations': list(self.operation_codes.keys()),
            'regex_mappings_count': len(self.regex_mappings),
            'literal_mappings_count': len(self.literal_mappings)
        }

    def test_expression_encoding(self, expr):
        """Test encode một biểu thức"""
        return self._encode_expression(expr)
