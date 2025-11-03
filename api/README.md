# ConvertKeylogApp API

> RESTful API for mathematical expression encoding to calculator keylog

## 🚀 Quick Start

### Installation

```bash
# Install API dependencies
cd api
pip install -r requirements.txt

# Run the API server
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 📋 API Endpoints Overview

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API root information |
| `/health` | GET | Basic health check |
| `/api/v1/system/status` | GET | Comprehensive system status |

### Equation Mode

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/equation/solve` | POST | Solve equation system |
| `/api/v1/equation/config` | GET | Get equation configuration |

### Geometry Mode

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/geometry/encode` | POST | Encode geometry problem |
| `/api/v1/geometry/config` | GET | Get geometry configuration |

## 🔧 Usage Examples

### Equation Mode Example

```bash
curl -X POST "http://localhost:8000/api/v1/equation/solve" \
  -H "Content-Type: application/json" \
  -d '{
    "num_variables": 2,
    "calculator_version": "fx799",
    "equations": [
      {"coefficients": ["2", "1", "8"]},
      {"coefficients": ["1", "-1", "1"]}
    ]
  }'
```

### Geometry Mode Example

```bash
curl -X POST "http://localhost:8000/api/v1/geometry/encode" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "Tương giao",
    "calculator_version": "fx799",
    "shape_a": {
      "type": "Điểm",
      "dimension": "3D",
      "data": {"coordinates": "1,2,3"}
    },
    "shape_b": {
      "type": "Điểm",
      "dimension": "3D",
      "data": {"coordinates": "4,5,6"}
    }
  }'
```

## 🏗️ Architecture

### Directory Structure

```
api/
├── __init__.py          # Package initialization
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic models for request/response
├── requirements.txt     # Python dependencies
└── README.md           # This documentation
```

### Service Integration

The API integrates directly with existing ConvertKeylogApp services:

- **EquationService**: `services/equation/equation_service.py`
- **PolynomialService**: `services/polynomial/polynomial_service.py`  
- **GeometryService**: `services/geometry/geometry_service.py`
- **ExcelProcessor**: `services/excel/excel_processor.py`

### Key Features

✅ **Direct Service Integration**: No code duplication, wraps existing services
✅ **Simplified Architecture**: Inline endpoints for reliability
✅ **Error Handling**: Standardized error responses with details
✅ **System Monitoring**: Health checks and status endpoints
✅ **Interactive Documentation**: Auto-generated API docs

## 🚦 Response Formats

### Success Response
```json
{
  "success": true,
  "data": {
    "encoded_result": "wj1131=2=3=CqT11T1234=5=6=CqT2T1RT2=",
    "processing_time_ms": 156,
    ...
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "message": "Internal server error: ...",
    "timestamp": "2025-11-03T12:30:45.123Z"
  }
}
```

## 🔧 Configuration

### Supported Calculator Versions

- **Equation Mode**: fx799, fx800, fx801, fx802, fx803
- **Geometry Mode**: fx799, fx800

### Processing Capabilities

- **Equation Systems**: 2×2, 3×3, 4×4 variable systems
- **Geometry**: 25 combinations (5 shapes × 5 operations)
- **Large File Support**: Chunked processing with memory monitoring

## 🚀 Deployment

### Development
```bash
# Run with auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# Run with multiple workers
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

**Version**: 1.0.0  
**Compatible with**: ConvertKeylogApp v2.2  
**Framework**: FastAPI  
**Python**: 3.9+
