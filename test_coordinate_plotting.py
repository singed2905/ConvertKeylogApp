#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test coordinate plotting feature in Geometry Mode
Kiểm tra tính năng hiển thị tọa độ trong Geometry Mode
"""

import tkinter as tk
from views.geometry_view import GeometryView
from utils.config_loader import config_loader

def test_coordinate_plotting_2d():
    """Test 2D coordinate plotting with points and circles"""
    print("=== TESTING 2D COORDINATE PLOTTING ===")
    
    root = tk.Tk()
    root.title("Test Coordinate Plotting - 2D")
    
    # Load config
    config = config_loader.get_mode_config("Geometry Mode")
    
    # Create GeometryView
    app = GeometryView(root, config)
    
    # Simulate manual input for 2D points
    print("1. Setting up 2D point distance calculation...")
    app.pheptoan_var.set("Khoảng cách")
    app.dropdown1_var.set("Điểm")
    app.dropdown2_var.set("Điểm")
    app.kich_thuoc_A_var.set("2")
    app.kich_thuoc_B_var.set("2")
    
    # Trigger UI updates
    app._on_operation_changed()
    app._on_shape_changed()
    
    print("2. Ready for manual input:")
    print("   - Nhóm A: Nhập tọa độ điểm A (ví dụ: 1,2)")
    print("   - Nhóm B: Nhập tọa độ điểm B (ví dụ: 4,6)")
    print("   - Click 'Thực thi tất cả' để thấy đồ thị")
    
    root.mainloop()

def test_coordinate_plotting_3d():
    """Test 3D coordinate plotting with spheres"""
    print("=== TESTING 3D COORDINATE PLOTTING ===")
    
    root = tk.Tk()
    root.title("Test Coordinate Plotting - 3D")
    
    # Load config
    config = config_loader.get_mode_config("Geometry Mode")
    
    # Create GeometryView
    app = GeometryView(root, config)
    
    # Simulate manual input for 3D spheres
    print("1. Setting up 3D sphere area calculation...")
    app.pheptoan_var.set("Diện tích")
    app.dropdown1_var.set("Mặt cầu")
    app.kich_thuoc_A_var.set("3")
    
    # Trigger UI updates
    app._on_operation_changed()
    app._on_shape_changed()
    
    print("2. Ready for manual input:")
    print("   - Nhóm A: Nhập tâm mặt cầu (ví dụ: 0,0,0) và bán kính (ví dụ: 5)")
    print("   - Click 'Thực thi tất cả' để thấy đồ thị 3D")
    
    root.mainloop()

def test_coordinate_plotting_lines():
    """Test coordinate plotting with lines"""
    print("=== TESTING LINE COORDINATE PLOTTING ===")
    
    root = tk.Tk()
    root.title("Test Coordinate Plotting - Lines")
    
    # Load config
    config = config_loader.get_mode_config("Geometry Mode")
    
    # Create GeometryView
    app = GeometryView(root, config)
    
    # Simulate manual input for lines
    print("1. Setting up line distance calculation...")
    app.pheptoan_var.set("Khoảng cách")
    app.dropdown1_var.set("Đường thẳng")
    app.dropdown2_var.set("Đường thẳng")
    app.kich_thuoc_A_var.set("3")
    app.kich_thuoc_B_var.set("3")
    
    # Trigger UI updates
    app._on_operation_changed()
    app._on_shape_changed()
    
    print("2. Ready for manual input:")
    print("   - Nhóm A: Điểm (ví dụ: 0,0,0), Vector (ví dụ: 1,1,1)")
    print("   - Nhóm B: Điểm (ví dụ: 1,0,0), Vector (ví dụ: 0,1,1)")
    print("   - Click 'Thực thi tất cả' để thấy đồ thị 3D với 2 đường thẳng")
    
    root.mainloop()

if __name__ == "__main__":
    print("🎯 Coordinate Plotting Feature Test")
    print("====================================")
    print("")
    print("Chọn test case:")
    print("1. Test 2D plotting (điểm, đường tròn)")
    print("2. Test 3D plotting (mặt cầu)")
    print("3. Test line plotting (đường thẳng 3D)")
    print("")
    
    try:
        choice = input("Nhập lựa chọn (1-3): ").strip()
        
        if choice == "1":
            test_coordinate_plotting_2d()
        elif choice == "2":
            test_coordinate_plotting_3d()
        elif choice == "3":
            test_coordinate_plotting_lines()
        else:
            print("Lựa chọn không hợp lệ. Chạy test 2D mặc định...")
            test_coordinate_plotting_2d()
            
    except KeyboardInterrupt:
        print("\nTest đã bị hủy.")
    except Exception as e:
        print(f"Lỗi test: {e}")
        print("\nChạy test cơ bản...")
        test_coordinate_plotting_2d()
