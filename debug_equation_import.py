"""Debug import errors trong EquationService"""
import sys
import os

# Add path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports_step_by_step():
    """Test import từng bước để tìm lỗi"""
    print("🔍 Debug Equation Service Imports")
    print("=" * 40)
    
    try:
        print("1. Testing basic imports...")
        import numpy as np
        print("   ✅ numpy OK")
        
        import math
        print("   ✅ math OK")
        
        from typing import List, Dict, Tuple, Optional, Any
        print("   ✅ typing OK")
        
        print("\n2. Testing MappingManager...")
        from services.equation.mapping_manager import MappingManager
        mapper = MappingManager()
        print("   ✅ MappingManager OK")
        
        print("\n3. Testing PrefixResolver...")
        from services.equation.prefix_resolver import EquationPrefixResolver
        resolver = EquationPrefixResolver()
        print("   ✅ EquationPrefixResolver OK")
        
        print("\n4. Testing EquationEncodingService...")
        from services.equation.equation_encoding_service import EquationEncodingService
        encoding = EquationEncodingService()
        print("   ✅ EquationEncodingService OK")
        
        print("\n5. Testing main EquationService...")
        from services.equation.equation_service import EquationService
        service = EquationService()
        print("   ✅ EquationService OK")
        
        print("\n6. Testing basic functionality...")
        service.set_variables_count(2)
        service.set_version("fx799")
        
        # Simple test
        equations = ["2,3,7", "1,1,4"]
        success, status, solutions, final = service.process_complete_workflow(equations)
        
        print(f"   Processing: {'Success' if success else 'Failed'}")
        print(f"   Status: {status}")
        print(f"   Solutions: {solutions}")
        print(f"   Final result: {final}")
        
        if success:
            print("\n✅ Tất cả imports và basic functionality đều OK!")
        else:
            print("\n⚠️ Imports OK nhưng có lỗi logic")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Lỗi import: {e}")
        print("\n🔧 Cần kiểm tra:")
        print("   - Đường dẫn file có đúng không?")
        print("   - Có file __init__.py trong các folder không?")
        print("   - Syntax error trong các file service?")
        return False
        
    except Exception as e:
        print(f"\n❌ Lỗi khác: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def check_file_structure():
    """Kiểm tra cấu trúc file"""
    print("\n📁 Checking file structure...")
    
    expected_files = [
        "services/__init__.py",
        "services/equation/__init__.py", 
        "services/equation/equation_service.py",
        "services/equation/mapping_manager.py",
        "services/equation/prefix_resolver.py",
        "services/equation/equation_encoding_service.py",
        "config/equation_mode/equation_config.json",
        "config/equation_mode/mapping.json",
        "config/equation_mode/equation_prefixes.json"
    ]
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING!")

if __name__ == "__main__":
    print("🚀 Debug Equation Service Imports")
    
    # Kiểm tra cấu trúc file trước
    check_file_structure()
    
    # Test imports
    test_imports_step_by_step()