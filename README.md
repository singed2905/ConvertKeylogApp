# ConvertKeylogApp v2.2

**Ứng dụng chuyển đổi và mã hóa keylog cho máy tính Casio**

Repository: [singed2905/ConvertKeylogApp](https://github.com/singed2905/ConvertKeylogApp)

---

## 📋 Tổng quan

ConvertKeylogApp là ứng dụng Python desktop hỗ trợ:
- Giải hệ phương trình tuyến tính (2-4 ẩn)
- Tính toán hình học không gian
- Giải phương trình đa thức (bậc 2-4) với phát hiện nghiệm bội
- Tính toán vector (2D/3D)
- Mã hóa kết quả sang định dạng keylog cho máy tính Casio

---

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Python 3.8+
- Windows/Linux/macOS

### Dependencies
```bash
pip install -r requirements.txt
```

**Thư viện chính:**
- `pandas >= 1.5.0` - Xử lý Excel
- `openpyxl >= 3.0.0` - Đọc/ghi Excel
- `numpy >= 1.20.0` - Tính toán số học
- `psutil >= 5.8.0` - System monitoring
- `tkinter` - GUI (built-in)

### Chạy ứng dụng
```bash
python main.py
```

---

## 📚 Chức năng từng Mode

### 1️⃣ **Equation Mode** - Giải hệ phương trình

#### Tính năng
- **Hỗ trợ hệ**: 2, 3, 4 ẩn
- **Input**: Biểu thức toán học (sqrt, sin, cos, tan, log, ln, pi, ^)
- **Output**: Nghiệm + Keylog mã hóa

#### Quy trình xử lý
```
Input → Parse expressions → Solve system → Encode → Generate keylog
```

#### Phân loại nghiệm (Enhanced)
- ✅ **Nghiệm duy nhất**: det(A) ≠ 0
- ❌ **Vô nghiệm**: rank(A) < rank([A|b])
- ♾️ **Vô số nghiệm**: rank(A) == rank([A|b]) < n

#### Đặc điểm kỹ thuật
- **No-eval encoding**: Giữ nguyên biểu thức gốc khi mã hóa
- **Rank analysis**: Phân biệt chính xác vô nghiệm vs vô số nghiệm
- **Always output keylog**: Sinh keylog ngay cả khi solve fail

#### Ví dụ
```python
# Input hệ 2 ẩn:
# x + y = 3
# 2x - y = 0
# → Nghiệm: x = 1, y = 2
# → Keylog: wj... (encoded)
```

---

### 2️⃣ **Geometry Mode** - Hình học không gian

#### Đối tượng hỗ trợ
| Đối tượng | Dimension | Input |
|-----------|-----------|-------|
| Điểm | 2D/3D | x, y[, z] |
| Đường thẳng | 3D | Điểm (A) + Vector (u) |
| Mặt phẳng | 3D | ax + by + cz + d = 0 |
| Đường tròn | 2D | Tâm (I) + Bán kính (R) |
| Mặt cầu | 3D | Tâm (I) + Bán kính (R) |

#### Phép toán
- **Tương giao**: Điểm giao giữa các đối tượng
- **Khoảng cách**: Khoảng cách giữa 2 đối tượng
- **Diện tích**: Diện tích đường tròn/mặt cầu
- **Thể tích**: Thể tích mặt cầu
- **PT đường thẳng**: Phương trình từ 2 điểm

#### Format keylog
```
# Single object (Diện tích/Thể tích):
wj{shapeA_code}{encoded_values}C{operation_code}{tcode}=

# Two objects:
wj{shapeA_code}{encoded_values}C{shapeB_code}{encoded_values}C{operation_code}{tcodeA}R{tcodeB}=
```

#### Excel Integration
**Auto-detect large files:**
- File > 10MB hoặc > 50,000 rows → Large File Processor
- Chunked processing với memory optimization
- Progress tracking real-time

**Template generation:**
```python
geometry_service.create_template_for_shapes("Đường thẳng", "Mặt phẳng")
```

---

### 3️⃣ **Polynomial Mode** - Phương trình đa thức

#### Tính năng
- **Bậc hỗ trợ**: 2, 3, 4
- **Solving methods**:
  - NumPy: `np.roots` (default)
  - Analytical: Công thức đại số (bậc 2)
- **Phát hiện nghiệm bội**: Threshold 1e-8

#### Root Analysis
```python
# Example: x² - 2x + 1 = 0
# Roots: [1.0, 1.0]
# Analysis:
{
  'root_multiplicities': {'1.0': 2},
  'compact_display': 'x = 1.0 (bội 2)',
  'has_repeated_roots': True
}
```

#### Encoding System
- **PolynomialEncodingService**: Mapping từ `polynomial_mapping.json`
- **PolynomialPrefixResolver**: Prefix/suffix theo version
- **Test encoding**: Debug từng hệ số

#### Keylog Format
```
{prefix}{encoded_a}={encoded_b}={encoded_c}=...{suffix}
```

**Prefix by version:**
- fx799: `wjP2`, `wjP3`, `wjP4`
- fx991: `POLY2`, `POLY3`, `POLY4`

#### Workflow
```
Validate → Solve → Detect repeated roots → Encode → Generate keylog
```

---

### 4️⃣ **Vector Mode** - Tính toán vector

#### Calculation Types

**A. Scalar-Vector Operations**
| Operation | Formula | Example |
|-----------|---------|---------|
| Multiply | k × v | 3 × (1,2) = (3,6) |
| Divide | v ÷ k | (4,8) ÷ 2 = (2,4) |
| Add | v + k | (1,2) + 3 = (4,5) |
| Subtract | v - k | (5,3) - 2 = (3,1) |

**B. Vector-Vector Operations**
| Operation | Formula | Output Type |
|-----------|---------|-------------|
| Dot Product | A • B | Scalar |
| Cross Product | A × B | Vector (3D only) |
| Add | A + B | Vector |
| Subtract | A - B | Vector |
| Angle | arccos((A•B)/(|A||B|)) | Scalar (degrees) |
| Distance | |A - B| | Scalar |

#### Fixed Values System
Mỗi operation có fixed value identifier:
```python
{
  "scalar_vector": {
    "multiply": "1",
    "divide": "1",
    "add": "0",
    "subtract": "0"
  },
  "vector_vector": {
    "dot_product": "DOT",
    "cross_product": "CROSS",
    "angle": "ANG",
    "distance": "DIST"
  }
}
```

#### Keylog Format
```
# Scalar-Vector:
wv{vectorA_encoded}C{scalar_encoded}{op_code}{fixed_value}=

# Vector-Vector:
wv{vectorA_encoded}C{vectorB_encoded}C{op_code}{fixed_value}=
```

#### Expression Support
```python
# Input: "sqrt(2), pi, 2^3"
# Parsed: [1.414, 3.142, 8.0]
# Supported: sqrt, sin, cos, tan, log, ln, pi, e, ^
```

---

## 🗂️ Cấu trúc Project

```
ConvertKeylogApp/
├── config/
│   ├── common/              # Shared configs
│   ├── equation_mode/       # Equation mode settings
│   ├── geometry_mode/       # Geometry mode settings
│   ├── polynomial_mode/     # Polynomial mode settings
│   ├── vector_mode/         # Vector mode settings
│   ├── version_configs/     # Calculator versions
│   └── modes.json           # Mode definitions
├── services/
│   ├── equation/            # Equation solving & encoding
│   ├── geometry/            # Geometry calculations
│   ├── polynomial/          # Polynomial solving
│   ├── vector/              # Vector operations
│   └── excel/               # Excel processing (+ large file support)
├── views/                   # GUI components
│   ├── main_view.py         # Mode selector
│   ├── equation_view.py
│   ├── geometry_view.py
│   ├── polynomial_equation_view.py
│   └── vector_view.py
├── utils/                   # Utilities
├── tests/                   # Unit tests
├── main.py                  # Entry point
├── requirements.txt
└── README.md
```

---

## ⚙️ Configuration

### Version Support
```json
{
  "fx799": {"prefix": "wj", "description": "Casio fx-799"},
  "fx991": {"prefix": "FX", "description": "Casio fx-991"},
  "fx570": {"prefix": "V", "description": "Casio fx-570"}
}
```

### Mode Configuration
Mỗi mode có config riêng trong `config/{mode_name}/`:
- `mapping.json` - Character mapping rules
- `settings.json` - Mode-specific settings
- `templates.json` - Excel templates

---

## 📊 Excel Processing

### Normal Files
- Load toàn bộ vào memory
- Process từng row tuần tự
- Export 1 lần

### Large Files (>10MB hoặc >50k rows)
```python
# Auto-detect và switch processor
is_large, file_info = excel_processor.is_large_file(file_path)

if is_large:
    # Chunked reading
    # Streaming write
    # Memory cleanup per chunk
    # Progress tracking
```

**Features:**
- Recommended chunk size: 1000 rows
- Memory optimization với `gc.collect()`
- Crash protection với `psutil`
- Multi-sheet export (data + summary + errors)

---

## 🧪 Testing

### Run tests
```bash
# All tests
pytest

# Specific test
pytest tests/test_polynomial_encoding.py

# With coverage
pytest --cov=services
```

### Test Files
```
tests/
├── test_equation_basic.py
├── test_geometry_basic.py
├── test_polynomial_encoding.py
├── test_vector_basic.py
├── test_integral_encoding.py
└── test_large_file_crash_proof.py
```

---

## 🔧 Development

### Adding New Mode

1. **Create service**:
```python
# services/new_mode/new_service.py
class NewService:
    def __init__(self, config=None):
        self.config = config
    
    def process_workflow(self, inputs):
        # Processing logic
        return result
```

2. **Create view**:
```python
# views/new_mode_view.py
class NewModeView:
    def __init__(self, root, config=None):
        self.root = root
        self.service = NewService(config)
```

3. **Register in config**:
```json
// config/modes.json
{
  "New Mode": {
    "enabled": true,
    "config_path": "config/new_mode"
  }
}
```

4. **Add to main view**:
```python
# views/main_view.py
def _open_new_mode(self):
    config = config_loader.get_mode_config("New Mode")
    new_window = tk.Toplevel(self.root)
    view = NewModeView(new_window, config)
```

---

## 🐛 Known Issues & Limitations

### Equation Mode
- Hệ gần suy biến có thể cho kết quả không ổn định (numerical error)
- Không hỗ trợ hệ phi tuyến

### Geometry Mode
- Chỉ hỗ trợ hình học Euclid 2D/3D
- Cross product chỉ có cho 3D

### Polynomial Mode
- Numerical instability cho bậc cao với hệ số lớn
- Threshold phát hiện nghiệm bội có thể cần điều chỉnh

### Vector Mode
- Cross product yêu cầu 3D vectors
- Angle calculation có thể bị clamping error với floating point

### Excel
- Large files (>100MB) có thể chậm
- Memory usage cao với chunked processing

---

## 📝 Changelog

### v2.2 (Current)
- ✨ Added Vector Mode với fixed values system
- 🔧 Enhanced Equation Mode với rank analysis
- 🚀 Large file support cho Excel processing
- 🐛 Fixed repeated roots detection trong Polynomial Mode

### v2.1
- ✨ Added Polynomial Mode với enhanced solver
- 🔧 Improved geometry encoding system
- 📊 Excel batch processing với progress tracking

### v2.0
- 🎨 New UI với mode selector
- 📁 Config restructure theo mode
- 🔧 Enhanced equation solving với no-eval encoding

---

## 👥 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open Pull Request

### Coding Standards
- Follow PEP 8
- Add docstrings cho functions/classes
- Write unit tests cho new features
- Update README nếu cần

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📧 Contact

Project Link: [https://github.com/singed2905/ConvertKeylogApp](https://github.com/singed2905/ConvertKeylogApp)

---

## 🙏 Acknowledgments

- NumPy - Numerical computations
- Pandas - Excel processing
- OpenPyXL - Excel file handling
- Tkinter - GUI framework

---

**Made with ❤️ by singed2905**