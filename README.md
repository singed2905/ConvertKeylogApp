# ConvertKeylogApp v2.0

Giao diện được chuyển từ dự án TL, chỉ giữ phần UI (không kèm logic). Cấu trúc thư mục và config được tối ưu hóa theo từng mode.

## Cấu trúc mới

```
ConvertKeylogApp/
├── main.py                     # Entry point
├── views/                      # Giao diện Tkinter
│   ├── main_view.py            # Màn hình chọn chế độ (cập nhật)
│   ├── geometry_view.py        # Giao diện Geometry Mode
│   ├── equation_view.py        # Giao diện Equation Mode
│   └── polynomial_equation_view.py # Giao diện Polynomial Mode
│
├── config/                     # Cấu hình theo mode
│   ├── common/                 # Config chung
│   │   ├── modes.json          # Danh sách các chế độ
│   │   ├── versions.json       # Danh sách phiên bản máy tính
│   │   └── version_mapping.json # Ánh xạ phiên bản
│   │
│   ├── geometry_mode/          # Config cho Geometry Mode
│   │   ├── geometry_excel_mapping.json
│   │   └── geometry_operations.json
│   │
│   ├── equation_mode/          # Config cho Equation Mode
│   │   ├── equation_prefixes.json
│   │   └── equation_excel_mapping.json
│   │
│   ├── polynomial_mode/        # Config cho Polynomial Mode
│   │   ├── polynomial_mapping.json
│   │   └── math_replacements.json
│   │
│   └── version_configs/        # Cấu hình theo phiên bản
│       ├── fx799_config.json
│       └── fx880_config.json
│
└── utils/
    ├── file_utils.py           # Tiện ích đọc file (cũ)
    └── config_loader.py        # Utility load config mới
```

## Tính năng

### 3 chế độ của TL đã được chuyển đổi:

1. **Geometry Mode** - Giao diện xử lý hình học
   - Dropdown chọn nhóm A/B (điểm, đường thẳng, mặt phẳng, đường tròn, mặt cầu)
   - Phép toán (tương giao, khoảng cách, diện tích, thể tích)
   - Nhập toạ độ, phương trình
   - Phiên bản máy tính

2. **Equation Mode** - Giao diện giải hệ phương trình
   - Chọn số ẩn (2, 3, 4)
   - Nhập hệ số phương trình
   - Hiển thị kết quả mã hóa
   - Kết quả nghiệm và tổng

3. **Polynomial Equation Mode** - Giao diện giải phương trình bậc cao
   - Chọn bậc phương trình (2, 3, 4)
   - Nhập hệ số theo bậc
   - Hiển thị dạng phương trình
   - Kết quả nghiệm chi tiết

## 🎆 Tính năng mới trong v2.0

### Cấu trúc Config tối ưu
- **Tách biệt theo mode**: Mỗi mode có config riêng biệt
- **Load tối ưu**: Chỉ load config cần thiết cho mode đang sử dụng
- **Cache thông minh**: Config được cache để tăng hiệu suất
- **Hỗ trợ nhiều phiên bản**: Cấu hình riêng cho từng phiên bản máy tính

### ConfigLoader Class
- `config_loader.get_mode_config(mode)` - Load toàn bộ config cho 1 mode
- `config_loader.load_geometry_config(name)` - Load config geometry cụ thể
- `config_loader.load_equation_config(name)` - Load config equation cụ thể
- `config_loader.load_polynomial_config(name)` - Load config polynomial cụ thể
- `config_loader.get_available_modes()` - Lấy danh sách modes
- `config_loader.get_available_versions()` - Lấy danh sách versions

## Chạy thử

```bash
python main.py
```

- Chọn chế độ từ dropdown
- Bấm "Mở chế độ" để xem giao diện
- Tất cả chức năng chỉ là demo UI, không có logic xử lý

## Lưu ý

- Đây chỉ là **giao diện UI** (không có logic xử lý)
- Tất cả các nút sẽ hiển thị thông báo "Chức năng đang phát triển"
- Layout và màu sắc giữ nguyên từ TL
- Cấu trúc thư mục được tối ưu hóa theo mode

## Migration từ v1.0

Nếu bạn đang sử dụng phiên bản cũ:
1. File `config/modes.json` cũ vẫn hoạt động nhưng không được khuyến khích
2. Nên sử dụng cấu trúc mới `config/common/modes.json`
3. Các view sẽ nhận config qua tham số constructor

## Changelog v2.0

### ✨ Added
- Cấu trúc config mới tách theo mode (11 files JSON)
- ConfigLoader class với cache và lazy loading
- Hỗ trợ multi-version calculator configs
- Geometry operations definitions (22 combinations)
- Enhanced equation mapping (2 methods)
- LaTeX to calculator symbol mapping
- Math expression replacements cho polynomial mode

### 🔄 Changed  
- main_view.py sử dụng ConfigLoader thay vì FileUtils
- Views nhận config qua constructor parameter
- Footer hiển thị thông tin version mới

### 📎 Deprecated
- `utils/file_utils.py` vẫn giữ để backward compatibility
- File `config/modes.json` gốc (nên dùng `config/common/modes.json`)

---

**Tách từ**: [TL Repository](https://github.com/singed2905/TL)  
**Version**: 2.0 (2025-10-29)  
**Config Structure**: Restructured by Mode  
**Language**: Python 100%
