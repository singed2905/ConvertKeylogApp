"""Quick test Equation Service - No GUI, chỉ test logic"""
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def quick_test_equations():
    """Test nhanh EquationService logic"""
    try:
        from services.equation.equation_service import EquationService
        
        print("🧪 Quick Test EquationService v2.0")
        print("=" * 40)
        
        service = EquationService()
        
        # Test 1: Hệ 2x2 đơn giản
        print("\n🟢 Test 1: Hệ 2x2 - 2x+3y=7, x-y=1")
        service.set_variables_count(2)
        service.set_version("fx799")
        
        success, status, solutions, final = service.process_complete_workflow(["2,3,7", "1,-1,1"])
        print(f"   Success: {success}")
        print(f"   Solutions: {solutions}")
        print(f"   Keylog: {final}")
        
        # Test 2: Hệ 3x3
        print("\n🟡 Test 2: Hệ 3x3 - x+y+z=6, 2x-y+z=1, x+2y-z=2")
        service.set_variables_count(3)
        
        success, status, solutions, final = service.process_complete_workflow(["1,1,1,6", "2,-1,1,1", "1,2,-1,2"])
        print(f"   Success: {success}")
        print(f"   Solutions: {solutions}")
        print(f"   Keylog: {final}")
        
        # Test 3: Biểu thức
        print("\n🔵 Test 3: Biểu thức - sqrt(4)x + pi*y = 10")
        service.set_variables_count(2)
        
        success, status, solutions, final = service.process_complete_workflow(["sqrt(4),pi,10", "1,1,6"])
        print(f"   Success: {success}")
        print(f"   Solutions: {solutions}")
        print(f"   Keylog: {final}")
        
        # Test 4: Error case - hệ vô nghiệm
        print("\n🔴 Test 4: Hệ vô nghiệm - 2x+4y=6, x+2y=5")
        service.set_variables_count(2)
        
        success, status, solutions, final = service.process_complete_workflow(["2,4,6", "1,2,5"])
        print(f"   Success: {success}")
        print(f"   Status: {status}")
        print(f"   Solutions: {solutions}")
        
        print("\n" + "=" * 40)
        print("✅ Quick test hoàn thành!")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def check_dependencies():
    """Kiểm tra dependencies cần thiết"""
    missing_deps = []
    
    try:
        import numpy
        print("✅ numpy OK")
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import pandas
        print("✅ pandas OK")
    except ImportError:
        missing_deps.append("pandas")
    
    try:
        import tkinter
        print("✅ tkinter OK")
    except ImportError:
        missing_deps.append("tkinter")
    
    if missing_deps:
        print(f"❌ Thiếu dependencies: {', '.join(missing_deps)}")
        print(f"Chạy: pip install {' '.join(missing_deps)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 ConvertKeylogApp v2.0 - Equation Quick Test")
    print("" + "=" * 50)
    
    # Kiểm tra dependencies
    if check_dependencies():
        print("\n🎆 Bắt đầu test Equation Service...")
        quick_test_equations()
    else:
        print("❌ Vui lòng cài đặt dependencies trước khi test.")