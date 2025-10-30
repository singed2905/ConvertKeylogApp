# 🧮 ConvertKeylogApp v2.2

> Ứng dụng chuyển đổi biểu thức toán học thành keylog cho máy tính Casio. Hỗ trợ Equation Mode (2×2, 3×3, 4×4) và Polynomial Mode (bậc 2–4), kèm Excel batch.

## ✨ Tính năng chính

### 🧠 Equation Mode v2.2 (Mới)
- Giải hệ 2×2, 3×3, 4×4 bằng NumPy (ổn định, nhanh)
- Mã hóa TL-compatible từ CHUỖI GỐC (không phụ thuộc nghiệm)
- Behavior mới: Luôn sinh Keylog, nghiệm hiển thị “Hệ vô nghiệm hoặc vô số nghiệm” khi solve fail hoặc det≈0
- Excel: Tạo template, Import/Export, progress tracking, memory monitoring
- Fix: Thiếu hệ số ở hệ 4 ẩn đã được khắc phục

### 📈 Polynomial Mode v2.1
- Giải phương trình bậc 2/3/4 (NumPy + analytical fallback)
- Hỗ trợ nghiệm phức, format a ± bi, precision cấu hình được
- Multi-version prefix: fx799(P2=…), fx991(EQN2=…), fx570(POL2=…), fx580(POLY2=…), fx115(QUAD=…)
- Template 3 sheet (Input/Examples/Instructions), Export Excel đầy đủ

## 🚀 Cài đặt nhanh

Yêu cầu: Python 3.9+, pip

```bash
pip install numpy pandas
python main.py
```

## 📖 Hướng dẫn sử dụng nhanh

- Equation Mode: Chọn số ẩn (2/3/4) → nhập từng phương trình dạng `a11,a12,…,c1` → “🚀 Xử lý & Mã hóa” → Copy keylog
- Polynomial Mode: Chọn bậc (2/3/4) → nhập hệ số → “🚀 Giải & Mã hóa” → Copy keylog
- Excel: “📝 Tạo Template”, “📁 Import Excel”, “🔥 Xử lý File Excel”, “💾 Xuất Excel”

Xem hướng dẫn chi tiết: USAGE_GUIDE_VI.md

## 🗂️ Cấu trúc dự án (rút gọn)
```
ConvertKeylogApp/
├── views/
│   ├── equation_view.py
│   └── polynomial_equation_view.py
├── services/
│   ├── equation/
│   │   ├── equation_service.py
│   │   ├── equation_encoding_service.py
│   │   ├── mapping_manager.py
│   │   └── prefix_resolver.py
│   └── polynomial/
│       ├── polynomial_service.py
│       ├── polynomial_solver.py
│       ├── polynomial_prefix_resolver.py
│       └── polynomial_template_generator.py
├── config/
│   ├── equation_mode/
│   └── polynomial_mode/
├── PROJECT_DESCRIPTION.md
└── USAGE_GUIDE_VI.md
```

## 🔧 Kỹ thuật nổi bật
- Service Layer tách UI/logic
- Config-driven prefixes & mappings (JSON)
- Fallback/Graceful handling: luôn sinh keylog, không chặn workflow

## 📄 License
MIT-like internal use. © 2025 ConvertKeylogApp Team
