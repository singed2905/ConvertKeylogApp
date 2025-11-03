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
| `/api/v1/equation/process-batch` | POST | Batch equation processing |
| `/api/v1/equation/status/{job_id}` | GET | Get job status |
| `/api/v1/equation/config` | GET | Get equation configuration |

### Polynomial Mode

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/polynomial/solve` | POST | Solve polynomial equation |
| `/api/v1/polynomial/process-batch` | POST | Batch polynomial processing |
| `/api/v1/polynomial/status/{job_id}` | GET | Get job status |
| `/api/v1/polynomial/config` | GET | Get polynomial configuration |

### Geometry Mode

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/geometry/encode` | POST | Encode geometry problem |
| `/api/v1/geometry/process-batch` | POST | Batch geometry processing |
| `/api/v1/geometry/validate` | POST | Validate geometry input |
| `/api/v1/geometry/status/{job_id}` | GET | Get job status |
| `/api/v1/geometry/config` | GET | Get geometry configuration |

### System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/system/status` | GET | System status and capabilities |
| `/api/v1/system/config` | GET | System configuration |
| `/api/v1/system/health` | GET | Detailed health check |
| `/api/v1/system/metrics` | GET | System metrics |
| `/api/v1/system/cleanup` | POST | System cleanup |

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

### Polynomial Mode Example

```bash
curl -X POST "http://localhost:8000/api/v1/polynomial/solve" \
  -H "Content-Type: application/json" \
  -d '{
    "degree": 2,
    "calculator_version": "fx799",
    "coefficients": {
      "a": "1",
      "b": "-5",
      "c": "6"
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
├── README.md           # This file
└── routers/            # API route handlers
    ├── __init__.py
    ├── equation.py     # Equation mode endpoints
    ├── polynomial.py   # Polynomial mode endpoints
    ├── geometry.py     # Geometry mode endpoints
    └── system.py       # System monitoring endpoints
```

### Service Integration

The API integrates directly with existing ConvertKeylogApp services:

- **EquationService**: `services/equation/equation_service.py`
- **PolynomialService**: `services/polynomial/polynomial_service.py`  
- **GeometryService**: `services/geometry/geometry_service.py`
- **ExcelProcessor**: `services/excel/excel_processor.py`

### Key Features

✅ **Direct Service Integration**: No code duplication, wraps existing services
✅ **Comprehensive Models**: Pydantic models for all requests/responses
✅ **Error Handling**: Standardized error responses with details
✅ **Background Processing**: Async job processing for batch operations
✅ **System Monitoring**: Health checks, metrics, and status endpoints
✅ **Input Validation**: Comprehensive validation for all inputs
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
    "code": "INVALID_INPUT",
    "message": "Number of equations must match number of variables",
    "details": {
      "provided_equations": 2,
      "required_equations": 3
    },
    "timestamp": "2025-11-03T12:30:45.123Z"
  }
}
```

## 🔧 Configuration

### Supported Calculator Versions

- **Equation Mode**: fx799, fx800, fx801, fx802, fx803
- **Polynomial Mode**: fx799, fx991, fx570, fx580, fx115  
- **Geometry Mode**: fx799, fx800

### Processing Capabilities

- **Equation Systems**: 2×2, 3×3, 4×4 variable systems
- **Polynomials**: Degree 2, 3, 4 with complex root support
- **Geometry**: 25 combinations (5 shapes × 5 operations)
- **Batch Processing**: Background job processing with progress tracking
- **Large File Support**: Chunked processing with memory monitoring

## 📊 Monitoring

### Health Endpoints

- `/health` - Basic service health
- `/api/v1/system/health` - Detailed component health
- `/api/v1/system/status` - Comprehensive system status
- `/api/v1/system/metrics` - Detailed system metrics

### Job Tracking

All batch operations return a `job_id` that can be used to track progress:

```bash
curl "http://localhost:8000/api/v1/equation/status/eq_batch_20251103_001"
```

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

### Docker (Future)
```dockerfile
FROM python:3.11
COPY api/ /app/api/
COPY services/ /app/services/
COPY utils/ /app/utils/
COPY config/ /app/config/
WORKDIR /app
RUN pip install -r api/requirements.txt
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔒 Security Considerations

- **Input Validation**: All inputs validated with Pydantic models
- **Error Handling**: No sensitive information leaked in error responses
- **CORS**: Configurable CORS middleware
- **Rate Limiting**: Can be added with `slowapi` middleware
- **Authentication**: Can be added with JWT tokens

## 📈 Performance

- **Async Processing**: Non-blocking I/O operations
- **Background Jobs**: Heavy processing moved to background tasks
- **Memory Monitoring**: Built-in memory usage tracking
- **Chunked Processing**: Large file processing with progress tracking
- **Service Reuse**: Direct integration with existing optimized services

---

**Version**: 1.0.0  
**Compatible with**: ConvertKeylogApp v2.2  
**Framework**: FastAPI  
**Python**: 3.9+
