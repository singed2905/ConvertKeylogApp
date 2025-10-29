# ConvertKeylogApp

Giao diện được chuyển từ dự án TL, chỉ giữ phần UI (không kèm logic). Cấu trúc thư mục gọn gàng hơn.

## Cấu trúc
- main.py: entry point
- views/: giao diện Tkinter
  - main_view.py: màn hình chọn chế độ
  - geometry_view.py: giao diện Geometry Mode (UI only)
  - equation_view.py: giao diện Equation Mode (UI only)
  - polynomial_equation_view.py: giao diện Polynomial Equation Mode (UI only)
- config/modes.json: danh sách chế độ
- utils/file_utils.py: tiện ích đọc file cấu hình

## Tính năng

### 3 chế độ của TL đã được chuyển đổi:

1. **Geometry Mode** - Giao diện xử lý hình học
   - Dropdown chọn nhóm A/B (diểm, đường thẳng, mặt phẳng, đường tròn, mặt cầu)
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
- Layout và màu sắc giữa nguyên từ TL
- Cấu trúc thư mục được tối ưu hóa
