"""Test TL compatibility ngay - Quick verification"""
import sys
import os

# Add path cho imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def quick_test_tl_compatibility():
    """Test nhanh tương thích TL"""
    try:
        print("🚀 Quick TL Compatibility Test")
        print("=" * 40)
        
        # Test components
        print("\n1️⃣ Testing MappingManager...")
        from services.equation.mapping_manager import MappingManager
        mapper = MappingManager()
        
        # Test basic encoding
        test_inputs = ["2", "-3", "sqrt(4)", "sin(pi/2)"]
        for inp in test_inputs:
            encoded = mapper.encode_string(inp)
            print(f"   '{inp}' → '{encoded}'")
        
        print("\n2️⃣ Testing PrefixResolver...")
        from services.equation.prefix_resolver import EquationPrefixResolver
        prefix_resolver = EquationPrefixResolver()
        
        # Test prefixes
        test_versions = [("fx799", 2), ("fx801", 2), ("fx880", 2)]
        for version, variables in test_versions:
            prefix = prefix_resolver.get_equation_prefix(version, variables)
            print(f"   {version} - {variables} ẩn: '{prefix}'")
        
        print("\n3️⃣ Testing EquationEncodingService...")
        from services.equation.equation_encoding_service import EquationEncodingService
        encoding_service = EquationEncodingService()
        
        # Test encoding data
        test_coeffs = ["2", "3", "7", "1", "-1", "1"]
        result = encoding_service.encode_equation_data(test_coeffs, 2, "fx799")
        
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Encoded: {result['encoded_coefficients']}")
            print(f"   Final: {result['total_result']}")
            print(f"   Prefix: {result['prefix_used']}")
        else:
            print(f"   Error: {result.get('error', 'Unknown')}")
        
        print("\n4️⃣ Testing Full EquationService...")
        from services.equation.equation_service import EquationService
        service = EquationService()
        service.set_variables_count(2)
        service.set_version("fx799")
        
        # Test full workflow
        equations = ["2,3,7", "1,-1,1"]
        success, status, solutions, final = service.process_complete_workflow(equations)
        
        print(f"   Success: {success}")
        print(f"   Status: {status}")
        print(f"   Solutions: {solutions}")
        print(f"   Final keylog: {final}")
        
        # So sánh với expected TL
        expected_prefix = "w912"
        has_correct_prefix = expected_prefix in final if final else False
        print(f"   Correct prefix (w912): ✅" if has_correct_prefix else f"   Correct prefix: ❌")
        
        print("\n" + "=" * 40)
        if success and has_correct_prefix:
            print("✅ TL Compatibility: WORKING!")
        elif success:
            print("⚠️ Processing OK, nhưng prefix cần kiểm tra")
        else:
            print("❌ Có lỗi cần fix")
            
        return success and has_correct_prefix
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    quick_test_tl_compatibility()