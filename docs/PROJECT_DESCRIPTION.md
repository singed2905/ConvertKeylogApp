# ConvertKeylogApp v2.2 - Mô tả Dự án Tổng Hợp

> Ứng dụng desktop Python chuyển đổi biểu thức toán học thành keylog cho máy tính Casio. Hỗ trợ đa mode: Equation, Polynomial, Geometry.

---

## 1. Tổng quan dự án

**ConvertKeylogApp** là ứng dụng desktop Python được thiết kế để **chuyển đổi các phép tính toán học phức tạp thành mã keylog tương thích với máy tính Casio**. Dự án được phát triển dựa trên kiến trúc modular, hỗ trợ đa mode tính toán và đa phiên bản máy tính.

### Vấn đề giải quyết
- Việc nhập các phương trình phức tạp, hệ phương trình nhiều ẩn, hay polynomial bậc cao trên máy tính Casio rất tốn thời gian
- Sinh viên, kỹ sư cần công cụ chuyển đổi nhanh từ biểu thức toán học sang keylog máy tính
- Cần hỗ trợ batch processing cho nhiều bài toán cùng lúc

### Giải pháp
**3 mode tính toán chuyên biệt:**
1. **Equation Mode v2.2** - Giải hệ phương trình tuyến tính 2×2, 3×3, 4×4
2. **Polynomial Mode v2.1** - Giải phương trình polynomial bậc 2, 3, 4  
3. **Geometry Mode v2.1** - Xử lý các bài toán hình học (Production ready)

---

## 2. Kiến trúc hệ thống

### Cấu trúc thư mục
```
ConvertKeylogApp/
├── main.py                     # Entry point chính
├── views/                      # UI Layer (Tkinter)
│   ├── main_view.py            # Mode selector
│   ├── equation_view.py        # Equation Mode UI (v2.2)
│   ├── polynomial_equation_view.py # Polynomial UI (v2.1)
│   └── geometry_view.py        # Geometry UI (v2.1)
├── services/                   # Business Logic Layer
│   ├── equation/               # Hệ phương trình services
│   │   ├── equation_service.py    # Core solving logic
│   │   ├── equation_encoding_service.py # TL encoding
│   │   ├── mapping_manager.py     # TL mappings
│   │   └── prefix_resolver.py     # Multi-version prefixes
│   ├── polynomial/            # Polynomial services
│   │   ├── polynomial_service.py  # Core polynomial logic
│   │   ├── polynomial_solver.py   # Solving algorithms
│   │   ├── polynomial_prefix_resolver.py # Multi-version
│   │   └── polynomial_template_generator.py # Excel templates
│   └── geometry/              # Hình học services
│       ├── geometry_service.py    # Core geometry
│       ├── mapping_adapter.py     # LaTeX encoding
│       └── excel_loader.py        # Excel processing
├── config/                    # Configuration system
│   ├── equation_mode/         # Equation configs
│   │   ├── equation_mappings.json # TL mappings
│   │   └── equation_prefixes.json # Version prefixes  
│   ├── polynomial_mode/       # Polynomial configs
│   │   ├── polynomial_prefixes.json # Version prefixes
│   │   └── math_replacements.json # Expression parsing
│   ├── geometry_mode/         # Geometry configs
│   └── common/               # Shared configs
└── docs/                     # Documentation
    ├── PROJECT_DESCRIPTION.md  # Tài liệu này
    └── USER_GUIDE.md          # Hướng dẫn sử dụng
```

### Design Patterns
- **Service Layer Pattern:** Tách biệt UI và business logic hoàn toàn
- **Strategy Pattern:** Đa solver methods (NumPy, analytical, symbolic)
- **Template Method Pattern:** Chuẩn hóa workflow xử lý cho mỗi mode
- **Config-Driven Development:** JSON-based configuration system
- **Observer Pattern:** UI components react to service state changes

---

## 3. Tính năng chi tiết theo Mode

### 🧠 Equation Mode v2.2 (Mới nhất)
**Chức năng:** Giải hệ phương trình tuyến tính và mã hóa keylog

**Đầu vào hỗ trợ:**
- Hệ 2×2: 6 hệ số (a₁₁,a₁₂,c₁,a₂₁,a₂₂,c₂)
- Hệ 3×3: 12 hệ số (a₁₁,...,a₃₃,c₃)  
- Hệ 4×4: 20 hệ số (4 phương trình × 5 hệ số)
- Biểu thức: sqrt(), sin(), cos(), log(), ln, pi, ^ (lũy thừa)

**Đầu ra:**
- **Nghiệm hệ:** Luôn hiển thị "Hệ vô nghiệm hoặc vô số nghiệm" (behavior v2.2)
- **Keylog:** Format TL `w912=...== =` (2 ẩn), `w913=...== = =` (3 ẩn), `w914=...== = = =` (4 ẩn)
- **Luôn sinh keylog:** Dù solve fail hoặc det≈0, keylog vẫn được tạo

**Tính năng nổi bật:**
- ✅ NumPy solver ổn định cho ma trận n×n
- ✅ TL-compatible encoding từ chuỗi gốc (không eval)
- ✅ Excel template generator và batch processor
- ✅ Memory monitoring cho file lớn
- ✅ Error-free workflow: Không chặn bằng popup lỗi
- ✅ Multi-version support: fx799-fx803

### 📈 Polynomial Mode v2.1
**Chức năng:** Giải phương trình polynomial và mã hóa keylog

**Đầu vào hỗ trợ:**
- Bậc 2: ax² + bx + c = 0 (3 hệ số: a, b, c)
- Bậc 3: ax³ + bx² + cx + d = 0 (4 hệ số: a, b, c, d)  
- Bậc 4: ax⁴ + bx³ + cx² + dx + e = 0 (5 hệ số: a, b, c, d, e)
- Biểu thức: Đầy đủ như Equation Mode

**Đầu ra:**
- **Nghiệm:** Hiển thị tất cả nghiệm (thực + phức) với format chuẩn a ± bi
- **Keylog:** Multi-version prefix system
  - fx799: `P2=1=-5=6==`
  - fx991: `EQN2=1=-5=6=0`  
  - fx570: `POL2=1=-5=6=ROOT`
  - fx580: `POLY2=1=-5=6=SOLVE`
  - fx115: `QUAD=1=-5=6=`

**Solver engines:**
- ✅ NumPy roots finding (engine chính, ổn định)
- ✅ Analytical methods (fallback cho edge cases)  
- ✅ Complex roots handling với precision cấu hình được

**Tính năng đặc biệt:**
- ✅ PolynomialPrefixResolver: Hỗ trợ 8+ calculator versions
- ✅ Template generator 3-sheet system (Input/Examples/Instructions) 
- ✅ Dynamic input fields với form hiển thị theo degree
- ✅ Expression parsing engine tích hợp

### 📐 Geometry Mode v2.1 (Production Ready)
**Chức năng:** Xử lý bài toán hình học 2D/3D và mã hóa keylog

**5 Hình học cơ bản:**
- 🎯 Biểm: Tọa độ 2D/3D
- 📏 Đường thẳng: Điểm + Vector hướng  
- 📐 Mặt phẳng: Phương trình ax+by+cz+d=0
- ⚫ Đường tròn: Tâm + Bán kính
- 🌍 Mặt cầu: Tâm + Bán kính

**5 Phép toán:**
- Tương giao: Tìm giao điểm/giao tuyến giữa 2 hình
- Khoảng cách: Tính khoảng cách giữa các hình 
- Diện tích: Tính diện tích hình phẳng
- Thể tích: Tính thể tích khối
- Phương trình đường thẳng: Tìm phương trình

**Tính năng đặc biệt:**
- ✅ Excel integration hoàn chỉnh với progress tracking
- ✅ Memory monitoring real-time với color coding
- ✅ Template generator cho tất cả combinations hình dạng
- ✅ LaTeX to calculator encoding system
- ✅ Anti-crash mechanism cho file lớn

---

## 4. Hỗ trợ đa phiên bản máy tính

**Equation Mode prefixes (TL-compatible):**
- **fx799:** w912 (2 ẩn), w913 (3 ẩn), w914 (4 ẩn)
- **fx800-803:** Các format khác theo config JSON

**Polynomial Mode prefixes (Đa dạng):**
| Version | Bậc 2 | Bậc 3 | Bậc 4 | Suffix Pattern |
|---------|-------|-------|-------|----------------|
| fx799   | P2=   | P3=   | P4=   | ==, ===, ==== |
| fx991   | EQN2= | EQN3= | EQN4= | =0, ==0, ===0 |
| fx570   | POL2= | POL3= | POL4= | =ROOT, ==ROOT, ===ROOT |
| fx580   | POLY2=| POLY3=| POLY4=| =SOLVE, ==SOLVE, ===SOLVE |
| fx115   | QUAD= | CUB3= | QUAT= | =, ==, === |

**Geometry Mode prefixes:**
- fx799/fx800: Hỗ trợ đầy đủ 5 hình × 5 phép toán = 25 combinations

---

## 5. Công nghệ và kỹ thuật

**Core Technologies:**
- **Python 3.9+** - Main language với modern features
- **Tkinter** - GUI framework với custom styling
- **NumPy** - High-performance numerical computing
- **Pandas** - Excel data processing và manipulation
- **psutil** - System monitoring (memory, CPU)
- **JSON** - Configuration management system

**Architecture Principles:**
- **Layered Architecture:** UI → Services → Models → Config
- **Dependency Injection:** Services inject config và dependencies
- **Graceful Error Handling:** Fallback mechanisms và user notifications
- **Performance Optimization:** Chunked processing, memory monitoring

**Key Technical Decisions:**
- **Tkinter over PyQt:** Built-in, lightweight, cross-platform
- **NumPy over SymPy:** Performance cho numerical computation
- **JSON over YAML:** Simpler, faster parsing, better Python integration
- **Service layer over MVC:** Better separation, easier testing

---

## 6. Workflow tổng quát

### Bước tổng quát cho mọi mode:
1. **Mode Selection** → Chọn Equation/Polynomial/Geometry từ main screen
2. **Parameter Setup** → Chọn số ẩn/bậc/phép toán và version máy tính
3. **Input Data** → Nhập thủ công hoặc import Excel file  
4. **Processing** → Auto validate → Solve/Calculate → Encode keylog
5. **Output Display** → Hiển thị results, encoded coefficients, và final keylog
6. **Export Options** → Copy keylog to clipboard hoặc export Excel results

### Error Handling Flow:
- **Input validation** ngay khi nhập
- **Graceful degradation** khi service/component fail
- **User notification** rõ ràng, không technical jargon
- **Fallback mechanisms** cho font, encoding, file processing

---

## 7. Target Users và Use Cases

**Primary Users:**
- **Sinh viên ĐH/CĐ** - Giải nhanh bài tập toán, vật lý, kỹ thuật
- **Giáo viên/Giảng viên** - Tạo đề thi, kiểm tra, chấm điểm batch
- **Kỹ sư/Kỹ thuật viên** - Tính toán nhanh trong công việc
- **Nghiên cứu sinh** - Xử lý data toán học với keylog output

**Secondary Users:**  
- **Developer** muốn extend chức năng hoặc integrate API
- **IT Support** cần deploy cho team/organization

**Use Cases chính:**
1. **Single Calculation:** Giải 1 bài cụ thể, copy keylog vào máy tính
2. **Batch Processing:** Xử lý hàng trăm bài tập Excel cùng lúc
3. **Template Creation:** Tạo template chuẩn cho students/team
4. **Educational:** Giảng dạy và demo các phép toán toán học

---

## 8. Roadmap phát triển

**Phase 2 (Hiện tại - Hoàn thành):**
- ✅ Equation Mode v2.2 fully functional (fix bug 3-4 ẩn, always keylog)
- ✅ Polynomial Mode v2.1 với PolynomialPrefixResolver  
- ✅ Geometry Mode v2.1 production-ready
- ✅ Excel integration hoàn chỉnh cho cả 3 modes
- ✅ Config system với JSON externalization

**Phase 3 (Tương lai gần):**
- 🚧 Advanced expression parsing (complex expressions, functions)
- 🚧 Plugin system cho custom mathematical operations  
- 🚧 Web interface với Flask backend
- 🚧 Database integration để save history và templates

**Phase 4 (Tương lai xa):**
- 🚧 Cloud sync và collaboration features
- 🚧 Mobile app companion
- 🚧 API endpoints cho third-party integration
- 🚧 Multi-language support (English, other languages)

---

## 9. Technical Specifications

### System Requirements:
- **Minimum:** Python 3.9+, 4GB RAM, 100MB disk
- **Recommended:** Python 3.11+, 8GB RAM, 500MB disk
- **Excel Processing:** Microsoft Excel 2010+ formats
- **OS Support:** Windows 10+, macOS 10.14+, Ubuntu 18.04+

### Performance Benchmarks:
- **Manual calculation:** <1s response time
- **Excel processing:** 100-500 rows/second depending on complexity
- **Memory usage:** <500MB cho file <50MB, smart chunking cho file lớn hơn
- **File size limit:** Thực tế không giới hạn (chunked processing)

### Quality Assurance:
- **Code coverage:** >85% line coverage (target)
- **Error handling:** Comprehensive try-catch và fallback
- **Cross-platform testing:** Windows, macOS, Linux
- **Memory leak prevention:** Proper resource cleanup

---

## 10. Success Metrics và KPI

**Technical Metrics:**
- Maintainability Index >80
- Response time <2s cho 95% operations  
- Memory efficiency <500MB cho 95% use cases
- Zero-crash rate đối với chunked Excel processing

**User Experience Metrics:**
- Time-to-first-result <5 minutes cho new users
- Error rate <5% cho validated input data
- User satisfaction target >4.0/5.0
- Feature adoption rate >80% cho core features

---

**ConvertKeylogApp v2.2** đang phát triển thành **ecosystem hoàn chỉnh** cho việc chuyển đổi toán học sang keylog máy tính với focus vào **user experience**, **technical excellence**, và **production reliability**.

---

**Document Version:** 2.2  
**Last Updated:** October 30, 2025  
**Author:** ConvertKeylogApp Development Team