# ConvertKeylogApp v2.0 - Tài liệu Mô tả Project

## 1. GIỚI THIỆU TỔNG QUAN

### 1.1 Tên dự án
**ConvertKeylogApp v2.0** - Ứng dụng chuyển đổi và mã hóa dữ liệu toán học

### 1.2 Mục tiêu
ConvertKeylogApp là một ứng dụng desktop được phát triển bằng Python với giao diện Tkinter, được thiết kế nhằm:
- Chuyển đổi các bài toán toán học phức tạp thành mã keylog tương thích với máy tính khoa học
- Hỗ trợ xử lý hàng loạt dữ liệu thông qua tích hợp Excel
- Cung cấp giao diện thân thiện và dễ sử dụng cho người dùng cuối

### 1.3 Đối tượng sử dụng
- Sinh viên, học sinh cần giải bài tập toán học
- Giáo viên, giảng viên cần công cụ hỗ trợ giảng dạy
- Người làm công việc kỹ thuật cần tính toán nhanh
- Người dùng cần xử lý dữ liệu toán học hàng loạt

## 2. TÍNH NĂNG CHÍNH

### 2.1 Geometry Mode (Chế độ Hình học)
**Trạng thái**: Production Ready ✅

**Tính năng chi tiết:**
- **5 Hình học cơ bản được hỗ trợ:**
  - Điểm (Point): Tọa độ 2D/3D
  - Đường thẳng (Line): Điểm + Vector hướng
  - Mặt phẳng (Plane): Phương trình ax+by+cz+d=0
  - Đường tròn (Circle): Tâm + Bán kính
  - Mặt cầu (Sphere): Tâm + Bán kính

- **5 Phép toán được hỗ trợ:**
  - Tương giao (Intersection): Tìm giao điểm/giao tuyến
  - Khoảng cách (Distance): Tính khoảng cách giữa các hình
  - Diện tích (Area): Tính diện tích hình phẳng
  - Thể tích (Volume): Tính thể tích khối
  - Phương trình đường thẳng (Line Equation): Tìm phương trình

- **Chế độ xử lý:**
  - **Manual Mode**: Nhập dữ liệu thủ công, tính toán từng bài
  - **Excel Mode**: Import Excel, xử lý hàng loạt, xuất kết quả

### 2.2 Equation Mode (Chế độ Phương trình)
**Trạng thái**: Giao diện sẵn sàng ⚠️

**Tính năng:**
- Giải hệ phương trình tuyến tính 2, 3, 4 ẩn
- Hỗ trợ biểu thức phức tạp (sin, cos, sqrt, log, ^)
- Mã hóa hệ số tự động thành keylog
- Hiển thị nghiệm và mã hóa kết quả

### 2.3 Polynomial Equation Mode (Chế độ Phương trình Đa thức)
**Trạng thái**: Giao diện sẵn sàng ⚠️

**Tính năng:**
- Giải phương trình đa thức bậc 2, 3, 4
- Hiển thị dạng chuẩn phương trình
- Tìm nghiệm thực và phức
- Mã hóa keylog chuyên dụng

## 3. KIẾN TRÚC SYSTEM

### 3.1 Kiến trúc tổng thể
ConvertKeylogApp sử dụng kiến trúc **Service-Based** với các layer rõ ràng:

```
┌─────────────────────────────────────┐
│           Presentation Layer         │
│        (Views - Tkinter UI)         │
├─────────────────────────────────────┤
│           Business Logic Layer       │
│          (Services)                 │
├─────────────────────────────────────┤
│           Data Layer                │
│     (Models + Excel Processing)     │
├─────────────────────────────────────┤
│           Configuration Layer       │
│        (JSON Config Files)         │
└─────────────────────────────────────┘
```

### 3.2 Chi tiết các layer

**Presentation Layer** (`views/`):
- `main_view.py`: Màn hình chọn chế độ chính
- `geometry_view.py`: Giao diện Geometry Mode (1366 dòng)
- `equation_view.py`: Giao diện Equation Mode (300 dòng)
- `polynomial_equation_view.py`: Giao diện Polynomial Mode

**Business Logic Layer** (`services/`):
- `geometry/geometry_service.py`: Core geometry processing
- `geometry/mapping_adapter.py`: LaTeX to calculator encoding
- `excel/excel_processor.py`: Excel batch processing logic

**Data Layer** (`services/geometry/models/`):
- Point, Line, Plane, Circle, Sphere models
- Relationship và operation definitions

**Configuration Layer** (`config/`):
- Mode-based configuration system
- Version-specific calculator configs
- Operation mappings và encoding rules

### 3.3 Design Patterns sử dụng

1. **Service Pattern**: Logic business tách biệt trong services
2. **Adapter Pattern**: MappingAdapter chuyển đổi LaTeX sang calculator format
3. **Observer Pattern**: UI components lắng nghe state changes
4. **Template Method**: Excel processing workflow có thể override
5. **Factory Pattern**: Tạo geometry models dựa trên type

## 4. LUỒNG HOẠT ĐỘNG

### 4.1 Manual Mode Workflow

```
Start → Chọn Mode → Chọn Operation → Chọn Shapes → 
Input Data → Validate → Process → Generate Keylog → 
Display Result → Copy to Clipboard → End
```

### 4.2 Excel Mode Workflow

```
Start → Chọn Mode → Chọn Operation → Import Excel → 
Validate File → Lock Manual Inputs → Process Batch → 
Progress Tracking → Memory Monitoring → Generate Output → 
Export Excel → Display Summary → End
```

### 4.3 Error Handling Flow

```
Error Occurred → Log Error → User Notification → 
Cleanup Resources → Reset State → Ready for Next Operation
```

## 5. TECHNICAL SPECIFICATIONS

### 5.1 Công nghệ sử dụng
- **Language**: Python 3.7+
- **GUI Framework**: Tkinter (built-in)
- **Excel Processing**: pandas + openpyxl
- **Memory Monitoring**: psutil
- **Math Processing**: Built-in math module + custom algorithms

### 5.2 System Requirements
- **Minimum**: Python 3.7+, 4GB RAM, 100MB disk space
- **Recommended**: Python 3.9+, 8GB RAM, 500MB disk space
- **Excel Support**: Microsoft Excel 2010+ formats (.xlsx, .xls)

### 5.3 Performance Metrics
- **Manual Mode**: <1s response time cho single calculation
- **Excel Mode**: ~100-500 rows/second tùy theo complexity
- **Memory Usage**: <500MB cho file <5MB, chunked processing cho file lớn hơn
- **File Size Support**: Lý thuyết không giới hạn với chunked processing

## 6. ARCHITECTURE DECISIONS

### 6.1 Tại sao chọn Tkinter?
- **Built-in**: Không cần cài đặt thêm dependencies
- **Cross-platform**: Chạy trên Windows, Linux, macOS
- **Lightweight**: Phù hợp cho desktop application
- **Customizable**: Đủ flexible cho complex UI

### 6.2 Tại sao Service-Based Architecture?
- **Separation of Concerns**: UI logic tách biệt business logic
- **Testability**: Dễ viết unit test cho từng service
- **Maintainability**: Dễ maintain và extend features
- **Reusability**: Services có thể dùng lại cho các UI khác

### 6.3 Config System Design
- **Mode-based**: Mỗi mode có config riêng biệt
- **JSON Format**: Dễ đọc, dễ edit, dễ parse
- **Hierarchical**: Common config + mode-specific config
- **Version Support**: Multi-version calculator support

## 7. FUTURE DEVELOPMENT

### 7.1 Short-term Goals (1-3 tháng)
- ✅ Complete Equation Mode logic integration
- ✅ Complete Polynomial Mode logic integration  
- ✅ Add comprehensive unit tests
- ✅ Performance optimization cho Excel processing
- ✅ Add more calculator versions support

### 7.2 Long-term Goals (6-12 tháng)
- 🔄 Web version với Flask/Django
- 🔄 API endpoints cho third-party integration
- 🔄 Database support cho lưu trữ history
- 🔄 Plugin system cho custom operations
- 🔄 Multi-language support

### 7.3 Technical Debt
- Refactor monolithic view files thành components
- Add comprehensive error logging
- Implement proper configuration validation
- Add automated testing pipeline

## 8. DEPLOYMENT & MAINTENANCE

### 8.1 Deployment Process
1. **Development**: Local development với Python virtual environment
2. **Testing**: Automated testing với pytest framework
3. **Packaging**: PyInstaller để tạo executable
4. **Distribution**: GitHub releases với pre-built binaries

### 8.2 Maintenance Strategy
- **Monthly releases** với bug fixes và minor improvements
- **Quarterly major updates** với new features
- **Community feedback** integration qua GitHub Issues
- **Backward compatibility** guarantee trong major versions

## 9. RISK ASSESSMENT

### 9.1 Technical Risks
- **Memory Issues**: Excel files quá lớn có thể gây crash → Chunked processing
- **Font Dependency**: Flexio font có thể không có → Fallback font system
- **Cross-platform Issues**: Different OS behaviors → Extensive testing

### 9.2 User Experience Risks
- **Learning Curve**: Complex UI cho new users → Comprehensive documentation
- **Data Loss**: Excel processing errors → Backup và validation systems
- **Performance**: Slow processing cho large files → Progress tracking và optimization

## 10. SUCCESS METRICS

### 10.1 Technical Metrics
- **Code Quality**: Maintainability Index > 80
- **Test Coverage**: > 85% line coverage
- **Performance**: < 2s response time cho 95% operations
- **Memory Efficiency**: < 500MB usage cho 95% use cases

### 10.2 User Metrics
- **Ease of Use**: < 5 minutes để complete first calculation
- **Error Rate**: < 5% failed operations
- **User Satisfaction**: > 4.0/5.0 rating từ feedback
- **Adoption**: Steady growth trong target user base

---

**Document Version**: 1.0  
**Last Updated**: October 29, 2025  
**Author**: ConvertKeylogApp Development Team