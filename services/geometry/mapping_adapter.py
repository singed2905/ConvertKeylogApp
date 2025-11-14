"""Geometry Mapping Adapter - REFACTORED to use LatexToKeylogEncoder
Fixed import paths and simplified encoding logic
"""
import sys
import os
from typing import Dict, Any, List
from utils.config_loader import config_loader

# ✅ FIX: Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# ✅ Import LatexToKeylogEncoder
try:
    from utils.latex_to_keylog import LatexToKeylogEncoder
except ImportError:
    print("Warning: Cannot import LatexToKeylogEncoder")
    LatexToKeylogEncoder = None


class GeometryMappingAdapter:
    """Adapter to handle mapping - REFACTORED với LatexToKeylogEncoder

    ✅ Thay đổi:
    - Sử dụng LatexToKeylogEncoder thay vì duplicate logic
    - Hỗ trợ tích phân (nếu cần trong geometry)
    - Fallback paths tự động
    - Code cleaner, dễ maintain

    Giữ nguyên:
    - Excel mapping methods
    - Interface công khai
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}

        # ✅ Sử dụng LatexToKeylogEncoder thay vì load polynomial mappings
        if LatexToKeylogEncoder:
            self.encoder = LatexToKeylogEncoder()
        else:
            print("Warning: LatexToKeylogEncoder not available, encoding will not work")
            self.encoder = None

        # Giữ Excel mappings cho geometry operations
        self.excel_mappings = self._load_excel_mappings()

    def _load_excel_mappings(self) -> Dict[str, Any]:
        """Load Excel mapping configuration - Giữ nguyên"""
        try:
            if self.config and 'geometry' in self.config:
                geometry_config = self.config['geometry']
                if 'excel_mapping' in geometry_config:
                    return geometry_config['excel_mapping']

            # Fallback: try to load directly from config_loader
            return config_loader.load_geometry_config('geometry_excel_mapping')
        except Exception as e:
            print(f"Warning: Could not load Excel mappings: {e}")
            return {}

    def encode_string(self, input_string: str) -> str:
        """Encode a string using LatexToKeylogEncoder

        ✅ REFACTORED: Delegate sang LatexToKeylogEncoder
        Hỗ trợ:
        - Fractions (nested)
        - Integrals (nếu có trong geometry)
        - sqrt, sin, cos, tan, ln
        - Dấu: -, *, /, ^
        """
        if not self.encoder:
            print("Warning: Encoder not available, returning input as-is")
            return input_string

        # ✅ THAY ĐỔI: Delegate sang encoder mới
        return self.encoder.encode(input_string)

    def get_excel_column_mapping(self, shape: str, group: str) -> Dict[str, str]:
        """Get Excel column mapping for a specific shape and group - Giữ nguyên

        Args:
            shape: Loại hình (Điểm, Đường thẳng, Mặt phẳng, Đường tròn, Mặt cầu)
            group: Group (A, B, C, ...)

        Returns:
            Dict mapping từ key → Excel column name
        """
        try:
            group_key = f"group_{group.lower()}_mapping"
            if group_key in self.excel_mappings and shape in self.excel_mappings[group_key]:
                shape_config = self.excel_mappings[group_key][shape]
                columns = shape_config.get('columns', {})
                return {key: col_info['excel_column'] for key, col_info in columns.items()}
        except Exception as e:
            print(f"Error getting Excel mapping for {shape} group {group}: {e}")

        return self._get_default_excel_mapping(shape, group)

    def _get_default_excel_mapping(self, shape: str, group: str) -> Dict[str, str]:
        """Fallback Excel mapping - Giữ nguyên"""
        if shape == "Điểm":
            return {'point_input': f'data_{group}'}
        elif shape == "Đường thẳng":
            return {'line_A1': f'd_P_data_{group}', 'line_X1': f'd_V_data_{group}'}
        elif shape == "Mặt phẳng":
            base = 'P1' if group == 'A' else 'P2'
            return {
                'plane_a': f'{base}_a',
                'plane_b': f'{base}_b',
                'plane_c': f'{base}_c',
                'plane_d': f'{base}_d'
            }
        elif shape == "Đường tròn":
            suffix = '1' if group == 'A' else '2'
            return {'circle_center': f'C_data_I{suffix}', 'circle_radius': f'C_data_R{suffix}'}
        elif shape == "Mặt cầu":
            suffix = '1' if group == 'A' else '2'
            return {'sphere_center': f'S_data_I{suffix}', 'sphere_radius': f'S_data_R{suffix}'}

        return {}

    # ✅ NEW METHODS - Thêm từ LatexToKeylogEncoder

    def encode_batch(self, expressions: List[str]) -> List[str]:
        """Encode multiple expressions at once

        ✅ NEW: Batch encoding support
        """
        if not self.encoder:
            return expressions
        return self.encoder.encode_batch(expressions)

    def validate_latex(self, expression: str) -> tuple:
        """Validate LaTeX expression

        ✅ NEW: Validation support
        Returns: (is_valid, error_message)
        """
        if not self.encoder:
            return (False, "Encoder not available")
        return self.encoder.validate_latex(expression)

    def is_available(self) -> bool:
        """Check if encoder is available"""
        return self.encoder is not None


# ========== TESTING ==========
if __name__ == "__main__":
    print("=" * 80)
    print("GEOMETRY MAPPING ADAPTER - REFACTORED TEST")
    print("=" * 80)

    adapter = GeometryMappingAdapter()

    if not adapter.is_available():
        print("❌ Adapter not available (LatexToKeylogEncoder missing)")
        exit(1)

    print("✅ Adapter initialized successfully")
    print(f"  - Encoder type: LatexToKeylogEncoder")
    print(f"  - Mapping rules: {len(adapter.encoder.mappings)}")
    print()

    # Test 1: Basic encoding
    print("--- Test 1: Basic Encoding ---")
    test_cases = [
        "1",
        "-5",
        "\\frac{1}{2}",
        "sqrt(4)",
        "sin(pi/2)",
    ]

    for expr in test_cases:
        encoded = adapter.encode_string(expr)
        print(f"{expr:20} → {encoded}")

    # Test 2: Batch encoding
    print("\n--- Test 2: Batch Encoding (NEW) ---")
    batch = ["\\frac{1}{2}", "sqrt(9)", "-3"]
    results = adapter.encode_batch(batch)
    print(f"Input:  {batch}")
    print(f"Output: {results}")

    # Test 3: Validation
    print("\n--- Test 3: Validation (NEW) ---")
    validation_tests = [
        "\\frac{1}{2}",
        "\\frac{1{2}",  # Invalid
        "sqrt(16)",
    ]

    for expr in validation_tests:
        valid, error = adapter.validate_latex(expr)
        status = "✓" if valid else f"✗ ({error})"
        print(f"{status} {expr}")

    # Test 4: Excel mapping (giữ nguyên)
    print("\n--- Test 4: Excel Mapping (Unchanged) ---")
    shapes_tests = [
        ("Điểm", "A"),
        ("Đường thẳng", "B"),
        ("Mặt phẳng", "A"),
    ]

    for shape, group in shapes_tests:
        mapping = adapter.get_excel_column_mapping(shape, group)
        print(f"{shape} (Group {group}): {mapping}")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
