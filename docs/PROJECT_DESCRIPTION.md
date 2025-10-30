# ConvertKeylogApp - Mô tả Dự án

[Phiên bản chính thức]

(Đây là bản di chuyển từ PROJECT_DESCRIPTION.md ở root)

## Tổng quan dự án

**ConvertKeylogApp** là ứng dụng desktop Python được thiết kế để **chuyển đổi các phép tính toán học phức tạp thành mã keylog tương thích với máy tính Casio**. Dự án được phát triển dựa trên kiến trúc modular, hỗ trợ đa mode tính toán và đa phiên bản máy tính.

## Vấn đề giải quyết

### Bối cảnh
- Việc nhập các phương trình phức tạp, hệ phương trình nhiều ẩn, hay polynomial bậc cao trên máy tính Casio rất tốn thời gian
- Sinh viên, kỹ sư cần công cụ chuyển đổi nhanh từ biểu thức toán học sang keylog máy tính
- Cần hỗ trợ batch processing cho nhiều bài toán cùng lúc

### Giải pháp
ConvertKeylogApp cung cấp **3 mode tính toán chuyên biệt**:
1. **Equation Mode** - Giải hệ phương trình tuyến tính 2×2, 3×3, 4×4
2. **Polynomial Mode** - Giải phương trình polynomial bậc 2, 3, 4  
3. **Geometry Mode** - Xử lý các bài toán hình học (đang phát triển)

## Kiến trúc hệ thống

### Cấu trúc thư mục
```
ConvertKeylogApp/
├── main.py                     # Entry point chính
├── views/                      # UI Layer
│   ├── main_view.py            # Main window với mode selector
│   ├── equation_view.py        # UI cho Equation Mode
│   ├── polynomial_equation_view.py # UI cho Polynomial Mode
│   └── geometry_view.py        # UI cho Geometry Mode
├── services/                   # Business Logic Layer
│   ├── equation/               # Equation Mode services
│   │   ├── equation_service.py
│   │   ├── equation_encoding_service.py
│   │   ├── mapping_manager.py
│   │   └── prefix_resolver.py
│   ├── polynomial/            # Polynomial Mode services
│   │   ├── polynomial_service.py
│   │   ├── polynomial_solver.py
│   │   ├── polynomial_prefix_resolver.py
│   │   └── polynomial_template_generator.py
│   └── geometry/              # Geometry Mode services
├── config/                    # Configuration files
│   ├── equation_mode/         # Equation mode config
│   ├── polynomial_mode/       # Polynomial mode config
│   └── common/               # Shared configuration
├── utils/                    # Utilities
└── docs/                     # Documentation
```

### Design Patterns sử dụng
- **Service Layer Pattern:** Tách biệt UI và business logic
- **Strategy Pattern:** Đa solver methods (NumPy, analytical)
- **Template Method:** Chuẩn hóa workflow xử lý
- **Config-Driven Development:** JSON-based configuration

## Tính năng chi tiết theo Mode

### 🧠 Equation Mode v2.2
**Chức năng:** Giải hệ phương trình tuyến tính và mã hóa keylog

**Đầu vào:**
- Hệ 2×2: 6 hệ số (a₁₁,a₁₂,c₁,a₂₁,a₂₂,c₂)
- Hệ 3×3: 12 hệ số (a₁₁,a₁₂,a₁₃,c₁,a₂₁,a₂₂,a₂₃,c₂,a₃₁,a₃₂,a₃₃,c₃)
- Hệ 4×4: 20 hệ số (4 phương trình × 5 hệ số)

**Đầu ra:**
- Nghiệm hệ: Hiển thị "Hệ vô nghiệm hoặc vô số nghiệm" (behavior mới)
- Keylog: Format TL `w912=...== =` (luôn được sinh)

**Tính năng đặc biệt:**
- ✅ Hỗ trợ biểu thức: sqrt(), sin(), cos(), log(), ln, pi, ^
- ✅ Excel import/export với smart chunking
- ✅ Template generator cho từng loại hệ n×n
- ✅ Memory monitoring cho file lớn
- ✅ Error-free workflow: Luôn sinh keylog dù solve fail

### 📈 Polynomial Mode v2.1  
**Chức năng:** Giải phương trình polynomial và mã hóa keylog

**Đầu vào:**
- Bậc 2: ax² + bx + c = 0 (3 hệ số)
- Bậc 3: ax³ + bx² + cx + d = 0 (4 hệ số)  
- Bậc 4: ax⁴ + bx³ + cx² + dx + e = 0 (5 hệ số)

**Đầu ra:**
- Nghiệm: Hiển thị tất cả nghiệm (thực + phức) với format đẹp
- Keylog: Multi-version `P2=1=-5=6==` (fx799), `EQN2=1=-5=6=0` (fx991)

**Solver engines:**
- ✅ NumPy roots finding (chính)
- ✅ Analytical methods (analytical fallback)
- ✅ Complex roots handling với format a±bi

**Tính năng đặc biệt:**
- ✅ Template generator với 3 sheets (Input/Examples/Instructions)
- ✅ Multi-version prefix system (8 calculator versions)
- ✅ Expression parsing: sqrt(), sin(), cos(), pi, log(), ^
- ✅ Dynamic input fields theo degree selected

### 📐 Geometry Mode (Đang phát triển)
**Chức năng:** Xử lý bài toán hình học và mã hóa keylog
- 🚧 Trong giai đoạn thiết kế và implement

## Hỗ trợ đa phiên bản máy tính

**Equation Mode prefixes:**
- **fx799:** w912, w913, w914
- **fx800-803:** Các format đặc biệt theo từng model

**Polynomial Mode prefixes:**  
- **fx799:** P2=, P3=, P4= với suffix ==, ===, ====
- **fx991:** EQN2=, EQN3=, EQN4= với suffix =0, ==0, ===0
- **fx570:** POL2=, POL3=, POL4= với suffix =ROOT, ==ROOT, ===ROOT
- **fx580:** POLY2=, POLY3=, POLY4= với suffix =SOLVE, ==SOLVE, ===SOLVE
- **fx115:** QUAD=, CUB3=, QUAT= với suffix =, ==, ===

## Công nghệ sử dụng

**Core Technologies:** Python 3, Tkinter, NumPy, Pandas, JSON configs

**Architecture:** UI → Services → Config, Dependency Injection, Graceful Error Handling

## Workflow tổng quát
1) Chọn Mode → 2) Nhập dữ liệu/Import Excel → 3) Xử lý → 4) Copy Keylog/Export Excel

## Roadmap
- Geometry Mode, Advanced parsing, Plugin modes, Cloud sync
