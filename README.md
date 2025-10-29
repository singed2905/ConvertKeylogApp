# 🧮 ConvertKeylogApp v2.0

> **Ứng dụng chuyển đổi và mã hóa dữ liệu toán học cho máy tính khoa học**

ConvertKeylogApp là một ứng dụng desktop Python với giao diện Tkinter, được thiết kế để chuyển đổi các bài toán toán học thành mã keylog phù hợp với máy tính khoa học. Ứng dụng hỗ trợ 3 chế độ tính toán chính với khả năng xử lý Excel tự động.

## ✨ **Tính năng nổi bật**

### 🎯 **Geometry Mode** - Production Ready
- **5 Hình học cơ bản**: Điểm, Đường thẳng, Mặt phẳng, Đường tròn, Mặt cầu
- **5 Phép toán**: Tương giao, Khoảng cách, Diện tích, Thể tích, Phương trình đường thẳng
- **Excel Integration**: Import/Export hàng loạt với progress tracking
- **Memory Monitoring**: Theo dõi bộ nhớ real-time với color coding
- **Template Generator**: Tạo mẫu Excel tự động

### 📐 **Equation Mode** - Giao diện sẵn sàng
- **Hệ phương trình**: Giải hệ 2, 3, 4 ẩn
- **Biểu thức phức tạp**: Hỗ trợ sin, cos, sqrt, log, ^, v.v.
- **Mã hóa tự động**: Chuyển đổi hệ số thành keylog
- **Kết quả chi tiết**: Hiển thị nghiệm và mã hóa

### 🔢 **Polynomial Equation Mode** - Giao diện sẵn sàng
- **Phương trình bậc cao**: Bậc 2, 3, 4
- **Hiển thị dạng chuẩn**: Tự động format phương trình
- **Giải nghiệm đầy đủ**: Nghiệm thực và phức
- **Mã hóa keylog**: Chuyển đổi sang định dạng máy tính

## 🚀 **Cài đặt nhanh**

### Yêu cầu hệ thống
- Python 3.7+
- Windows/Linux/macOS
- RAM: Tối thiểu 4GB (khuyến nghị 8GB cho Excel lớn)

### Cài đặt dependencies
```bash
pip install pandas openpyxl tkinter psutil
```


## 📖 **Cách sử dụng**

### 🖱️ Chế độ Thủ công (Manual Mode)
1. **Khởi động** ứng dụng với `python main.py`
2. **Chọn Geometry Mode** từ màn hình chính
3. **Chọn phép toán** (Tương giao, Khoảng cách, v.v.)
4. **Chọn hình dạng** cho nhóm A và B (nếu cần)
5. **Nhập dữ liệu** vào các trường tương ứng:
   - Điểm: `1,2,3` (tọa độ x,y,z)
   - Đường thẳng: Điểm `0,0,0` và Vector `1,0,0`
   - Mặt phẳng: Hệ số `a,b,c,d` cho phương trình `ax+by+cz+d=0`
   - Đường tròn: Tâm `0,0` và Bán kính `5`
   - Mặt cầu: Tâm `0,0,0` và Bán kính `3`
6. **Bấm "🚀 Thực thi tất cả"** để tính toán
7. **Kết quả** hiển thị 1 dòng mã keylog với font Flexio Fx799VN
8. **Bấm "📋 Copy Kết Quả"** để copy vào clipboard

### 📊 Chế độ Excel (Batch Mode)
1. **Chọn phép toán và hình dạng** như manual mode
2. **Bấm "📁 Import Excel"** để chọn file .xlsx/.xls
3. **File được import** - các trường input sẽ bị khóa
4. **Bấm "🔥 Xử lý File Excel"** để bắt đầu processing
5. **Chọn nơi lưu** file kết quả
6. **Theo dõi progress** với thanh tiến độ và memory monitor
7. **Nhận file kết quả** với cột `keylog` đã được điền

### 📝 Tạo Template Excel
1. **Chọn hình dạng** cho nhóm A và B
2. **Bấm "📝 Tạo Template"** (chỉ hiện trong import mode)
3. **Chọn nơi lưu** template
4. **Nhận file template** với format chuẩn và dữ liệu mẫu

## 📊 **Excel Format được hỗ trợ**

### Điểm + Điểm
| data_A | data_B | keylog |
|--------|--------|---------|
| 1,2    | 3,4    | (auto) |
| 3,4,5  | 1,2,3  | (auto) |

### Đường thẳng + Đường thẳng
| d_P_data_A | d_V_data_A | d_P_data_B | d_V_data_B | keylog |
|------------|------------|------------|------------|--------|
| 0,0,0      | 1,0,0      | 1,1,1      | 0,1,0      | (auto) |

### Mặt phẳng + Mặt phẳng
| P1_a | P1_b | P1_c | P1_d | P2_a | P2_b | P2_c | P2_d | keylog |
|------|------|------|------|------|------|------|------|---------|
| 1    | 1    | 1    | 0    | 2    | 1    | 3    | 4    | (auto) |

### Đường tròn + Mặt cầu
| C_data_I1 | C_data_R1 | S_data_I1 | S_data_R1 | keylog |
|-----------|-----------|-----------|-----------|--------|
| 0,0       | 5         | 0,0,0     | 3         | (auto) |

## 🏗️ **Kiến trúc ứng dụng**

```
ConvertKeylogApp/
├── main.py                    # Entry point
├── views/                     # Giao diện Tkinter
│   ├── main_view.py          # Màn hình chọn chế độ
│   ├── geometry_view.py      # Geometry Mode (Hoàn chỉnh!)
│   ├── equation_view.py      # Equation Mode
│   └── polynomial_equation_view.py
│
├── services/                  # Logic xử lý
│   ├── geometry/             # Geometry service
│   │   ├── models/           # Geometry models
│   │   ├── geometry_service.py # Core service
│   │   ├── mapping_adapter.py  # Encoding logic
│   │   └── excel_loader.py     # Excel logic
│   └── excel/                # Excel services
│       └── excel_processor.py # Excel processing
│
├── config/                   # Cấu hình theo mode
│   ├── common/              # Config chung
│   ├── geometry_mode/       # Config Geometry
│   └── version_configs/     # Config theo phiên bản
│
├── utils/                   # Tiện ích
└── tests/                   # File test
    ├── test_geometry_basic.py
    ├── test_excel_full.py
    └── quick_run_geometry.py
```

## ⚡ **Tính năng nâng cao**

### 💾 Memory Management
- **Real-time monitoring**: Theo dõi bộ nhớ liên tục
- **Color coding**: 🟢 <500MB, 🟠 500-800MB, 🔴 >800MB
- **Chunked processing**: Xử lý file lớn an toàn
- **Anti-crash system**: Tự động tối ưu khi memory cao

### 📈 Excel Processing
- **Batch processing**: Xử lý hàng nghìn dòng tự động
- **Progress tracking**: Thanh tiến độ chi tiết
- **Error handling**: Log lỗi và thống kê
- **Cancel support**: Có thể hủy xử lý bất kỳ lúc nào
- **Smart keylog detection**: Tự động tìm/tạo cột keylog

### 🎨 UI/UX Features
- **Font Flexio Fx799VN**: Chuyên dụng cho máy tính khoa học
- **Responsive interface**: Dropdown ẩn/hiện thông minh
- **Status indicators**: Excel, Service, Memory status
- **Copy to clipboard**: 1-click copy kết quả
- **Modern design**: Clean, intuitive interface

## 📋 **Phiên bản hỗ trợ**

- **fx799, fx800**: Các dòng máy tính phổ biến

## 🐛 **Troubleshooting**

### Lỗi phổ biến
- **"GeometryService không khởi tạo được"**: Kiểm tra cài đặt dependencies
- **"Font Flexio không tìm thấy"**: Ứng dụng sẽ tự động fallback sang Courier New
- **"Memory cao"**: Sử dụng chunked processing cho file Excel lớn
- **"Excel không đọc được"**: Đảm bảo file .xlsx/.xls không bị corrupt

### Performance tips
- Sử dụng template để đảm bảo format đúng
- Backup dữ liệu trước khi xử lý batch lớn

## 📜 **License**

- © Copyright 15/07/2025
- Phần mềm thuộc bản quyền của phòng KTCN-RD



---

