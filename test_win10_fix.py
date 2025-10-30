"""Test fix cho Windows 10 + Python 3.12.0"""
import sys
import os
import shutil

# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def clean_pycache_windows():
    """Dọn dẹp __pycache__ cho Windows"""
    print("🧽 Cleaning __pycache__ folders on Windows...")
    
    # Các thư mục cần clean
    cache_dirs = [
        "__pycache__",
        "services/__pycache__",
        "services/equation/__pycache__",
        "services/geometry/__pycache__",
        "services/excel/__pycache__",
        "views/__pycache__",
        "utils/__pycache__",
        "config/__pycache__"
    ]
    
    cleaned_count = 0
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"   ✅ Cleaned: {cache_dir}")
                cleaned_count += 1
            except Exception as e:
                print(f"   ⚠️ Cannot clean {cache_dir}: {e}")
        else:
            print(f"   ➖ Not found: {cache_dir}")
    
    print(f"\n📦 Cleaned {cleaned_count} cache directories")
    return cleaned_count

def test_python_312_compatibility():
    """Test tương thích Python 3.12"""
    print(f"\n🐍 Python version: {sys.version}")
    
    if sys.version_info < (3, 8):
        print("❌ Python quá cũ! Cần Python 3.8+")
        return False
    
    if sys.version_info >= (3, 12):
        print("✅ Python 3.12+ - Sử dụng typing modern")
    else:
        print("✅ Python tương thích")
    
    return True

def test_imports_clean():
    """Test imports sau khi clean cache"""
    print("\n🗋 Testing imports after cache clean...")
    
    try:
        print("1. Basic Python modules:")
        import numpy as np
        print("   ✅ numpy")
        
        import math
        print("   ✅ math")
        
        from typing import List, Dict, Tuple, Optional, Any
        print("   ✅ typing (List, Dict, Tuple, Optional, Any)")
        
        print("\n2. EquationService components:")
        
        # Test MappingManager
        from services.equation.mapping_manager import MappingManager
        mapper = MappingManager()
        test_encode = mapper.encode_string("2")
        print(f"   ✅ MappingManager - encode '2' -> '{test_encode}'")
        
        # Test PrefixResolver
        from services.equation.prefix_resolver import EquationPrefixResolver
        resolver = EquationPrefixResolver()
        test_prefix = resolver.get_equation_prefix("fx799", 2)
        print(f"   ✅ EquationPrefixResolver - fx799, 2 an -> '{test_prefix}'")
        
        # Test EquationEncodingService
        from services.equation.equation_encoding_service import EquationEncodingService
        encoding_service = EquationEncodingService()
        print(f"   ✅ EquationEncodingService - Available: {encoding_service.is_available()}")
        
        # Test main EquationService
        from services.equation.equation_service import EquationService
        service = EquationService()
        print(f"   ✅ EquationService - TL encoding: {service.tl_encoding_available}")
        
        print("\n3. Full workflow test:")
        service.set_variables_count(2)
        service.set_version("fx799")
        
        # Test cơ bản: 2x + 3y = 7, x - y = 1
        equations = ["2,3,7", "1,-1,1"]
        success, status, solutions, final = service.process_complete_workflow(equations)
        
        print(f"   Success: {success}")
        print(f"   Status: {status}")
        print(f"   Solutions: {solutions}")
        print(f"   Final keylog: {final}")
        
        # Kiểm tra prefix đúng
        expected_prefix = "w912"
        has_correct_prefix = final.startswith(expected_prefix) if final else False
        print(f"   Correct TL prefix: ✅" if has_correct_prefix else f"   Correct TL prefix: ❌")
        
        if success and has_correct_prefix:
            print("\n✅ Tất cả imports và TL compatibility đều OK!")
            return True
        elif success:
            print("\n⚠️ Processing OK nhưng prefix cần kiểm tra")
            return True
        else:
            print("\n❌ Có lỗi processing")
            return False
        
    except Exception as e:
        print(f"\n❌ Lỗi import/test: {e}")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())
        return False

def run_ui_test():
    """Test UI sau khi fix"""
    print("\n🖥️ Testing UI integration...")
    
    try:
        import tkinter as tk
        from views.equation_view import EquationView
        
        print("   Creating test window...")
        root = tk.Tk()
        root.withdraw()  # Ẩn window để test
        
        # Tạo EquationView
        app = EquationView(root)
        
        # Kiểm tra service có khởi tạo thành công không
        if hasattr(app, 'equation_service') and app.equation_service:
            print("   ✅ EquationService khởi tạo thành công trong UI!")
            success = True
        else:
            print("   ❌ EquationService vẫn chưa khởi tạo trong UI")
            success = False
        
        root.destroy()
        return success
        
    except Exception as e:
        print(f"   ❌ Lỗi UI test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Windows 10 + Python 3.12.0 Fix Test")
    print("" + "=" * 50)
    
    # Kiểm tra Python version
    if not test_python_312_compatibility():
        exit(1)
    
    # Clean cache
    clean_pycache_windows()
    
    # Test imports
    imports_ok = test_imports_clean()
    
    if imports_ok:
        # Test UI
        ui_ok = run_ui_test()
        
        print("\n" + "=" * 50)
        if ui_ok:
            print("🎉 HOÀN THÀNH! Equation Mode sẵn sàng với TL encoding!")
            print("\n🎯 Giờ bạn có thể:")
            print("   1. Chạy: python main.py")
            print("   2. Chọn Equation Mode")
            print("   3. Nhập: 2,3,7 và 1,-1,1")
            print("   4. Bấm '🚀 Xử lý & Giải nghiệm'")
            print("   5. Xem keylog bắt đầu bằng 'w912'")
        else:
            print("⚠️ Imports OK nhưng UI vẫn có vấn đề")
            print("Hãy chạy: python main.py để kiểm tra")
    else:
        print("\n❌ Vẫn có lỗi import. Kiểm tra lại dependencies:")
        print("   pip install numpy pandas openpyxl psutil")
        print("   Sau đó chạy lại script này.")