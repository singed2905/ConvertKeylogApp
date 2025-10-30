# Hướng Dẫn Sử Dụng ConvertKeylogApp

Tài liệu này hướng dẫn sử dụng nhanh cho 2 chế độ chính: Equation Mode và Polynomial Mode. Ứng dụng hỗ trợ cả nhập thủ công và xử lý Excel hàng loạt.

## 1) Cài đặt & Khởi động

- Yêu cầu: Python 3.9+, pip, quyền đọc/ghi file
- Cài thư viện:
  - pip install -r requirements.txt (nếu có)
  - Hoặc đảm bảo có: numpy, pandas
- Chạy ứng dụng:
  - python main.py

## 2) Equation Mode (Giải hệ phương trình + Keylog TL)

### Bước 1: Chọn tham số
- Số ẩn: 2 / 3 / 4
- Phiên bản máy: fx799, fx800, fx801, fx802, fx803

### Bước 2: Nhập dữ liệu
- Nhập từng phương trình theo format: a11,a12,...,c1 (cách nhau bằng dấu phẩy)
- Hỗ trợ biểu thức: sqrt(9), sin(pi/2), 2^3, log(10), ln(2), pi
- Ô trống sẽ tự động điền 0

Ví dụ hệ 3 ẩn:
- PT1: 2,1,-1,8
- PT2: -3,-1,2,-11
- PT3: -2,1,2,-3

### Bước 3: Xử lý & Kết quả
- Bấm “🚀 Xử lý & Mã hóa”
- KẾT QUẢ NGHIỆM: Hiển thị “Hệ vô nghiệm hoặc vô số nghiệm” (theo yêu cầu mới)
- KẾT QUẢ MÃ HÓA: Hiển thị từng hệ số encode dạng lưới
- KẾT QUẢ TỔNG: Luôn sinh keylog TL (kể cả solve fail)
- Bấm “📋 Copy Kết Quả” để copy keylog vào clipboard

### Bước 4: Export Excel
- Bấm “💾 Xuất Excel”
- File kết quả gồm: số ẩn, version, đầu vào, nghiệm, danh sách encoded coefficients, keylog tổng

### Import Excel (Batch)
- “📝 Tạo Template” → tạo file mẫu
- “📁 Import Excel” → chọn file cần xử lý
- “🔥 Xử lý File Excel” → xuất file kết quả
- Gợi ý: File >100MB sẽ bật cảnh báo RAM, app hỗ trợ chunking tự động

## 3) Polynomial Mode (Polynomial + Keylog)

### Bước 1: Chọn tham số
- Bậc: 2 / 3 / 4
- Phiên bản máy: fx799, fx991, fx570, fx580, fx115

### Bước 2: Nhập hệ số
- Dạng bậc 2: a, b, c
- Dạng bậc 3: a, b, c, d
- Dạng bậc 4: a, b, c, d, e
- Hỗ trợ biểu thức: sqrt(), sin(), cos(), log(), ln, pi, ^

### Bước 3: Xử lý & Kết quả
- Bấm “🚀 Giải & Mã hóa”
- Nghiệm: Hiển thị tất cả nghiệm (thực/phức) dạng đẹp
- Keylog: Multi-version prefix (P2=/EQN2=/POL2=/POLY2=/QUAD= ...)

### Bước 4: Template & Export
- “📝 Tạo Template” với 3 sheet: Input, Examples, Instructions
- “💾 Export Excel” xuất đầy đủ input, nghiệm, keylog, encoded coefficients

## 4) Lưu ý nhập liệu
- Dùng dấu phẩy để phân tách hệ số
- Với biểu thức, cần đóng ngoặc đầy đủ: sqrt(9), sin(pi/2)
- Tránh để nhiều hệ số 0 dẫn tới ma trận phụ thuộc (Equation Mode vẫn sinh keylog)

## 5) Khắc phục sự cố
- Không sinh keylog: Kiểm tra ký tự lạ ngoài mapping TL
- File Excel lớn: Đóng bớt ứng dụng khác, đảm bảo còn RAM trống
- Lỗi font Flexio: App tự fallback sang Courier New

## 6) FAQ nhanh
- Q: Tại sao nghiệm luôn hiện “Hệ vô nghiệm hoặc vô số nghiệm”?  
  A: Đây là behavior theo yêu cầu: Nghiệm không ảnh hưởng keylog; keylog luôn được sinh.
- Q: Có thể chỉ copy keylog mà không xem nghiệm?  
  A: Có, keylog luôn hiển thị ở phần “KẾT QUẢ TỔNG”.
- Q: Polynomial có hỗ trợ nghiệm phức?  
  A: Có, định dạng a ± bi với độ chính xác cấu hình trong service.

## 7) Liên hệ & đóng góp
- Issues/feedback: tạo issue trên repository
- Đóng góp code: fork repo, tạo PR với mô tả thay đổi rõ ràng
