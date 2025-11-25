
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from services.geometry_v2.geometry_v2_service import GeometryV2Service


def test_basic_encoding():
    """Test encoding cơ bản"""
    print("=" * 60)
    print("TEST 1: ENCODING CƠ BẢN - 2 ĐIỂM")
    print("=" * 60)

    service = GeometryV2Service()

    # Set config
    service.set_operation("Khoảng cách")
    service.set_shapes("Điểm", "Điểm")
    service.set_dimension("3", "3")

    # Data
    data_a = {'point_input': '1, 2 \\cdot 5'}
    data_b = {'point_input': '4, 5, 6'}

    # Encode
    result = service.process_manual_data(data_a, data_b)

    print(f"✅ Success: {result['success']}")
    if result['success']:
        print(f"📝 Encoded: {result['encoded']}")
        print(f"📋 Expected: wjP1C2C3CwjP4C5C6CDIST= =")  # ← CẬP NHẬT
    else:
        print(f"❌ Error: {result['error']}")
    print()


def test_expression_encoding():
    """Test encoding với biểu thức"""
    print("=" * 60)
    print("TEST 2: ENCODING VỚI BIỂU THỨC")
    print("=" * 60)

    service = GeometryV2Service()
    service.set_operation("Khoảng cách")
    service.set_shapes("Điểm", "Điểm")

    data_a = {'point_input': 'sqrt(2), -3, sin(45)'}
    data_b = {'point_input': '1, 2, log(10)'}

    result = service.process_manual_data(data_a, data_b)

    print(f"✅ Success: {result['success']}")
    if result['success']:
        print(f"📝 Encoded: {result['encoded']}")
        print(f"📋 Expected: wjPs(2)Cp3Cj(45)CwjP1C2Ci(10)CDIST= =")  # ← CẬP NHẬT
    else:
        print(f"❌ Error: {result['error']}")
    print()


def test_vector():
    """Test encoding vecto"""
    print("=" * 60)
    print("TEST 3: ENCODING VECTO")
    print("=" * 60)

    service = GeometryV2Service()
    service.set_operation("Tích vô hướng 2 vecto")
    service.set_shapes("Vecto", "Vecto")

    data_a = {'vecto_input': '1, 2, 3'}
    data_b = {'vecto_input': '4, 5, 6'}

    result = service.process_manual_data(data_a, data_b)

    print(f"✅ Success: {result['success']}")
    if result['success']:
        print(f"📝 Encoded: {result['encoded']}")
        print(f"📋 Expected: wjV1C2C3CwjV4C5C6CDOT= =")  # ← CẬP NHẬT
    else:
        print(f"❌ Error: {result['error']}")
    print()


def test_line():
    """Test encoding đường thẳng"""
    print("=" * 60)
    print("TEST 4: ENCODING ĐƯỜNG THẲNG")
    print("=" * 60)

    service = GeometryV2Service()
    service.set_operation("Khoảng cách")
    service.set_shapes("Đường thẳng", "Điểm")

    data_a = {
        'line_A1': '1, 2, 3',
        'line_X1': '4, 5, 6'
    }
    data_b = {'point_input': '4, 5, 6'}

    result = service.process_manual_data(data_a, data_b)

    print(f"✅ Success: {result['success']}")
    if result['success']:
        print(f"📝 Encoded: {result['encoded']}")
        print(f"📋 Expected: wjLA1C2C3CU2Cp1C1CwjP4C5C6CDIST= =")  # ← CẬP NHẬT
    else:
        print(f"❌ Error: {result['error']}")
    print()


def test_plane():
    """Test encoding mặt phẳng"""
    print("=" * 60)
    print("TEST 5: ENCODING MẶT PHẲNG")
    print("=" * 60)

    service = GeometryV2Service()
    service.set_operation("Khoảng cách")
    service.set_shapes("Mặt phẳng", "Điểm")

    data_a = {
        'plane_a': '2',
        'plane_b': '-3',
        'plane_c': '1',
        'plane_d': '5'
    }
    data_b = {'point_input': '1, 2, 3'}

    result = service.process_manual_data(data_a, data_b)

    print(f"✅ Success: {result['success']}")
    if result['success']:
        print(f"📝 Encoded: {result['encoded']}")
        print(f"📋 Expected: wjPL2Cp3C1C5CwjP1C2C3CDIST= =")  # ← CẬP NHẬT
    else:
        print(f"❌ Error: {result['error']}")
    print()


def test_circle():
    """Test encoding đường tròn"""
    print("=" * 60)
    print("TEST 6: ENCODING ĐƯỜNG TRÒN")
    print("=" * 60)

    service = GeometryV2Service()
    service.set_operation("Diện tích")
    service.set_shapes("Đường tròn", None)

    data_a = {
        'circle_center': '3, 4',
        'circle_radius': '5'
    }

    result = service.process_manual_data(data_a, None)

    print(f"✅ Success: {result['success']}")
    if result['success']:
        print(f"📝 Encoded: {result['encoded']}")
        print(f"📋 Expected: wjCI3C4CR5CAREA= =")  # ← CẬP NHẬT
    else:
        print(f"❌ Error: {result['error']}")
    print()


def test_sphere():
    """Test encoding mặt cầu"""
    print("=" * 60)
    print("TEST 7: ENCODING MẶT CẦU")
    print("=" * 60)

    service = GeometryV2Service()
    service.set_operation("Thể tích")
    service.set_shapes("Mặt cầu", None)

    data_a = {
        'sphere_center': '1, 2, 3',
        'sphere_radius': '7'
    }

    result = service.process_manual_data(data_a, None)

    print(f"✅ Success: {result['success']}")
    if result['success']:
        print(f"📝 Encoded: {result['encoded']}")
        print(f"📋 Expected: wjSI1C2C3CR7CVOL= =")  # ← CẬP NHẬT
    else:
        print(f"❌ Error: {result['error']}")
    print()


def test_triangle():
    """Test encoding tam giác"""
    print("=" * 60)
    print("TEST 8: ENCODING TAM GIÁC")
    print("=" * 60)

    service = GeometryV2Service()
    service.set_operation("Phép tính tam giác")
    service.set_shapes("Tam giác", None)

    data_a = {
        'triangle_a': '5',
        'triangle_b': '7',
        'triangle_c': '60'
    }

    result = service.process_manual_data(data_a, None)

    print(f"✅ Success: {result['success']}")
    if result['success']:
        print(f"📝 Encoded: {result['encoded']}")
        print(f"📋 Expected: wjT5C7C60CTRI= =")  # ← CẬP NHẬT
    else:
        print(f"❌ Error: {result['error']}")
    print()


def test_complex_expression():
    """Test encoding biểu thức phức tạp"""
    print("=" * 60)
    print("TEST 9: ENCODING BIỂU THỨC PHỨC TẠP")
    print("=" * 60)

    service = GeometryV2Service()
    service.set_operation("Khoảng cách")
    service.set_shapes("Điểm", "Điểm")

    data_a = {'point_input': 'sqrt(2), log(10), sin(x)'}
    data_b = {'point_input': '3/4, -5, 2*pi'}

    result = service.process_manual_data(data_a, data_b)

    print(f"✅ Success: {result['success']}")
    if result['success']:
        print(f"📝 Encoded: {result['encoded']}")
        print(f"📋 Expected: wjPs(2)Ci(10)Cj([)CwjP3P4Cp5C2OpiCDIST= =")  # ← CẬP NHẬT
    else:
        print(f"❌ Error: {result['error']}")
    print()


def test_validation_errors():
    """Test validation lỗi"""
    print("=" * 60)
    print("TEST 10: VALIDATION ERRORS")
    print("=" * 60)

    service = GeometryV2Service()
    service.set_operation("Khoảng cách")
    service.set_shapes("Điểm", "Điểm")

    # Test 1: Empty data
    print("Test 10.1: Empty data")
    data_a = {'point_input': ''}
    data_b = {'point_input': '1, 2, 3'}
    result = service.process_manual_data(data_a, data_b)
    print(f"   Success: {result['success']}")
    print(f"   Error: {result.get('error', 'N/A')}")
    print()

    # Test 2: Missing field
    print("Test 10.2: Missing field")
    data_a = {}  # Missing point_input
    data_b = {'point_input': '1, 2, 3'}
    result = service.process_manual_data(data_a, data_b)
    print(f"   Success: {result['success']}")
    print(f"   Error: {result.get('error', 'N/A')}")
    print()

def test_encoder_info():
    """Test lấy thông tin encoder"""
    print("=" * 60)
    print("TEST 11: ENCODER INFO")
    print("=" * 60)

    service = GeometryV2Service()

    if service.encoder:
        info = service.encoder.get_encoding_info()

        print(f"📊 Shapes available: {len(info['shapes'])}")
        for shape in info['shapes']:
            print(f"   - {shape}")
        print()

        print(f"📊 Operations available: {len(info['operations'])}")
        for op in info['operations']:
            print(f"   - {op}")
        print()

        print(f"📊 Regex mappings: {info['regex_mappings_count']}")
        print(f"📊 Literal mappings: {info['literal_mappings_count']}")
    else:
        print("❌ Encoder not initialized")
    print()

def run_all_tests():
    """Chạy tất cả tests"""
    print("\n" + "=" * 60)
    print("🚀 BẮT ĐẦU TEST GEOMETRY V2 SERVICE")
    print("=" * 60 + "\n")

    try:
        test_basic_encoding()
        test_expression_encoding()
        test_vector()
        test_line()
        test_plane()
        test_circle()
        test_sphere()
        test_triangle()
        test_complex_expression()
        test_validation_errors()
        test_encoder_info()

        print("=" * 60)
        print("✅ TẤT CẢ TESTS ĐÃ HOÀN THÀNH")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ LỖI TRONG QUÁ TRÌNH TEST: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
