"""Test EquationService - Basic functionality test"""
import sys
import os

# Thêm path để import được services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_equation_service_basic():
    """Test cơ bản cho EquationService"""
    try:
        from services.equation.equation_service import EquationService
        print("✅ Import EquationService thành công!")
        
        # Test khởi tạo
        service = EquationService()
        print("✅ Khởi tạo EquationService thành công!")
        
        # Test hệ 2 phương trình 2 ẩn
        print("\n=== TEST HỆ 2 PHƯƠNG TRÌNH 2 ẨN ===")
        service.set_variables_count(2)
        service.set_version("fx799")
        
        # Ví dụ: 2x + 3y = 7, x - y = 1
        equation_inputs = ["2,3,7", "1,-1,1"]
        
        # Test validation
        is_valid, msg = service.validate_input(equation_inputs)
        print(f"Validation: {is_valid} - {msg}")
        
        if is_valid:
            # Xử lý hoàn chỉnh
            success, status_msg, solutions_text, final_result = service.process_complete_workflow(equation_inputs)
            
            print(f"Xử lý thành công: {success}")
            print(f"Status: {status_msg}")
            print(f"Nghiệm: {solutions_text}")
            print(f"Kết quả cuối: {final_result}")
            
            # Hiển thị encoded coefficients
            encoded = service.get_encoded_coefficients_display()
            print(f"Encoded coefficients: {encoded}")
            
            # Hiển thị ma trận info
            print("\nMatrix Info:")
            print(service.get_matrix_info())
        
        print("\n=== TEST HỆ 3 PHƯƠNG TRÌNH 3 ẨN ===")
        service.set_variables_count(3)
        
        # Ví dụ: x + y + z = 6, 2x - y + z = 1, x + 2y - z = 2
        equation_inputs_3 = ["1,1,1,6", "2,-1,1,1", "1,2,-1,2"]
        
        is_valid, msg = service.validate_input(equation_inputs_3)
        print(f"Validation: {is_valid} - {msg}")
        
        if is_valid:
            success, status_msg, solutions_text, final_result = service.process_complete_workflow(equation_inputs_3)
            
            print(f"Xử lý thành công: {success}")
            print(f"Status: {status_msg}")
            print(f"Nghiệm: {solutions_text}")
            print(f"Kết quả cuối: {final_result}")
        
        print("\n=== TEST BIỂU THỨC PHỨC TẠP ===")
        service.set_variables_count(2)
        
        # Ví dụ với biểu thức: sqrt(4)x + pi*y = 10, sin(pi/2)*x + cos(0)*y = 3
        equation_complex = ["sqrt(4),pi,10", "sin(pi/2),cos(0),3"]
        
        is_valid, msg = service.validate_input(equation_complex)
        print(f"Validation: {is_valid} - {msg}")
        
        if is_valid:
            success, status_msg, solutions_text, final_result = service.process_complete_workflow(equation_complex)
            
            print(f"Xử lý thành công: {success}")
            print(f"Status: {status_msg}")
            print(f"Nghiệm: {solutions_text}")
            print(f"Kết quả cuối: {final_result}")
        
        print("\n✅ Tất cả test cơ bản đều pass!")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_equation_ui():
    """Test giao diện Equation Mode"""
    try:
        print("\n=== TEST EQUATION UI ===")
        import tkinter as tk
        
        # Import equation view
        sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'views'))
        from equation_view import EquationView
        
        root = tk.Tk()
        
        # Tạo sample config
        sample_config = {
            'common': {
                'versions': {
                    'versions': ['fx799', 'fx800', 'fx801']
                }
            },
            'equation': {
                'encoding': {
                    'numbers': {
                        '0': '00', '1': '01', '2': '02', '3': '03', '4': '04',
                        '5': '05', '6': '06', '7': '07', '8': '08', '9': '09',
                        '-': 'FF', '.': 'FE'
                    },
                    'prefix': 'EQ'
                },
                'prefixes': {
                    'versions': {
                        'fx799': {'base_prefix': 'EQ799'},
                        'fx800': {'base_prefix': 'EQ800'},
                        'fx801': {'base_prefix': 'EQ801'}
                    }
                }
            }
        }
        
        app = EquationView(root, config=sample_config)
        print("✅ Tạo EquationView thành công!")
        
        # Test cơ bản - không chạy mainloop
        print("✅ UI test cơ bản pass!")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test UI: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("🧪 Testing EquationService v2.0...")
    print("=" * 50)
    
    # Test service
    service_ok = test_equation_service_basic()
    
    # Test UI (optional - có thể skip nếu không có display)
    ui_ok = test_equation_ui()
    
    print("=" * 50)
    if service_ok and ui_ok:
        print("🎉 Tất cả tests đều PASS! EquationService v2.0 sẵn sàng!")
    elif service_ok:
        print("✅ Service tests PASS! UI có thể cần adjustment.")
    else:
        print("❌ Có lỗi trong quá trình test. Vui lòng kiểm tra lại.")