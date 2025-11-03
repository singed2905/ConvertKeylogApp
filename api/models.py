from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class CalculatorVersion(str, Enum):
    """Supported calculator versions"""
    FX799 = "fx799"
    FX800 = "fx800"
    FX801 = "fx801"
    FX802 = "fx802"
    FX803 = "fx803"
    FX991 = "fx991"
    FX570 = "fx570"
    FX580 = "fx580"
    FX115 = "fx115"

class NumVariables(int, Enum):
    """Number of variables for equation systems"""
    TWO = 2
    THREE = 3
    FOUR = 4

class PolynomialDegree(int, Enum):
    """Polynomial degrees"""
    DEGREE_2 = 2
    DEGREE_3 = 3
    DEGREE_4 = 4

class GeometryShape(str, Enum):
    """Geometry shapes"""
    POINT = "Điểm"
    LINE = "Đường thẳng"
    PLANE = "Mặt phẳng"
    CIRCLE = "Đường tròn"
    SPHERE = "Mặt cầu"

class GeometryOperation(str, Enum):
    """Geometry operations"""
    INTERSECTION = "Tương giao"
    DISTANCE = "Khoảng cách"
    AREA = "Diện tích"
    VOLUME = "Thể tích"
    LINE_EQUATION = "PT đường thẳng"

class Dimension(str, Enum):
    """Coordinate dimensions"""
    TWO_D = "2D"
    THREE_D = "3D"

# ========== EQUATION MODELS ==========

class EquationCoefficients(BaseModel):
    """Coefficients for a single equation"""
    coefficients: List[str] = Field(..., description="List of equation coefficients")

class EquationSolveRequest(BaseModel):
    """Request to solve equation system"""
    num_variables: NumVariables = Field(..., description="Number of variables (2, 3, or 4)")
    calculator_version: CalculatorVersion = Field(default=CalculatorVersion.FX799)
    equations: List[EquationCoefficients] = Field(..., description="List of equations")

class EquationSolveResponse(BaseModel):
    """Response from equation solving"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

# ========== POLYNOMIAL MODELS ==========

class PolynomialCoefficients(BaseModel):
    """Polynomial coefficients"""
    a: str = Field(..., description="Coefficient of highest degree term")
    b: Optional[str] = Field(None, description="Coefficient of second highest degree term")
    c: Optional[str] = Field(None, description="Coefficient of third highest degree term")
    d: Optional[str] = Field(None, description="Coefficient of fourth highest degree term")
    e: Optional[str] = Field(None, description="Coefficient of constant term")

class PolynomialSolveRequest(BaseModel):
    """Request to solve polynomial"""
    degree: PolynomialDegree = Field(..., description="Polynomial degree (2, 3, or 4)")
    calculator_version: CalculatorVersion = Field(default=CalculatorVersion.FX799)
    coefficients: PolynomialCoefficients = Field(..., description="Polynomial coefficients")

class PolynomialSolveResponse(BaseModel):
    """Response from polynomial solving"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

# ========== GEOMETRY MODELS ==========

class PointData(BaseModel):
    """Point coordinate data"""
    coordinates: str = Field(..., description="Coordinates as comma-separated string")

class LineData(BaseModel):
    """Line data"""
    point: str = Field(..., description="Point on line as comma-separated string")
    vector: str = Field(..., description="Direction vector as comma-separated string")

class PlaneData(BaseModel):
    """Plane data"""
    coefficients: Dict[str, str] = Field(..., description="Plane coefficients {a, b, c, d}")

class CircleData(BaseModel):
    """Circle data"""
    center: str = Field(..., description="Center coordinates as comma-separated string")
    radius: str = Field(..., description="Radius value")

class SphereData(BaseModel):
    """Sphere data"""
    center: str = Field(..., description="Center coordinates as comma-separated string")
    radius: str = Field(..., description="Radius value")

class GeometryShapeData(BaseModel):
    """Geometry shape with data"""
    type: GeometryShape = Field(..., description="Shape type")
    dimension: Optional[Dimension] = Field(None, description="Dimension for points")
    data: Union[PointData, LineData, PlaneData, CircleData, SphereData] = Field(..., description="Shape-specific data")

class GeometryEncodeRequest(BaseModel):
    """Request to encode geometry problem"""
    operation: GeometryOperation = Field(..., description="Geometry operation")
    calculator_version: CalculatorVersion = Field(default=CalculatorVersion.FX799)
    shape_a: GeometryShapeData = Field(..., description="First shape")
    shape_b: Optional[GeometryShapeData] = Field(None, description="Second shape (if needed)")

class GeometryEncodeResponse(BaseModel):
    """Response from geometry encoding"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

# ========== BATCH PROCESSING MODELS ==========

class BatchItem(BaseModel):
    """Single item in batch processing"""
    id: str = Field(..., description="Unique identifier for this item")
    data: Dict[str, Any] = Field(..., description="Item-specific data")

class BatchRequest(BaseModel):
    """Batch processing request"""
    mode: str = Field(..., description="Processing mode (equation, polynomial, geometry)")
    parameters: Dict[str, Any] = Field(..., description="Mode-specific parameters")
    batch_data: List[BatchItem] = Field(..., description="List of items to process")

class BatchResponse(BaseModel):
    """Batch processing response"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

# ========== ERROR MODELS ==========

class ErrorDetail(BaseModel):
    """Error detail structure"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
