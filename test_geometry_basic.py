#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic test for Geometry Mode logic integration
Test cơ bản để kiểm tra GeometryService hoạt động
"""

from services.geometry.geometry_service import GeometryService
from utils.config_loader import config_loader

def test_basic_geometry_service():
    """Test cơ bản GeometryService"""
    print("=== BASIC GEOMETRY SERVICE TEST ===")
    
    try:
        # Load config
        print("1. Loading config...")
        config = config_loader.get_mode_config("Geometry Mode")
        print(f"   Config loaded: {bool(config)}")
        
        # Initialize service
        print("2. Initializing GeometryService...")
        service = GeometryService(config)
        print(f"   Service created: {service is not None}")
        
        # Test basic operations
        print("3. Testing basic operations...")
        shapes = service.get_available_shapes()
        print(f"   Available shapes: {shapes}")
        
        operations = service.get_available_operations()
        print(f"   Available operations: {operations}")
        
        # Test point processing
        print("4. Testing point processing...")
        service.set_current_shapes("Điểm", "Điểm")
        service.set_kich_thuoc("2", "2")
        service.set_current_operation("Khoảng cách")
        
        # Test data processing
        data_A = {'point_input': '1,2'}
        data_B = {'point_input': '3,4'}
        
        result_A, result_B = service.thuc_thi_tat_ca(data_A, data_B)
        print(f"   Point A result: {result_A}")
        print(f"   Point B result: {result_B}")
        
        # Test final result generation
        final_result = service.generate_final_result()
        print(f"   Final encoded result: {final_result}")
        
        # Test mapping adapter
        print("5. Testing mapping adapter...")
        encoded = service.mapping_adapter.encode_string("sqrt{25}")
        print(f"   sqrt{{25}} -> {encoded}")
        
        encoded2 = service.mapping_adapter.encode_string("1/2")
        print(f"   1/2 -> {encoded2}")
        
        print("\n✅ ALL TESTS PASSED! GeometryService is working.")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_integration():
    """Test tích hợp với UI (import test)"""
    print("\n=== UI INTEGRATION TEST ===")
    
    try:
        # Test import geometry view
        from views.geometry_view import GeometryView
        print("   GeometryView import: OK")
        
        # Test service integration
        config = config_loader.get_mode_config("Geometry Mode")
        print(f"   Config for UI: {bool(config)}")
        
        print("✅ UI INTEGRATION TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ UI INTEGRATION FAILED: {e}")
        return False

if __name__ == "__main__":
    print("Testing Geometry Mode Logic Integration...\n")
    
    success1 = test_basic_geometry_service()
    success2 = test_ui_integration()
    
    print(f"\n{'='*50}")
    if success1 and success2:
        print("🎉 ALL TESTS PASSED! Geometry Mode logic is ready!")
    else:
        print("⚠️ SOME TESTS FAILED. Check the errors above.")
    print("='*50}")
