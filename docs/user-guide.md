# ConvertKeylogApp v2.0 - Hướng Dẫn Sử Dụng

## 📋 MỤC LỤC

1. [Cài đặt và Khởi động](#1-cài-đặt-và-khởi-động)
2. [Geometry Mode - Hướng dẫn chi tiết](#2-geometry-mode---hướng-dẫn-chi-tiết)
3. [Equation Mode - Hướng dẫn](#3-equation-mode---hướng-dẫn)
4. [Polynomial Mode - Hướng dẫn](#4-polynomial-mode---hướng-dẫn)
5. [Excel Processing - Hướng dẫn nâng cao](#5-excel-processing---hướng-dẫn-nâng-cao)
6. [Troubleshooting - Xử lý sự cố](#6-troubleshooting---xử-lý-sự-cố)

---

## 1. CÀI ĐẶT VÀ KHỚI ĐỘNG

### 1.1 Yêu cầu hệ thống
- **Python**: Phiên bản 3.7 trở lên
- **Hệ điều hành**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **RAM**: Tối thiểu 4GB (khuyên nghị 8GB cho Excel lớn)
- **Dung lượng**: 200MB trống

### 1.2 Cài đặt dependencies
```bash
# Mở terminal/command prompt và chạy:
pip install pandas openpyxl tkinter psutil

# Hoặc sử dụng requirements.txt:
pip install -r requirements.txt
```

### 1.3 Khởi động ứng dụng
```bash
# Di chuyển đến thư mục project:
cd ConvertKeylogApp

# Khởi động ứng dụng:
python main.py
```

### 1.4 Giao diện màn hình chính
Sau khi khởi động, bạn sẽ thấy màn hình chính với 3 nút mode:
- 🧮 **Geometry Mode** - Tính toán hình học
- 📐 **Equation Mode** - Giải hệ phương trình  
- 🔢 **Polynomial Mode** - Giải phương trình đa thức

---

## 2. GEOMETRY MODE - HƯỚNG DẮN CHI TIẾT

### 2.1 Khởi động Geometry Mode
1. Từ màn hình chính, click **"🧮 Geometry Mode"**
2. Cửa sổ Geometry sẽ mở với giao diện hoàn chỉnh

### 2.2 Giao diện Geometry Mode

**Header Section:**
- 🧮 Logo và title "Geometry v2.1 - Anti-Crash! 💪"
- **Phép toán**: Dropdown chọn phép toán (Tương giao, Khoảng cách, v.v.)
- **Phiên bản**: Dropdown chọn phiên bản máy tính (fx799, fx800, v.v.)
- **Status indicators**: Excel, Memory, Service status

**Input Section:**
- **Chọn nhóm A**: Dropdown chọn hình dạng cho đối tượng A
- **Chọn nhóm B**: Dropdown chọn hình dạng cho đối tượng B (ẩn khi không cần)
- **Input panels**: Các ô nhập liệu tương ứng với hình dạng đã chọn

**Result Section:**
- **Result Display**: Hiển thị kết quả mã hóa (1 dòng, font Flexio)
- **Action Buttons**: Các nút chức năng tương ứng với chế độ

### 2.3 Manual Mode - Tính toán thủ công

#### Bước 1: Chọn phép toán
1. Click dropdown **"Phép toán"** ở header
2. Chọn một trong 5 phép toán:
   - **Tương giao**: Tìm giao điểm/giao tuyến giữa 2 hình
   - **Khoảng cách**: Tính khoảng cách giữa 2 hình
   - **Diện tích**: Tính diện tích 1 hình phẳng (chỉ cần nhóm A)
   - **Thể tích**: Tính thể tích 1 khối (chỉ cần nhóm A)
   - **PT đường thẳng**: Tìm phương trình đường thẳng

💡 **Lưu ý**: Khi chọn "Diện tích" hoặc "Thể tích", dropdown nhóm B sẽ tự động ẩn.

#### Bước 2: Chọn hình dạng
1. **Dropdown nhóm A**: Chọn hình dạng cho đối tượng A
2. **Dropdown nhóm B**: Chọn hình dạng cho đối tượng B (nếu phép toán cần)

**5 hình dạng được hỗ trợ:**
- 🎯 **Điểm**: Cần tọa độ (x,y) hoặc (x,y,z)
- 📏 **Đường thẳng**: Cần điểm đi qua + vector hướng
- 📐 **Mặt phẳng**: Cần phương trình ax+by+cz+d=0
- ⭕ **Đường tròn**: Cần tâm (x,y) + bán kính
- 🌍 **Mặt cầu**: Cần tâm (x,y,z) + bán kính

#### Bước 3: Nhập dữ liệu

**Format nhập liệu cho từng hình:**

**🎯 Điểm:**
- **Kích thước**: Chọn 2D hoặc 3D
- **Tọa độ**: Nhập theo format `x,y` hoặc `x,y,z`
- **Ví dụ**: `1,2,3` cho điểm (1,2,3) trong không gian 3D

**📏 Đường thẳng:**
- **Điểm**: Nhập tọa độ một điểm trên đường thẳng `x,y,z`
- **Vector**: Nhập vector chỉ phương `a,b,c`
- **Ví dụ**: Điểm `0,0,0`, Vector `1,2,0`

**📐 Mặt phẳng:**
- **Hệ số a, b, c, d**: Nhập từng hệ số của phương trình `ax+by+cz+d=0`
- **Ví dụ**: a=`1`, b=`1`, c=`1`, d=`0` cho mặt phẳng `x+y+z=0`

**⭕ Đường tròn:**
- **Tâm**: Nhập tọa độ tâm `x,y`
- **Bán kính**: Nhập bán kính `r`
- **Ví dụ**: Tâm `0,0`, Bán kính `5`

**🌍 Mặt cầu:**
- **Tâm**: Nhập tọa độ tâm `x,y,z`
- **Bán kính**: Nhập bán kính `r`
- **Ví dụ**: Tâm `0,0,0`, Bán kính `3`

#### Bước 4: Thực thi tính toán
1. Sau khi nhập đầy đủ dữ liệu, các nút action sẽ xuất hiện:
   - **🔄 Xử lý Nhóm A**: Chỉ xử lý dữ liệu nhóm A
   - **🔄 Xử lý Nhóm B**: Chỉ xử lý dữ liệu nhóm B
   - **🚀 Thực thi tất cả**: Xử lý hoàn chỉnh và tạo kết quả cuối cùng ⭐
   - **💾 Xuất Excel**: Xuất kết quả ra file Excel

2. **Click "🚀 Thực thi tất cả"** để có kết quả hoàn chỉnh

#### Bước 5: Xem và copy kết quả
1. **Kết quả hiển thị**: 1 dòng mã keylog với font Flexio Fx799VN (hoặc Courier New)
2. **Nút "📋 Copy Kết Quả"**: Xuất hiện sau khi có kết quả
3. **Click Copy**: Kết quả sẽ được copy vào clipboard
4. **Paste vào máy tính**: Ctrl+V để dán vào máy tính khoa học

### 2.4 Excel Mode - Xử lý hàng loạt

#### Bước 1: Chuẩn bị file Excel
1. **Tạo template**: Click "📝 Tạo Template" để có file mẫu
2. **Hoặc chuẩn bị file Excel** theo format yêu cầu (xem section Excel Format)

#### Bước 2: Import Excel
1. **Click "📁 Import Excel"**
2. **Chọn file Excel** (.xlsx hoặc .xls)
3. **Ứng dụng sẽ**:
   - Lưu tên file và đường dẫn
   - Khóa các ô input thủ công
   - Chuyển sang chế độ import mode
   - Hiển thị nhóm nút import mode

#### Bước 3: Xử lý batch
1. **Click "🔥 Xử lý File Excel"**
2. **Chọn nơi lưu** file kết quả
3. **Progress window sẽ hiển thị**:
   - Thanh tiến độ chi tiết
   - Số dòng đã xử lý/tổng số dòng
   - Memory usage với color coding
   - Nút "🛑 Hủy" để cancel xử lý
4. **Chờ xử lý hoàn tất**
5. **Nhận thông báo** và file kết quả

#### Bước 4: Quay lại manual mode
1. **Click "↩️ Quay lại"** để thoát Excel mode
2. **Confirm** trong dialog xác nhận
3. **Ứng dụng sẽ**:
   - Mở khóa các ô input
   - Xóa dữ liệu cũ
   - Quay về manual mode
   - Ẩn nút Copy

---

## 3. EQUATION MODE - HƯỚNG DẮN

### 3.1 Khởi động Equation Mode
1. Từ màn hình chính, click **"📐 Equation Mode"**
2. Cửa sổ Equation sẽ mở với giao diện nhập hệ phương trình

### 3.2 Giao diện Equation Mode
- **Tiêu đề**: "🧠 EQUATION MODE v2.0 - GIẢI HỆ PHƯƠNG TRÌNH"
- **Thiết lập**: Dropdown chọn số ẩn (2, 3, 4) và phiên bản máy
- **Input area**: Các ô nhập hệ số phương trình
- **Result area**: 3 khu vực hiển thị kết quả

### 3.3 Cách sử dụng Equation Mode

#### Bước 1: Chọn số ẩn
1. **Dropdown "Số ẩn"**: Chọn 2, 3, hoặc 4 ẩn
2. **Các ô nhập** sẽ tự động cập nhật theo số ẩn

#### Bước 2: Nhập hệ số phương trình
**Format nhập liệu:**
- **Hệ 2 ẩn**: `a₁₁, a₁₂, c₁` cho phương trình `a₁₁x + a₁₂y = c₁`
- **Hệ 3 ẩn**: `a₁₁, a₁₂, a₁₃, c₁` cho phương trình `a₁₁x + a₁₂y + a₁₃z = c₁`
- **Hệ 4 ẩn**: `a₁₁, a₁₂, a₁₃, a₁₄, c₁` cho phương trình `a₁₁x + a₁₂y + a₁₃z + a₁₄t = c₁`

**Ví dụ hệ 2 ẩn:**
```
Phương trình 1: 2,3,7    (tương ứng 2x + 3y = 7)
Phương trình 2: 1,-1,1   (tương ứng x - y = 1)
```

#### Bước 3: Xử lý và xem kết quả
1. **Click nút xử lý** (đang phát triển)
2. **Kết quả sẽ hiển thị** trong 3 khu vực:
   - **Kết quả mã hóa**: Grid các hệ số đã mã hóa
   - **Kết quả nghiệm**: Giá trị nghiệm x, y, z, t
   - **Kết quả tổng**: Chuỗi mã hoàn chỉnh cho máy tính

---

## 4. POLYNOMIAL MODE - HƯỚNG DẮN

### 4.1 Khởi động Polynomial Mode
1. Từ màn hình chính, click **"🔢 Polynomial Mode"**
2. Cửa sổ Polynomial sẽ mở với giao diện nhập phương trình đa thức

### 4.2 Cách sử dụng Polynomial Mode

#### Bước 1: Chọn bậc phương trình
1. **Dropdown "Bậc"**: Chọn bậc 2, 3, hoặc 4
2. **Các ô nhập** sẽ cập nhật theo bậc đã chọn

#### Bước 2: Nhập hệ số
**Format cho từng bậc:**
- **Bậc 2**: `a, b, c` cho phương trình `ax² + bx + c = 0`
- **Bậc 3**: `a, b, c, d` cho phương trình `ax³ + bx² + cx + d = 0`  
- **Bậc 4**: `a, b, c, d, e` cho phương trình `ax⁴ + bx³ + cx² + dx + e = 0`

**Ví dụ phương trình bậc 2:**
```
Hệ số a: 1
Hệ số b: -5  
Hệ số c: 6
# Tương ứng phương trình: x² - 5x + 6 = 0
```

#### Bước 3: Xem kết quả
1. **Dạng phương trình**: Hiển thị phương trình đã format
2. **Nghiệm**: Hiển thị các nghiệm tìm được
3. **Mã keylog**: Chuỗi mã cho máy tính

---

## 5. EXCEL PROCESSING - HƯỚNG DẮN NÂNG CAO

### 5.1 Chuẩn bị file Excel

#### Template được khuyên nghị:
1. **Vào Geometry Mode**
2. **Chọn phép toán và hình dạng** bạn muốn xử lý
3. **Chuyển sang Import mode**: Click "📁 Import Excel"
4. **Tạo template**: Click "📝 Tạo Template"
5. **Lưu file template** và điền dữ liệu

#### Hoặc tạo thủ công theo format:

**🎯 Điểm + Điểm:**
| data_A | data_B | keylog |
|---------|---------|---------|
| 1,2     | 3,4     | (để trống) |
| 0,0,0   | 1,1,1   | (để trống) |

**📏 Đường thẳng + Đường thẳng:**
| d_P_data_A | d_V_data_A | d_P_data_B | d_V_data_B | keylog |
|-------------|-------------|-------------|-------------|---------|
| 0,0,0       | 1,0,0       | 1,1,1       | 0,1,0       | (để trống) |

**📐 Mặt phẳng + Mặt phẳng:**
| P1_a | P1_b | P1_c | P1_d | P2_a | P2_b | P2_c | P2_d | keylog |
|------|------|------|------|------|------|------|------|---------|
| 1    | 1    | 1    | 0    | 2    | 1    | 3    | 4    | (để trống) |

### 5.2 Import và xử lý Excel

#### Import file:
1. **Click "📁 Import Excel"**
2. **Chọn file Excel** từ file browser
3. **Ứng dụng sẽ validate**:
   - File extension (.xlsx, .xls)
   - File tồn tại và đọc được
   - Lưu tên file (không đọc content ngay)

#### Xử lý file:
1. **Click "🔥 Xử lý File Excel"**
2. **Chọn nơi lưu** file output
3. **Progress window xuất hiện** với:
   - Thanh tiến độ determinate (0-100%)
   - Label hiển thị "Đang xử lý: X/Y dòng"
   - Memory monitor với color coding
   - Nút "🛑 Hủy" để cancel

#### Theo dõi progress:
- **🟢 Memory OK** (<500MB): Màu xanh
- **🟡 Memory Medium** (500-800MB): Màu cam  
- **🔴 Memory High** (>800MB): Màu đỏ
- **Hủy xử lý**: Click "🛑 Hủy" nếu cần dừng

#### Kết quả:
- **Success popup**: Thống kê số dòng thành công/lỗi
- **Output file**: File Excel với cột keylog đã điền
- **Log display**: Hiển thị tóm tắt trong result area

### 5.3 Các chức năng Excel khác

**📁 Import File Khác:**
- Import file Excel khác để thay thế file hiện tại
- Thực hiện tương tự quy trình import thông thường

**📝 Tạo Template:**
- Tạo file Excel mẫu theo hình dạng đã chọn
- File chứa headers đúng format và 1-2 dòng dữ liệu mẫu
- Hỗ trợ tất cả combinations của 5 hình dạng

**↩️ Quay lại:**
- Thoát Excel mode, quay về manual mode
- Mở khóa input fields, clear dữ liệu cũ
- Ẩn nút Copy, hiển thị lại nút manual mode

---

## 6. TROUBLESHOOTING - XỬ LÝ SỰ CỐ

### 6.1 Lỗi khởi động

**❌ "GeometryService không khởi tạo được"**
- **Nguyên nhân**: Thiếu dependencies hoặc file config
- **Giải pháp**: 
  ```bash
  pip install pandas openpyxl psutil
  ```
  Kiểm tra thư mục `config/` có đầy đủ files

**❌ "Import Error: No module named 'services'"**
- **Nguyên nhân**: Đang chạy từ thư mục sai
- **Giải pháp**: Chuyển đến thư mục gốc ConvertKeylogApp và chạy `python main.py`

### 6.2 Lỗi giao diện

**❌ "Font Flexio không tìm thấy"**
- **Nguyên nhân**: Máy không có font Flexio Fx799VN
- **Giải pháp**: Ứng dụng tự động fallback sang Courier New (không cần sửa)

**❌ Dropdown B không ẩn/hiện đúng**
- **Nguyên nhân**: Chọn phép toán trước khi chọn hình
- **Giải pháp**: Chọn lại phép toán hoặc refresh bằng cách đổi phép toán

### 6.3 Lỗi xử lý dữ liệu

**❌ "Lỗi xử lý nhóm A/B"**
- **Nguyên nhân**: Dữ liệu nhập không đúng format
- **Giải pháp**: 
  - Điểm: Dùng dấu phẩy ngăn cách `1,2,3`
  - Số thực: Dùng dấu chấm `.` cho phần thập phân `1.5,2.0`
  - Kiểm tra không có khoảng trắng thừa

**❌ "Không có kết quả để copy"**
- **Nguyên nhân**: Chưa chạy "🚀 Thực thi tất cả"
- **Giải pháp**: Chạy thực thi tất cả trước khi copy

### 6.4 Lỗi Excel

**❌ "Excel không đọc được"**  
- **Nguyên nhân**: File Excel bị corrupt hoặc đang được mở
- **Giải pháp**:
  - Đóng Excel nếu đang mở file
  - Kiểm tra file không bị corrupt
  - Thử export lại từ Excel

**❌ "Memory cao trong khi xử lý Excel"**
- **Nguyên nhân**: File Excel quá lớn (>50MB)
- **Giải pháp**:
  - Đóng các ứng dụng khác
  - Tăng RAM nếu có thể
  - Chia file lớn thành nhiều file nhỏ
  - Sử dụng chunked processing (tự động)

**❌ "Lỗi trong quá trình xử lý Excel"**
- **Nguyên nhân**: Dữ liệu không đúng format hoặc thiếu cột
- **Giải pháp**:
  - Sử dụng template để đảm bảo format đúng
  - Kiểm tra tất cả cột required có đủ dữ liệu
  - Đảm bảo không có dòng trống ở giữa data

### 6.5 Performance Issues

**🐌 Ứng dụng chạy chậm**
- **Nguyên nhân**: Memory cao hoặc CPU overload
- **Giải pháp**:
  - Restart ứng dụng
  - Đóng các ứng dụng khác
  - Kiểm tra memory monitor để đảm bảo <500MB

**🔄 Processing bị dừng giữa chừng**
- **Nguyên nhân**: Lỗi dữ liệu hoặc memory overflow
- **Giải pháp**:
  - Click "🛑 Hủy" và restart
  - Chia file Excel thành chunks nhỏ hơn
  - Kiểm tra log errors để biết dòng nào bị lỗi

### 6.6 Liên hệ hỗ trợ

Nếu vẫn gặp vấn đề sau khi thử các giải pháp trên:

1. **GitHub Issues**: https://github.com/singed2905/ConvertKeylogApp/issues
2. **Mô tả chi tiết**: Lỗi gì, đang làm gì, file dữ liệu như thế nào
3. **Screenshots**: Chụp màn hình lỗi nếu có thể
4. **System info**: OS, Python version, RAM size

---

## 🎯 TIPS & TRICKS

### Manual Mode:
- **Dùng expressions**: Có thể nhập `sqrt(2)`, `pi/4`, `sin(30)` thay vì numbers
- **Copy nhanh**: Sau khi có kết quả, Ctrl+C cũng work (ngoài nút Copy)
- **Đổi phép toán**: Dropdown B sẽ tự động ẩn/hiện thông minh

### Excel Mode:
- **File size**: Tốt nhất <5MB, max khuyên nghị 50MB
- **Template trước**: Luôn tạo template để đảm bảo format
- **Backup dữ liệu**: Copy file gốc trước khi xử lý
- **Monitor memory**: Theo dõi màu memory để biết khi nào cần dừng

### General:
- **Restart định kỳ**: Restart app sau vài lần xử lý Excel lớn
- **Check version**: Đảm bảo chọn đúng phiên bản máy tính
- **Save work**: Xuất Excel ngay sau khi có kết quả manual

---

**📚 Hướng dẫn này cung cấp đầy đủ thông tin để sử dụng ConvertKeylogApp v2.0 hiệu quả!**

**Version**: 1.0  
**Last Updated**: October 29, 2025  
**For**: ConvertKeylogApp v2.0