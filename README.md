# ConvertKeylogApp v2.1 🧮

**Anti-Crash Excel Processing Tool for Geometry, Equations, Polynomials & Vectors**

## 🆕 NEW: Coordinate Plotting Feature in Geometry Mode

**Tính năng mới**: Hiển thị trực quan các nhóm A và B trên hệ tọa độ Oxy/Oxyz khi nhập liệu thủ công!

### ✨ Features

- **📊 Real-time Visualization**: Hiển thị ngay lập tức các đối tượng hình học trên trục tọa độ
- **🎨 Color Coding**: Nhóm A (màu xanh), Nhóm B (màu đỏ)
- **📏 Interactive Tools**: Zoom, pan, và các công cụ tương tác matplotlib
- **🔄 Auto-scale**: Tự động điều chỉnh tỷ lệ trục cho phù hợp
- **📐 2D/3D Support**: Hỗ trợ cả hệ tọa độ 2 chiều và 3 chiều

### 📍 Supported Shapes

#### 2D Visualization:
- **Điểm**: Hiển thị với tọa độ và nhãn
- **Đường tròn**: Hiển thị với tâm và bán kính
- **Đường thẳng**: Hiển thị theo phương trình tham số

#### 3D Visualization:
- **Điểm**: Hiển thị trong không gian 3D
- **Mặt cầu**: Hiển thị dạng wireframe với tâm
- **Đường thẳng**: Hiển thị theo vector phương
- **Mặt phẳng**: Hiển thị dạng lưới 3D

### 🚀 How to Use

1. **Chọn phép toán** (Khoảng cách, Tương giao, etc.)
2. **Chọn hình dạng** cho Nhóm A và B
3. **Nhập dữ liệu** vào các ô input
4. **Click 'Thực thi tất cả'** để xem kết quả và đồ thị
5. **Khung đồ thị sẽ xuất hiện** bên dưới nút Copy Kết Quả

### 💡 Examples

#### Khoảng cách 2 điểm 2D:
- Nhóm A: `1,2`
- Nhóm B: `4,6`
- Kết quả: Hiển thị 2 điểm và khoảng cách trên Oxy

#### Mặt cầu 3D:
- Tâm: `0,0,0`
- Bán kính: `5`
- Kết quả: Hiển thị mặt cầu trong không gian Oxyz

## 🔧 Installation

```bash
# Clone repository
git clone https://github.com/singed2905/ConvertKeylogApp.git
cd ConvertKeylogApp

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## 📋 Requirements

- Python 3.7+
- tkinter (built-in)
- matplotlib >= 3.5.0 (NEW for plotting)
- pandas >= 1.5.0
- openpyxl >= 3.0.0
- psutil >= 5.8.0
- numpy >= 1.20.0

## 🧪 Testing

```bash
# Test coordinate plotting feature
python test_coordinate_plotting.py

# Basic geometry tests
python test_geometry_basic.py

# Quick smoke test
python quick_run_geometry.py
```

## 🎯 Key Features

### 1. **Geometry Mode** 📐
- 5 shapes: Điểm, Đường thẳng, Mặt phẳng, Đường tròn, Mặt cầu
- 5 operations: Tương giao, Khoảng cách, Diện tích, Thể tích, PT đường thẳng
- **NEW**: Real-time coordinate visualization
- Large file Excel processing (250k+ rows)
- Memory-efficient streaming

### 2. **Equation Mode** 🧠
- Linear equation systems (2×2, 3×3, 4×4)
- NumPy solver with rank analysis
- Multi-version keylog support

### 3. **Polynomial Mode** 📈
- Polynomial equations (degree 2-4)
- Complex roots handling
- Repeated roots detection

### 4. **Vector Mode** 🔢
- 2D/3D vector operations
- Scalar and vector calculations
- Dot product, cross product, angles

## 🛡️ Anti-Crash Technology

- **Memory monitoring**: Real-time RAM usage tracking
- **Large file detection**: Auto-switch to streaming mode
- **Progress tracking**: Visual progress bars
- **Error recovery**: Graceful handling of processing errors
- **Chunk processing**: Memory-efficient batch processing

## 📊 Excel Integration

- **Import/Export**: Seamless Excel file handling
- **Template generation**: Auto-create input templates
- **Batch processing**: Handle thousands of calculations
- **Format validation**: Smart data structure checking

## 🎨 UI/UX Features

- **Modern interface**: Clean, responsive design
- **Real-time feedback**: Instant visual updates
- **Color coding**: Intuitive status indicators
- **Interactive plots**: Zoom, pan, navigate charts
- **Progress monitoring**: Live processing updates

## 🔮 Version Support

- Casio fx799, fx880, fx801
- TL-compatible encoding
- Multi-version keylog mapping

## 🤝 Contributing

Welcome contributions! Please feel free to submit issues and pull requests.

## 📝 License

MIT License - see LICENSE file for details.

## 🌟 Changelog

### v2.1.1 (Latest)
- ✨ **NEW**: Coordinate plotting feature in Geometry Mode
- 🎨 Real-time 2D/3D visualization
- 📊 Interactive matplotlib integration
- 🔍 Auto-scale and zoom capabilities
- 🎯 Color-coded A/B group display
- 📐 Support for all geometric shapes
- 🚫 Plot hidden during Excel import mode
- 🧪 Added comprehensive test suite

### v2.1.0
- 🔥 Anti-crash Excel processing
- 💾 Memory-efficient large file handling
- 📈 Progress tracking and monitoring
- 🎯 Enhanced UI/UX

---

**Made with ❤️ by singed2905**

🚀 **Try the new coordinate plotting feature today!**