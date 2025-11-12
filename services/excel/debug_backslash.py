# -*- coding: utf-8 -*-
"""
DEBUG SCRIPT - Test _clean_cell_value() directly
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.excel.large_file_processor import LargeFileProcessor

def test_current_implementation():
    """Test với data thực tế"""
    
    processor = LargeFileProcessor()
    
    print("=" * 80)
    print("🧪 TESTING CURRENT IMPLEMENTATION")
    print("=" * 80)
    
    # Test case 1: Từ Excel
    test_cases = [
        {
            'name': 'Test 1: Basic LaTeX with escape',
            'input': '["35.196152423", "\\\\frac{17}{4}", "0"]',
            'expected': '35.196152423,\\frac{17}{4},0',
            'description': 'Excel có \\frac{17}{4}, Python đọc thành \\\\frac{17}{4}'
        },
        {
            'name': 'Test 2: Nested LaTeX',
            'input': '["-6", "-\\\\frac{\\\\sqrt{7}}{10}", "0"]',
            'expected': '-6,-\\frac{\\sqrt{7}}{10},0',
            'description': 'LaTeX phức tạp với căn'
        },
        {
            'name': 'Test 3: No brackets',
            'input': '\\\\frac{17}{4}',
            'expected': '\\frac{17}{4}',
            'description': 'Cell đơn không có array'
        },
        {
            'name': 'Test 4: Normal number',
            'input': '["35.196152423", "0", "0"]',
            'expected': '35.196152423,0,0',
            'description': 'Số bình thường'
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"📋 {test['name']}")
        print(f"📝 {test['description']}")
        print(f"{'-'*80}")
        
        result = processor._clean_cell_value(test['input'])
        expected = test['expected']
        passed = result == expected
        
        print(f"Input:    {repr(test['input'])}")
        print(f"Expected: {repr(expected)}")
        print(f"Got:      {repr(result)}")
        
        if not passed:
            all_passed = False
            print(f"\n❌ FAILED!")
            print(f"\nCharacter comparison:")
            print(f"Expected chars: {[c for c in expected]}")
            print(f"Got chars:      {[c for c in result]}")
            print(f"\nBackslash count:")
            print(f"Expected: {expected.count(chr(92))} backslashes")
            print(f"Got:      {result.count(chr(92))} backslashes")
            
            # Check vị trí 14-15 nếu đủ dài
            if len(result) >= 15:
                print(f"\nPosition 13-15 (0-indexed):")
                print(f"Expected: {repr(expected[13:16] if len(expected) >= 16 else expected[13:])}")
                print(f"Got:      {repr(result[13:16] if len(result) >= 16 else result[13:])}")
        else:
            print(f"\n✅ PASSED!")
    
    print(f"\n{'='*80}")
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ Method _clean_cell_value() đang hoạt động đúng")
    else:
        print("❌ SOME TESTS FAILED!")
        print("\n🔧 Cần kiểm tra lại implementation:")
        print("   1. File: services/excel/large_file_processor.py")
        print("   2. Method: _clean_cell_value()")
        print("   3. Đảm bảo có dòng: elem = elem.replace('\\\\\\\\', '\\\\')")
    print("=" * 80)
    
    return all_passed


def check_implementation():
    """Kiểm tra xem code có dòng replace không"""
    
    print("\n" + "="*80)
    print("🔍 CHECKING IMPLEMENTATION")
    print("="*80)
    
    file_path = "services/excel/large_file_processor.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if replace line exists
    has_replace_1 = "replace('\\\\\\\\', '\\\\')" in content
    has_replace_2 = 'replace("\\\\\\\\", "\\\\")' in content
    
    print(f"\n📁 File: {file_path}")
    print(f"Checking for backslash normalization...")
    
    if has_replace_1 or has_replace_2:
        print(f"✅ Found: elem.replace('\\\\\\\\', '\\\\')")
        
        # Count occurrences
        count = content.count("replace('\\\\\\\\', '\\\\')") + content.count('replace("\\\\\\\\", "\\\\")')
        print(f"   Appears {count} time(s) in code")
        
        if count >= 2:
            print(f"   ✅ Good! Should be in 2 places:")
            print(f"      1. Non-array case (single value)")
            print(f"      2. Array case (element loop)")
        else:
            print(f"   ⚠️  Warning: Only found {count} occurrence(s)")
            print(f"      Should appear 2 times!")
        
        return True
    else:
        print(f"❌ NOT FOUND: elem.replace('\\\\\\\\', '\\\\')")
        print(f"\n🔧 FIX NEEDED:")
        print(f"   Add this line in 2 places in _clean_cell_value():")
        print(f"   elem = elem.replace('\\\\\\\\', '\\\\')")
        return False


def main():
    """Main test runner"""
    
    print("\n" + "🚀"*40)
    print("DEBUG SCRIPT FOR BACKSLASH ISSUE")
    print("🚀"*40)
    
    # Step 1: Check implementation
    impl_ok = check_implementation()
    
    # Step 2: Test functionality
    test_ok = test_current_implementation()
    
    # Summary
    print("\n" + "📊"*40)
    print("SUMMARY")
    print("📊"*40)
    
    if impl_ok and test_ok:
        print("\n✅ Everything is working correctly!")
        print("   - Implementation has backslash normalization")
        print("   - All tests passed")
        print("\n🎯 If Excel output still has double backslash:")
        print("   1. Restart Python completely")
        print("   2. Clear __pycache__ folders")
        print("   3. Re-import the file")
    elif impl_ok and not test_ok:
        print("\n⚠️  Implementation looks OK but tests failed")
        print("   - Check if there are other issues")
        print("   - Debug _clean_cell_value() method")
    elif not impl_ok:
        print("\n❌ Implementation is missing backslash fix")
        print("   - Apply fix from artifact [38]")
        print("   - Add: elem = elem.replace('\\\\\\\\', '\\\\')")
    
    print("\n" + "="*80 + "\n")
    
    return impl_ok and test_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
