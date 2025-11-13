# Polynomial Encoding Service - Hướng dẫn đầy đủ

## Tổng quan

**PolynomialEncodingService** là service mã hóa các hệ số polynomial từ biểu thức toán học sang format keylog của máy tính Casio. Service này sử dụng file **`config/polynomial_mode/polynomial_mapping.json`** để áp dụng các quy tắc chuyển đổi.

## Quy tắc mã hóa từ `polynomial_mapping.json`

### 1. Toán tử cơ bản

| Biểu thức input | Mã hóa | Mô tả |
|------------------|------------|-------|
| `-` | `p` | Dấu âm (trừ) |
| `*` | `O` | Phép nhân |
| `/` | `P` | Phép chia |
| `^` | `^` | Lũy thừa (giữ nguyên) |
| `_` | `_` | Chỉ số dưới (giữ nguyên) |

### 2. Hàm toán học

| Hàm input | Mã hóa | Mô tả |
|-------------|------------|-------|
| `sqrt(` | `s(` | Căn bậc hai |
| `sin(` | `j(` | Sin |
| `cos(` | `k(` | Cos |
| `tan(` | `l(` | Tan |
| `ln(` | `h(` | Logarit tự nhiên |

**Lưu ý:** Các biến thể của sqrt cũng được hỗ trợ:
- `\sqrt{` → `s(`
- `sqrt{` → `s(`
- `\sqrt(` → `s(`
- `sqrt(` → `s(`

### 3. Ngoặc và ký hiệu LaTeX

| Ký hiệu input | Mã hóa | Mô tả |
|---------------|------------|-------|
| `{` | `(` | Ngoặc nhọn mở |
| `}` | `)` | Ngoặc nhọn đóng |
| `\left(` | `(` | LaTeX ngoặc tròn mở |
| `\right)` | `)` | LaTeX ngoặc tròn đóng |
| `\left[` | `(` | LaTeX ngoặc vuông mở |
| `\right]` | `)` | LaTeX ngoặc vuông đóng |

### 4. Regex patterns (nâng cao)

#### Phân số (Fractions)
```
\frac{x}{y} → x a y
```
Ví dụ: `\frac{1}{2}` → `1a2`

#### Tích phân (Integrals)
```
\int_(a)^(b) f(x) dx → y f(x),a,b)
\int_{a}^{b} f(x) dx → y f(x),a,b)
```

## Cách sử dụng

### 1. Sử dụng trực tiếp PolynomialEncodingService

```python
from services.polynomial.polynomial_encoding_service import PolynomialEncodingService

# Khởi tạo encoder
encoder = PolynomialEncodingService()

# Mã hóa 1 hệ số
result = encoder.encode_coefficient("-5")
print(result)  # Output: "p5"

# Mã hóa danh sách hệ số
coeffs = ["1", "-5", "sqrt(4)"]
encoded = encoder.encode_coefficients(coeffs)
print(encoded)  # Output: ['1', 'p5', 's(4)']
```

### 2. Sử dụng thông qua PolynomialService (Khuyến nghị)

```python
from services.polynomial.polynomial_service import PolynomialService

# Khởi tạo service
service = PolynomialService()

# Cấu hình
service.set_degree(2)  # Phương trình bậc 2
service.set_version("fx799")  # Phiên bản máy tính

# Xử lý hoàn chỉnh: giải + mã hóa + tạo keylog
coeffs = ["1", "-5", "6"]
success, msg, roots, keylog = service.process_complete_workflow(coeffs)

if success:
    print("Nghiệm:", roots)
    print("Keylog:", keylog)
    print("Encoded coeffs:", service.get_last_encoded_coefficients())
```

### 3. Test encoding chi tiết (Debug)

```python
from services.polynomial.polynomial_encoding_service import PolynomialEncodingService

encoder = PolynomialEncodingService()

# Test với step-by-step transformation
result = encoder.test_encoding("-sqrt(25)")

print(f"Original: {result['original']}")
print(f"Final: {result['final']}")
print(f"Total transformations: {result['total_transformations']}")

for step in result['steps']:
    if step['step'] > 0:
        print(f"Step {step['step']}: {step['input']} → {step['output']}")
        print(f"  Rule: {step['rule']}")
        print(f"  Description: {step['description']}")
```

## Ví dụ thực tế

### Ví dụ 1: Phương trình bậc 2 cơ bản

```python
# Input: x² - 5x + 6 = 0
coeffs = ["1", "-5", "6"]

service = PolynomialService()
service.set_degree(2)
service.set_version("fx799")

success, msg, roots, keylog = service.process_complete_workflow(coeffs)

# Output:
# Encoded: ['1', 'p5', '6']
# Keylog: w9221=p5=6== 
# Roots: x₁ = 2, x₂ = 3
```

### Ví dụ 2: Với biểu thức toán học

```python
# Input: x² - sqrt(4)x + sin(pi/2) = 0
coeffs = ["1", "-sqrt(4)", "sin(pi/2)"]

service = PolynomialService()
service.set_degree(2)
service.set_version("fx799")

success, msg, roots, keylog = service.process_complete_workflow(coeffs)

# Quá trình:
# 1. Parse: "1" → 1.0, "-sqrt(4)" → -2.0, "sin(pi/2)" → 1.0
# 2. Solve: Roots = [1.0, 1.0] (nghiệm kép)
# 3. Encode: ['1', 'ps(4)', 'j(pi/2)']  # Áp dụng mapping rules
# 4. Keylog: w9221=ps(4)=j(pi/2)== 
```

### Ví dỡ 3: Đa phiên bản máy tính

```python
coeffs = ["1", "-5", "6"]
versions = ["fx799", "fx880"]

for version in versions:
    service = PolynomialService()
    service.set_degree(2)
    service.set_version(version)
    
    success, msg, roots, keylog = service.process_complete_workflow(coeffs)
    print(f"{version}: {keylog}")

# Output:
# fx799: w9221=p5=6== 
# fx880: EQN2=1=p5=6=0
```

## Workflow mã hóa

```
1. INPUT
   │
   └──> Coefficients: ["1", "-sqrt(4)", "sin(pi/2)"]

2. PARSE (PolynomialSolver)
   │
   └──> Numeric values: [1.0, -2.0, 1.0]

3. SOLVE (PolynomialSolver)
   │
   └──> Roots: [1.0, 1.0] (nghiệm kép)

4. ENCODE (PolynomialEncodingService)
   │
   ├─> Apply mapping rules từ polynomial_mapping.json
   │   ├─> "-" → "p"
   │   ├─> "sqrt(" → "s("
   │   └─> "sin(" → "j("
   │
   └──> Encoded: ['1', 'ps(4)', 'j(pi/2)']

5. GENERATE KEYLOG (PolynomialPrefixResolver)
   │
   ├─> Get prefix: "w922" (fx799, degree 2)
   ├─> Join coeffs: "1=ps(4)=j(pi/2)"
   ├─> Get suffix: "== "
   │
   └──> Final keylog: "w9221=ps(4)=j(pi/2)== "
```

## Cấu trúc file polynomial_mapping.json

```json
{
  "latex_to_calculator_mappings": [
    {
      "find": "-",
      "replace": "p",
      "type": "literal",
      "description": "Dấu âm (trừ) thành 'p'"
    },
    {
      "find": "sqrt(",
      "replace": "s(",
      "type": "literal",
      "description": "Hàm sqrt{ không dấu \\ → s("
    },
    {
      "find": "\\\\frac\\{([^{}]+)\\}\\{([^{}]+)\\}",
      "replace": "$1a$2",
      "type": "regex",
      "description": "Chuyển phân số \\frac{x}{y} thành dạng x a y"
    }
  ],
  "metadata": {
    "version": "1.4",
    "description": "Quy tắc mã hóa cho polynomial mode",
    "last_updated": "2025-11-12"
  }
}
```

## API Reference

### PolynomialEncodingService

#### `__init__(mapping_file: str)`
Khởi tạo encoder với file mapping.

#### `encode_coefficient(coefficient_str: str) -> str`
Mã hóa 1 hệ số.

**Parameters:**
- `coefficient_str`: Chuỗi biểu thức hệ số

**Returns:**
- Chuỗi đã mã hóa

#### `encode_coefficients(coefficients: List[str]) -> List[str]`
Mã hóa danh sách hệ số.

#### `test_encoding(test_input: str) -> Dict[str, Any]`
Test encoding với step-by-step transformation.

**Returns:**
```python
{
    "original": "input string",
    "final": "encoded string",
    "steps": [
        {
            "step": 1,
            "input": "before",
            "output": "after",
            "rule": "find → replace",
            "description": "rule description"
        }
    ],
    "total_transformations": 3
}
```

#### `get_mapping_info() -> Dict[str, Any]`
Lấy thông tin về các mapping rules.

#### `reload_mappings() -> bool`
Reload mappings từ file (hữu ích khi cập nhật config).

## Testing

Chạy file test để kiểm tra:

```bash
python test_polynomial_encoding.py
```

File test bao gồm:
1. Basic encoding tests
2. Detailed step-by-step encoding
3. Full service integration
4. Complex mathematical expressions
5. Multiple calculator versions
6. Encoding rules information

## Troubleshooting

### Lỗi: "Mapping file not found"

**Nguyên nhân:** File `config/polynomial_mode/polynomial_mapping.json` không tồn tại.

**Giải pháp:**
- Kiểm tra đường dẫn file
- Service sẽ tự động fallback về default mappings

### Lỗi: "Invalid mapping file structure"

**Nguyên nhân:** File JSON thiếu key `latex_to_calculator_mappings`.

**Giải pháp:**
- Kiểm tra cấu trúc JSON
- Tham khảo cấu trúc mẫu ở trên

### Lỗi: "Regex error"

**Nguyên nhân:** Regex pattern không hợp lệ trong mapping.

**Giải pháp:**
- Kiểm tra regex pattern trong JSON
- Lỗi sẽ được skip, không làm crash chương trình

## Best Practices

1. **Sử dụng PolynomialService thay vì PolynomialEncodingService trực tiếp**
   - PolynomialService xử lý workflow hoàn chỉnh
   - Tự động tích hợp encoding, solving, keylog generation

2. **Test encoding trước khi deploy**
   - Sử dụng `test_encoding()` để kiểm tra rules
   - Chạy `test_polynomial_encoding.py` để test toàn bộ

3. **Backup file mapping trước khi chỉnh sửa**
   - File mapping là core của encoding logic
   - Thay đổi có thể ảnh hưởng đến toàn bộ hệ thống

4. **Thêm description rõ ràng cho mỗi rule**
   - Giúp debug và maintain sau này
   - Hiển thị trong logging và test output

## Tính năng tương lai

- [ ] Hỗ trợ custom mapping profiles
- [ ] UI để chỉnh sửa mapping rules
- [ ] Validation cho regex patterns
- [ ] Export/import mapping configurations
- [ ] Mapping history và versioning

## Changelog

### Version 1.0 (2025-11-13)
- Khởi tạo PolynomialEncodingService
- Tích hợp với polynomial_mapping.json
- Hỗ trợ regex và literal replacements
- Test suite hoàn chỉnh

---

**Lưu ý:** Service này là một phần của ConvertKeylogApp v2.2. Để biết thêm thông tin, tham khảo `docs/PROJECT_DESCRIPTION.md`.
