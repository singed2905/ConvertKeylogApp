# Hướng Dẫn Sử Dụng ConvertKeylogApp (VI)

[Phiên bản chính thức]

(Đây là bản di chuyển từ USAGE_GUIDE_VI.md ở root)

Tài liệu này hướng dẫn sử dụng nhanh cho 2 chế độ chính: Equation Mode và Polynomial Mode. Ứng dụng hỗ trợ cả nhập thủ công và xử lý Excel hàng loạt.

## 1) Cài đặt & Khởi động
- Python 3.9+, pip
- pip install numpy pandas
- python main.py

## 2) Equation Mode (Giải hệ + Keylog TL)
1) Chọn số ẩn (2/3/4) và phiên bản
2) Nhập từng phương trình dạng: a11,a12,…,c1 (dùng dấu phẩy)
3) Biểu thức hỗ trợ: sqrt(9), sin(pi/2), 2^3, log(10), ln(2), pi
4) Bấm “🚀 Xử lý & Mã hóa”
5) KẾT QUẢ NGHIỆM: “Hệ vô nghiệm hoặc vô số nghiệm” (nếu solve fail hoặc det≈0)
6) KẾT QUẢ TỔNG: Luôn sinh keylog TL để copy/export

Batch Excel:
- “📝 Tạo Template” → “📁 Import Excel” → “🔥 Xử lý File Excel” → “💾 Xuất Excel”

## 3) Polynomial Mode (Polynomial + Keylog)
1) Chọn bậc (2/3/4) và phiên bản
2) Nhập hệ số theo degree (3/4/5 hệ số)
3) “🚀 Giải & Mã hóa” → nghiệm (thực/phức) + keylog multi-version
4) Template 3 sheet + Export Excel đầy đủ

## 4) Lưu ý nhập liệu
- Dấu phẩy phân tách
- Đóng ngoặc đầy đủ: sqrt(9), sin(pi/2)
- Equation Mode: vẫn sinh keylog nếu hệ suy biến

## 5) Khắc phục sự cố
- Không có keylog: kiểm tra ký tự ngoài mapping TL
- Excel lớn: đảm bảo RAM, app có cảnh báo >100MB và xử lý chunk
- Thiếu font Flexio: app tự fallback Courier New

## 6) FAQ
- Vì sao nghiệm luôn “vô nghiệm/vô số nghiệm”? → Behavior mới, keylog không phụ thuộc nghiệm
- Có thể chỉ copy keylog? → Có, ở mục “KẾT QUẢ TỔNG”
- Polynomial có nghiệm phức? → Có, a ± bi, precision có thể cấu hình
