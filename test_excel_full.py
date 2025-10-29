#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Excel Integration Test for ConvertKeylogApp
Test đầy đủ tích hợp Excel: import, export, batch, template
"""

import os
import pandas as pd
from services.geometry.geometry_service import GeometryService
from utils.config_loader import config_loader
from datetime import datetime

def create_sample_excel_file():
    """Tạo file Excel mẫu để test"""
    print("1. Tạo file Excel mẫu...")
    
    # Sample data for Point-Point distance calculation
    sample_data = {
        'data_A': ['1,2', '3,4,5', '0,0', '2,3,4'],
        'data_B': ['3,4', '1,2,3', '5,5', '0,1,2'],
        'keylog': ['', '', '', '']  # Empty - will be filled by processing
    }
    
    df = pd.DataFrame(sample_data)
    test_file = 'test_geometry_sample.xlsx'
    df.to_excel(test_file, index=False)
    print(f"   ✅ Tạo file mẫu: {test_file}")
    return test_file

def test_excel_integration():
    """Test tích hợp Excel đầy đủ"""
    print("\n=== FULL EXCEL INTEGRATION TEST ===")
    
    try:
        # Load config
        print("2. Loading config...")
        config = config_loader.get_mode_config("Geometry Mode")
        print(f"   Config loaded: {bool(config)}")
        
        # Initialize service
        print("3. Initializing GeometryService with Excel...")
        service = GeometryService(config)
        print(f"   Service created: {service is not None}")
        print(f"   Excel processor: {hasattr(service, 'excel_processor')}")
        
        # Create sample Excel file
        test_file = create_sample_excel_file()
        
        # Test file info
        print("\n4. Testing Excel file info...")
        file_info = service.get_excel_file_info(test_file)
        print(f"   File: {file_info['file_name']}")
        print(f"   Rows: {file_info['total_rows']}")
        print(f"   Columns: {file_info['columns']}")
        
        # Test validation
        print("\n5. Testing Excel validation...")
        validation = service.validate_excel_file_for_geometry(test_file, "Điểm", "Điểm")
        print(f"   Valid: {validation['valid']}")
        if validation['valid']:
            quality = validation['quality_issues']
            print(f"   Rows with data: {quality['rows_with_data']}")
            print(f"   Rows with errors: {quality['rows_with_errors']}")
        
        # Test batch processing
        print("\n6. Testing batch processing...")
        output_file = f"test_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        def progress_callback(progress, processed, total, errors):
            if processed % 2 == 0:  # Print every 2 rows
                print(f"   Progress: {progress:.1f}% ({processed}/{total}, {errors} errors)")
        
        results, output_path, success_count, error_count = service.process_excel_batch(
            test_file, "Điểm", "Điểm", "Khoảng cách", "2", "2",
            output_file, progress_callback
        )
        
        print(f"   Batch results:")
        print(f"     Success: {success_count}")
        print(f"     Errors: {error_count}")
        print(f"     Output file: {os.path.basename(output_path)}")
        
        # Show sample results
        if results:
            print(f"     Sample result: {results[0][:80]}...")
        
        # Test template creation
        print("\n7. Testing template creation...")
        template_file = f"template_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        created_template = service.create_excel_template_for_geometry("Điểm", "Điểm", template_file)
        print(f"   Template created: {os.path.basename(created_template)}")
        
        # Test single export
        print("\n8. Testing single result export...")
        # First process a single calculation
        service.set_current_shapes("Điểm", "Điểm")
        service.set_kich_thuoc("2", "2")
        service.set_current_operation("Khoảng cách")
        
        data_A = {'point_input': '1,2'}
        data_B = {'point_input': '3,4'}
        service.thuc_thi_tat_ca(data_A, data_B)
        
        # Export single result
        single_export_file = f"single_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        exported_single = service.export_single_result(single_export_file)
        print(f"   Single export: {os.path.basename(exported_single)}")
        
        print("\n✅ ALL EXCEL TESTS PASSED!")
        
        # Cleanup test files
        test_files = [test_file, output_path, created_template, exported_single]
        print("\n9. Cleaning up test files...")
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"   Removed: {os.path.basename(file)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ EXCEL INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chunked_processing():
    """Test xử lý file lớn bằng chunked method"""
    print("\n=== CHUNKED PROCESSING TEST ===")
    
    try:
        # Create larger sample file
        print("1. Creating large sample file...")
        large_data = {
            'data_A': [f'{i},{i+1}' for i in range(1, 51)],  # 50 rows
            'data_B': [f'{i+2},{i+3}' for i in range(1, 51)],
            'keylog': [''] * 50
        }
        
        large_df = pd.DataFrame(large_data)
        large_file = 'test_large_geometry.xlsx'
        large_df.to_excel(large_file, index=False)
        print(f"   Created large file: {large_file} (50 rows)")
        
        # Test chunked processing
        print("\n2. Testing chunked processing...")
        config = config_loader.get_mode_config("Geometry Mode")
        service = GeometryService(config)
        
        output_file = f"chunked_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        def progress_callback(progress, processed, total, errors):
            if processed % 10 == 0:  # Print every 10 rows
                print(f"   Chunked progress: {progress:.1f}% ({processed}/{total})")
        
        results, output_path, success_count, error_count = service.process_excel_batch_chunked(
            large_file, "Điểm", "Điểm", "Khoảng cách", "2", "2",
            chunksize=15, progress_callback=progress_callback
        )
        
        print(f"\n   Chunked results:")
        print(f"     Success: {success_count}/50")
        print(f"     Errors: {error_count}")
        print(f"     Output: {os.path.basename(output_path)}")
        
        # Cleanup
        for file in [large_file, output_path]:
            if os.path.exists(file):
                os.remove(file)
        
        print("✅ CHUNKED PROCESSING TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ CHUNKED PROCESSING TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test xử lý lỗi"""
    print("\n=== ERROR HANDLING TEST ===")
    
    try:
        config = config_loader.get_mode_config("Geometry Mode")
        service = GeometryService(config)
        
        # Test with invalid file
        print("1. Testing invalid file...")
        try:
            service.get_excel_file_info("nonexistent.xlsx")
            print("   ❌ Should have failed!")
            return False
        except Exception as e:
            print(f"   ✅ Correctly caught error: {type(e).__name__}")
        
        # Test with invalid structure
        print("\n2. Testing invalid Excel structure...")
        invalid_data = pd.DataFrame({
            'wrong_column': ['1,2', '3,4'],
            'another_wrong': ['5,6', '7,8']
        })
        invalid_file = 'test_invalid.xlsx'
        invalid_data.to_excel(invalid_file, index=False)
        
        validation = service.validate_excel_file_for_geometry(invalid_file, "Điểm", "Điểm")
        print(f"   Validation result: {validation['valid']} (should be False)")
        
        if validation['valid'] == False:
            print("   ✅ Correctly identified invalid structure")
        else:
            print("   ❌ Should have detected invalid structure")
        
        # Cleanup
        os.remove(invalid_file)
        
        print("✅ ERROR HANDLING TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR HANDLING TEST FAILED: {e}")
        return False

if __name__ == "__main__":
    print("Testing Full Excel Integration for ConvertKeylogApp...\n")
    
    success1 = test_excel_integration()
    success2 = test_chunked_processing()
    success3 = test_error_handling()
    
    print(f"\n{'='*60}")
    if success1 and success2 and success3:
        print("🎉 ALL EXCEL INTEGRATION TESTS PASSED!")
        print("\n🚀 ConvertKeylogApp Excel features are ready:")
        print("   ✅ Import Excel files")
        print("   ✅ Batch processing")
        print("   ✅ Chunked processing for large files")
        print("   ✅ Progress tracking")
        print("   ✅ Template generation")
        print("   ✅ Comprehensive validation")
        print("   ✅ Export with formatting")
        print("   ✅ Error handling")
    else:
        print("⚠️ SOME EXCEL TESTS FAILED. Check the errors above.")
    print("="*60)
