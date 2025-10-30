# ConvertKeylogApp v2.2 - Hướng Dẫn Sử Dụng Tổng Hợp

> Hướng dẫn đầy đủ và chi tiết sử dụng 3 modes: Equation (v2.2), Polynomial (v2.1), Geometry (v2.1)

---

## 📦 MUỤC LỤC

1. [Cài đặt & Khởi động](#1-cài-đặt--khởi-động)
2. [Equation Mode v2.2 - Hệ phương trình](#2-equation-mode-v22---hệ-phương-trình)
3. [Polynomial Mode v2.1 - Đa thức](#3-polynomial-mode-v21---đa-thức)
4. [Geometry Mode v2.1 - Hình học](#4-geometry-mode-v21---hình-học)
5. [Excel Processing - Nâng cao](#5-excel-processing---nâng-cao)
6. [Troubleshooting - Xử lý sự cố](#6-troubleshooting---xử-lý-sự-cố)

---

## 1. Cài đặt & Khởi động

### Yêu cầu hệ thống
- **Python:** 3.9+ (khuyến nghị 3.11+)
- **RAM:** Tối thiểu 4GB, khuyến nghị 8GB cho Excel lớn
- **OS:** Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Disk:** 200MB trống

### Cài đặt dependencies
```bash
pip install numpy pandas openpyxl psutil
```

### Khởi động ứng dụng
```bash
cd ConvertKeylogApp
python main.py
```

### Màn hình chính
Sau khi khởi động, chọn 1 trong 3 modes:
- 🧠 **Equation Mode v2.2** - Giải hệ phương trình
- 📈 **Polynomial Mode v2.1** - Giải phương trình đa thức
- 📐 **Geometry Mode v2.1** - Toán hình học

---

## 2. Equation Mode v2.2 - Hệ phương trình

### 2.1 Khởi động & Giao diện
1. Click **"🧠 Equation Mode"** từ main screen
2. Giao diện gồm:
   - **Header:** Số ẩn (2/3/4), Phiên bản máy (fx799-fx803)
   - **Input area:** Các ô nhập hệ số phương trình
   - **Result areas:** 3 vùng hiển thị kết quả

### 2.2 Chọn tham số
**Số ẩn:**
- **2 ẩn:** Hệ 2×2, cần 6 hệ số (2 phương trình × 3 hệ số)
- **3 ẩn:** Hệ 3×3, cần 12 hệ số (3 phương trình × 4 hệ số)
- **4 ẩn:** Hệ 4×4, cần 20 hệ số (4 phương trình × 5 hệ số)

**Phiên bản máy:** fx799 (chuẩn), fx800, fx801, fx802, fx803

### 2.3 Nhập dữ liệu
**Format:** Mỗi phương trình nhập hệ số cách nhau bằng dấu phẩy

**Ví dụ hệ 3 ẩn:**
```
PT1: 2,1,-1,8     # 2x + y - z = 8
PT2: -3,-1,2,-11  # -3x - y + 2z = -11  
PT3: -2,1,2,-3    # -2x + y + 2z = -3
```

**Biểu thức hỗ trợ:**
- `sqrt(9)`, `sin(pi/2)`, `cos(0)`, `tan(pi/4)`
- `log(10)`, `ln(2)`, `pi`, `2^3`, `1/2`
- Ô trống tự động điền `0`

### 2.4 Xử lý & Kết quả
1. **Bấm "🚀 Xử lý & Mã hóa"**
2. **Kết quả hiển thị:**
   - **KẾT QUẢ MÃ HÓA:** Grid hiển thị từng hệ số đã encode
   - **KẾT QUẢ NGHIỆM:** "Đặc biệt" luôn hiển thị "Hệ vô nghiệm hoặc vô số nghiệm" (behavior v2.2)
   - **KẾT QUẢ TỔNG:** Keylog TL format `w912=...== =` luôn được sinh
3. **Bấm "📋 Copy Kết Quả"** để copy keylog
4. **Bấm "💾 Xuất Excel"** để save kết quả

### 2.5 Excel Batch cho Equation
1. **"📝 Tạo Template"** → tạo file mẫu cho hệ n×n
2. **"📁 Import Excel"** → chọn file cần xử lý
3. **"🔥 Xử lý File Excel"** → batch processing với progress
4. File kết quả có keylog cho từng hệ

---

## 3. Polynomial Mode v2.1 - Đa thức

### 3.1 Khởi động & Giao diện
1. Click **"📈 Polynomial Mode"**
2. Giao diện hiển thị:
   - **Header:** Bậc (2/3/4), Phiên bản máy (fx799/fx991/fx570/fx580/fx115)
   - **Input section:** Nhập hệ số theo bậc
   - **Display section:** Hiển thị phương trình format chuẩn
   - **Result section:** Nghiệm + keylog

### 3.2 Chọn bậc và phiên bản
**Bậc polynomial:**
- **Bậc 2:** ax² + bx + c = 0 (3 hệ số)
- **Bậc 3:** ax³ + bx² + cx + d = 0 (4 hệ số)
- **Bậc 4:** ax⁴ + bx³ + cx² + dx + e = 0 (5 hệ số)

**Phiên bản keylog:** 
- **fx799:** P2=1=-5=6== (chuẩn Việt Nam)
- **fx991:** EQN2=1=-5=6=0 (equation solver)
- **fx570:** POL2=1=-5=6=ROOT (polynomial mode)
- **fx580:** POLY2=1=-5=6=SOLVE (extended)
- **fx115:** QUAD=1=-5=6= (compact)

### 3.3 Nhập hệ số
**Ví dụ bậc 2:** x² - 5x + 6 = 0
- Hệ số a: `1`
- Hệ số b: `-5`
- Hệ số c: `6`

**Biểu thức phức tạp:**
- `sqrt(2)`, `sin(pi/6)`, `log(100)`, `2^0.5`
- Tự động parse và tính giá trị số

### 3.4 Kết quả & Export
1. **Bấm "🚀 Giải & Mã hóa"**
2. **Kết quả:**
   - **Dạng chuẩn:** Hiển thị phương trình đã format đẹp
   - **Nghiệm:** Tất cả nghiệm (thực, phức) với format a ± bi
   - **Keylog:** Multi-version keylog theo phiên bản đã chọn
3. **Template Excel:** 3 sheet (Input/Examples/Instructions)
4. **Export Excel:** Đầy đủ input, nghiệm, keylog, encoded coefficients

---

## 4. Geometry Mode v2.1 - Hình học

### 4.1 Giao diện chính
1. Click **"📐 Geometry Mode"**
2. **Header với:**
   - Phép toán: Tương giao, Khoảng cách, Diện tích, Thể tích, PT đường thẳng
   - Phiên bản: fx799, fx800
   - Status: Excel, Memory, Service monitoring

### 4.2 5 Hình dạng hỗ trợ
**🎯 Điểm:**
- **2D:** Nhập tọa độ `x,y`
- **3D:** Nhập tọa độ `x,y,z`
- Ví dụ: `1,2,3`

**📏 Đường thẳng:**
- **Điểm:** Tọa độ 1 điểm trên đường thẳng `x,y,z`
- **Vector:** Vector chỉ phương `a,b,c`
- Ví dụ: Điểm `0,0,0`, Vector `1,2,0`

**📐 Mặt phẳng:**
- **Hệ số:** a, b, c, d cho phương trình `ax+by+cz+d=0`
- Ví dụ: a=`1`, b=`1`, c=`1`, d=`0` → mặt phẳng `x+y+z=0`

**⚫ Đường tròn:**
- **Tâm:** Tọa độ tâm `x,y`
- **Bán kính:** Nhập giá trị `r`
- Ví dụ: Tâm `0,0`, Bán kính `5`

**🌍 Mặt cầu:**
- **Tâm:** Tọa độ tâm `x,y,z`
- **Bán kính:** Nhập giá trị `r`
- Ví dụ: Tâm `0,0,0`, Bán kính `3`

### 4.3 5 Phép toán
1. **Tương giao:** Tìm giao điểm/tuyến giữa 2 hình (cần nhóm A + B)
2. **Khoảng cách:** Tính khoảng cách giữa 2 hình (cần nhóm A + B)
3. **Diện tích:** Tính diện tích hình phẳng (chỉ cần nhóm A)
4. **Thể tích:** Tính thể tích khối (chỉ cần nhóm A)
5. **PT đường thẳng:** Tìm phương trình đường thẳng

### 4.4 Manual Mode workflow
1. Chọn phép toán → dropdown nhóm B tự động ẩn/hiện
2. Chọn hình dạng nhóm A (và B nếu cần)
3. Nhập dữ liệu → các nút action xuất hiện
4. **Bấm "🚀 Thực thi tất cả"** để có kết quả hoàn chỉnh
5. Kết quả hiển thị 1 dòng keylog với font Flexio (hoặc Courier New)
6. **"📋 Copy Kết Quả"** để copy vào clipboard

---

## 5. Excel Processing - Nâng cao

### 5.1 Chuẩn bị Excel file
**Khuyến nghị dùng Template:**
1. Vào mode bất kì → chọn phép toán/hình dạng
2. **"📁 Import Excel"** → **"📝 Tạo Template"**
3. Lưu file template và điền dữ liệu theo format

**Format chuẩn theo mode:**

**Equation Mode:**
```
# Hệ 2 ẩn:
| eq1_coeffs     | eq2_coeffs     | keylog |
| 2,1,8          | 1,-1,1         |        |

# Hệ 3 ẩn:
| eq1_coeffs     | eq2_coeffs     | eq3_coeffs     | keylog |
| 2,1,-1,8       | -3,-1,2,-11    | -2,1,2,-3      |        |
```

**Polynomial Mode:**
```
# Bậc 2:
| coeff_a | coeff_b | coeff_c | keylog |
| 1       | -5      | 6       |        |
```

**Geometry Mode:**
```
# Điểm + Điểm:
| data_A | data_B | keylog |
| 1,2    | 3,4    |        |

# Đường thẳng + Đường thẳng:
| d_P_data_A | d_V_data_A | d_P_data_B | d_V_data_B | keylog |
| 0,0,0      | 1,0,0      | 1,1,1      | 0,1,0      |        |
```

### 5.2 Import & Xử lý batch
1. **Import:** Chọn file Excel → app hiển thị size, khóa manual inputs
2. **Cảnh báo file lớn:** >100MB sẽ bật warning RAM usage
3. **Xử lý:** Chọn output path → progress window với:
   - Progress bar determinate 0-100%
   - Memory monitor color-coded (🟢 <500MB, 🟡 500-800MB, 🔴 >800MB)
   - Cancel button để dừng xử lý
4. **Kết quả:** File Excel với cột keylog đã được điền

### 5.3 Performance & Memory
- **File size khuyến nghị:** <50MB cho performance tối ưu
- **Chunked processing:** Tự động cho file lớn, xử lý theo batch
- **Memory monitoring:** Real-time tracking, cảnh báo khi usage cao
- **Cancel mechanism:** Dừng xử lý bất kì lúc nào an toàn

---

## 6. Troubleshooting - Xử lý sự cố

### 6.1 Lỗi khởi động
**❌ "Service không khởi tạo được"**
```bash
pip install numpy pandas openpyxl psutil
# Kiểm tra thư mục config/ có đầy đủ files
```

**❌ "Import Error"**
- Chạy từ thư mục gốc: `cd ConvertKeylogApp && python main.py`

### 6.2 Lỗi xử lý
**❌ "Không có keylog"**
- Kiểm tra ký tự ngoài TL mapping
- Đảm bảo format đầu vào đúng (dấu phẩy, đóng ngoặc)
- Equation Mode: Vẫn sinh keylog nếu hệ suy biến

**❌ "Font Flexio không tìm thấy"**
- App tự động fallback sang Courier New (không cần sửa)

### 6.3 Lỗi Excel
**❌ "Memory cao"**
- Đóng các app khác, theo dõi memory monitor
- Dùng chunked processing (tự động cho file >100MB)
- Chia file lớn thành nhiều file nhỏ hơn

**❌ "Excel không đọc được"**
- Đóng Excel nếu đang mở file
- Kiểm tra file không corrupt
- Dùng template để đảm bảo format đúng

**❌ "Xử lý bị dừng"**
- Click "🛑 Hủy" và restart app
- Chia file thành chunks nhỏ hơn
- Kiểm tra log để biết dòng nào bị lỗi

### 6.4 Performance Tips
**Manual Mode:**
- Dùng expressions: `sqrt(2)`, `pi/4`, `sin(30)`
- Copy nhanh: Ctrl+C sau khi có kết quả
- Dropdown B tỳ ẩn/hiện tự động

**Excel Mode:** 
- File size tốt nhất <50MB
- Luôn dùng template trước
- Backup file gốc trước khi xử lý
- Theo dõi màu memory indicator

**General:**
- Restart app sau vài lần xử lý Excel lớn
- Chọn đúng version máy tính
- Export Excel ngay sau khi có kết quả manual

---

## 7. FAQ nhanh

**Q: Tại sao Equation Mode luôn hiển "Hệ vô nghiệm hoặc vô số nghiệm"?**
A: Đây là behavior v2.2 theo yêu cầu: Nghiệm không ảnh hưởng keylog; keylog luôn được sinh từ chuỗi gốc.

**Q: Có thể chỉ copy keylog mà không quan tâm nghiệm?**
A: Có, keylog luôn hiển thị ở "KẾT QUẢ TỔNG" và có thể copy ngay.

**Q: Polynomial có hỗ trợ nghiệm phức?** 
A: Có, hiển thị dạng a ± bi với precision có thể cấu hình trong service.

**Q: Geometry Mode có hỗ trợ biểu thức không?**
A: Hiện tại chưa, chỉ hỗ trợ số. Đang phát triển cho các version tiếp theo.

**Q: Làm sao biết app hỗ trợ bao nhiêu phiên bản máy tính?**
A: Kiểm tra dropdown "Phiên bản" trong mỗi mode, hoặc xem config files trong `config/`.

---

**📚 Tài liệu này cung cấp hướng dẫn đầy đủ để sử dụng ConvertKeylogApp v2.2 hiệu quả!**

**Version:** 2.2  
**Last Updated:** October 30, 2025  
**For:** ConvertKeylogApp v2.2 (Equation v2.2, Polynomial v2.1, Geometry v2.1)