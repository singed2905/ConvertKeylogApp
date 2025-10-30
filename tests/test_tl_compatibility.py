"""Test tương thích với TL - So sánh keylog output"""
import sys
import os

# Thêm path để import được services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_tl_keylog_compatibility():
    """Test keylog output có giống TL không"""
    try:
        from services.equation.equation_service import EquationService
        
        print("🧪 Testing TL Compatibility - Equation Keylog")
        print("=" * 55)
        
        service = EquationService()
        
        # Test cases giống TL
        test_cases = [
            {
                "name": "Basic 2x2 - Integer coefficients",
                "variables": 2,
                "version": "fx799", 
                "equations": ["2,3,7", "1,-1,1"],
                "description": "2x + 3y = 7; x - y = 1",
                "expected_prefix": "w912",
                "expected_solutions": "x = 2; y = 1"
            },
            {
                "name": "Complex expressions",
                "variables": 2,
                "version": "fx799",
                "equations": ["sqrt(4),pi,10", "sin(pi/2),cos(0),3"],
                "description": "sqrt(4)x + pi*y = 10; sin(pi/2)x + cos(0)y = 3",
                "expected_prefix": "w912"
            },
            {
                "name": "3x3 system",
                "variables": 3,
                "version": "fx799",
                "equations": ["1,1,1,6", "2,-1,1,1", "1,2,-1,2"],
                "description": "x+y+z=6; 2x-y+z=1; x+2y-z=2",
                "expected_prefix": "w913"
            },
            {
                "name": "fx801 version test",
                "variables": 2,
                "version": "fx801",
                "equations": ["1,2,5", "3,1,7"],
                "description": "x + 2y = 5; 3x + y = 7",
                "expected_prefix": "yl912"
            },
            {
                "name": "fx880 special prefix",
                "variables": 2,
                "version": "fx880",
                "equations": ["1,0,2", "0,1,3"],
                "description": "x = 2; y = 3",
                "expected_prefix": "wR$$|||"
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases):
            print(f"\n🔄 Test {i+1}: {test_case['name']}")
            print(f"   Description: {test_case['description']}")
            print(f"   Version: {test_case['version']}")
            print(f"   Expected prefix: {test_case['expected_prefix']}")
            
            # Setup service
            service.set_variables_count(test_case['variables'])
            service.set_version(test_case['version'])
            
            # Process
            success, status, solutions, final_keylog = service.process_complete_workflow(test_case['equations'])
            
            # Test compatibility features
            tl_compat = service.test_tl_compatibility([item for sublist in [eq.split(',') for eq in test_case['equations']] for item in sublist])
            
            result = {
                "test_name": test_case['name'],
                "success": success,
                "status": status,
                "solutions": solutions,
                "final_keylog": final_keylog,
                "expected_prefix": test_case['expected_prefix'],
                "actual_prefix": final_keylog.split(test_case['expected_prefix'])[:1] if test_case['expected_prefix'] in final_keylog else "Not found",
                "prefix_match": test_case['expected_prefix'] in final_keylog if final_keylog else False,
                "tl_compat_info": tl_compat
            }
            
            results.append(result)
            
            # Print results
            print(f"   Success: {success}")
            print(f"   Solutions: {solutions}")
            print(f"   Final keylog: {final_keylog}")
            print(f"   Prefix match: ✅ {result['prefix_match']}" if result['prefix_match'] else f"   Prefix match: ❌ {result['prefix_match']}")
            
            if tl_compat and not tl_compat.get('error'):
                print(f"   TL Encoding: ✅ Available")
            else:
                print(f"   TL Encoding: ❌ {tl_compat.get('error', 'Failed')}")
        
        # Summary
        print("\n" + "=" * 55)
        print("📊 SUMMARY:")
        
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r['success'])
        prefix_matches = sum(1 for r in results if r['prefix_match'])
        tl_encoding_works = sum(1 for r in results if not r['tl_compat_info'].get('error'))
        
        print(f"Total tests: {total_tests}")
        print(f"Successful processing: {successful_tests}/{total_tests}")
        print(f"Correct prefixes: {prefix_matches}/{total_tests}")
        print(f"TL encoding available: {tl_encoding_works}/{total_tests}")
        
        if successful_tests == total_tests and prefix_matches == total_tests:
            print("\n🎉 Tất cả tests PASS! ConvertKeylogApp đã tương thích với TL!")
        elif successful_tests == total_tests:
            print("\n✅ Processing OK, nhưng cần điều chỉnh prefixes.")
        else:
            print("\n❌ Có lỗi xử lý. Cần kiểm tra lại.")
        
        return results
        
    except Exception as e:
        print(f"❌ Lỗi test compatibility: {e}")
        import traceback
        print(traceback.format_exc())
        return []

def test_individual_encoding():
    """Test mã hóa từng biểu thức"""
    try:
        from services.equation.mapping_manager import MappingManager
        from services.equation.prefix_resolver import EquationPrefixResolver
        
        print("\n🔍 Testing Individual Components")
        print("-" * 40)
        
        # Test MappingManager
        mapper = MappingManager()
        prefix_resolver = EquationPrefixResolver()
        
        test_expressions = [
            "2", "-3", "1.5", "sqrt(4)", "sin(pi/2)", 
            "\\frac{1}{2}", "2*3", "10/5", "2^3"
        ]
        
        print("\n🔢 MappingManager Test:")
        for expr in test_expressions:
            encoded = mapper.encode_string(expr)
            print(f"   '{expr}' → '{encoded}'")
        
        print("\n🏷️ PrefixResolver Test:")
        versions = ["fx799", "fx801", "fx880"]
        for version in versions:
            for variables in [2, 3, 4]:
                prefix = prefix_resolver.get_equation_prefix(version, variables)
                print(f"   {version} - {variables} ẩn: '{prefix}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test individual: {e}")
        return False

def compare_with_tl_expected():
    """So sánh với kết quả mong đợi từ TL (manual)"""
    print("\n🤖 Expected TL Outputs (for comparison):")
    print("-" * 50)
    
    expected_tl = [
        {
            "input": "2,3,7 | 1,-1,1 (fx799, 2 ẩn)",
            "expected": "w9122=3=7=1=p1=1== =",
            "note": "2x+3y=7; x-y=1"
        },
        {
            "input": "1,1,1,6 | 2,-1,1,1 | 1,2,-1,2 (fx799, 3 ẩn)",
            "expected": "w9131=1=1=6=2=p1=1=1=1=2=p1=2== = =",
            "note": "x+y+z=6; 2x-y+z=1; x+2y-z=2"
        }
    ]
    
    for exp in expected_tl:
        print(f"Input: {exp['input']}")
        print(f"Expected TL: {exp['expected']}")
        print(f"Note: {exp['note']}")
        print()

if __name__ == "__main__":
    print("🚀 ConvertKeylogApp v2.0 - TL Compatibility Test")
    print("" + "=" * 60)
    
    # Kiểm tra dependencies
    try:
        import numpy
        print("✅ numpy OK")
    except ImportError:
        print("❌ Thiếu numpy - chạy: pip install numpy")
        exit(1)
    
    # Test individual components
    component_ok = test_individual_encoding()
    
    # Test full compatibility 
    if component_ok:
        results = test_tl_keylog_compatibility()
        
        # Hiển thị expected TL outputs để so sánh
        compare_with_tl_expected()
    
    print("\n" + "=" * 60)
    print("🏁 Test hoàn thành! Kiểm tra kết quả ở trên.")