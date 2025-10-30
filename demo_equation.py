"""Demo Equation Mode - Test đầy đủ chức năng"""
import sys
import os

# Thêm path cho imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_equation_demo():
    """Chạy demo Equation Mode với UI hoàn chỉnh"""
    try:
        import tkinter as tk
        from views.equation_view import EquationView
        from utils.config_loader import ConfigLoader
        
        print("🚀 Khởi động Equation Mode Demo...")
        
        # Load config
        config_loader = ConfigLoader()
        config = config_loader.get_mode_config('equation')
        
        # Tạo cửa sổ chính
        root = tk.Tk()
        root.configure(bg="#F0F8FF")
        
        # Hiển thị thông tin config
        if config:
            print("✅ Đã load config Equation Mode thành công")
            print(f"   - Phiên bản: {config.get('equation', {}).get('version', 'Unknown')}")
            print(f"   - Hỗ trợ ẩn: {config.get('equation', {}).get('supported_variables', {}).get('available', [2,3,4])}")
        else:
            print("⚠️ Sử dụng fallback config")
        
        # Khởi tạo EquationView
        app = EquationView(root, config=config)
        print("✅ EquationView khởi tạo thành công!")
        
        print("\n📝 Hướng dẫn sử dụng:")
        print("1. Chọn số ẩn (2, 3, hoặc 4)")
        print("2. Chọn phiên bản máy tính (fx799, fx800, v.v.)")
        print("3. Nhập hệ số phương trình (ví dụ: '2,3,7' cho 2x+3y=7)")
        print("4. Bấm '🚀 Xử lý & Giải nghiệm' để tính toán")
        print("5. Xem kết quả và copy keylog")
        print("\n🎉 Sẵn sàng sử dụng Equation Mode!")
        
        # Chạy giao diện
        root.mainloop()
        
    except ImportError as e:
        print(f"❌ Lỗi import: {e}")
        print("\n🔧 Cần cài đặt dependencies:")
        print("pip install numpy pandas openpyxl tkinter psutil")
        
    except Exception as e:
        print(f"❌ Lỗi khởi tạo: {e}")
        import traceback
        print(traceback.format_exc())

def test_sample_equations():
    """Test với dữ liệu mẫu"""
    try:
        from services.equation.equation_service import EquationService
        
        print("\n🧪 Testing các ví dụ phương trình mẫu...")
        
        service = EquationService()
        
        # Test case 1: Hệ 2 phương trình 2 ẩn
        print("\n1️⃣ Test hệ 2x2:")
        print("Phương trình: 2x + 3y = 7, x - y = 1")
        
        service.set_variables_count(2)
        success, status, solutions, final = service.process_complete_workflow(["2,3,7", "1,-1,1"])
        print(f"Kết quả: {solutions}")
        print(f"Keylog: {final}")
        
        # Test case 2: Hệ 3 phương trình 3 ẩn
        print("\n2️⃣ Test hệ 3x3:")
        print("Phương trình: x+y+z=6, 2x-y+z=1, x+2y-z=2")
        
        service.set_variables_count(3)
        success, status, solutions, final = service.process_complete_workflow(["1,1,1,6", "2,-1,1,1", "1,2,-1,2"])
        print(f"Kết quả: {solutions}")
        print(f"Keylog: {final}")
        
        # Test case 3: Với biểu thức
        print("\n3️⃣ Test với biểu thức:")
        print("Phương trình: sqrt(4)x + pi*y = 10, sin(pi/2)*x + cos(0)*y = 3")
        
        service.set_variables_count(2)
        success, status, solutions, final = service.process_complete_workflow(["sqrt(4),pi,10", "sin(pi/2),cos(0),3"])
        print(f"Kết quả: {solutions}")
        print(f"Keylog: {final}")
        
        print("\n✅ Tất cả test cases đều hoàn thành!")
        
    except Exception as e:
        print(f"❌ Lỗi test: {e}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    print("🧮 ConvertKeylogApp v2.0 - Equation Mode Demo")
    print("=" * 55)
    
    # Kiểm tra dependencies
    try:
        import numpy
        import pandas 
        print("✅ Dependencies OK (numpy, pandas)")
    except ImportError as e:
        print(f"❌ Thiếu dependency: {e}")
        print("Chạy: pip install numpy pandas openpyxl tkinter psutil")
        exit(1)
    
    # Test các sample equations trước
    test_sample_equations()
    
    print("\n" + "=" * 55)
    print("🚀 Khởi động Equation Mode GUI...")
    
    # Chạy demo UI
    run_equation_demo()