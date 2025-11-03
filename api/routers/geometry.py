from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Union
import uuid
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.models import (
    GeometryEncodeRequest, GeometryEncodeResponse,
    PointData, LineData, PlaneData, CircleData, SphereData,
    JobStatusResponse, ErrorDetail
)
from services.geometry.geometry_service import GeometryService
from utils.config_loader import config_loader

router = APIRouter(prefix="/api/v1/geometry", tags=["geometry"])

# Global service instance
geometry_service = None
active_jobs = {}

@router.on_event("startup")
async def startup_geometry_router():
    """Initialize geometry service"""
    global geometry_service
    try:
        config = config_loader.load_all_configs()
        geometry_service = GeometryService(config)
        print("✅ Geometry router initialized")
    except Exception as e:
        print(f"❌ Failed to initialize geometry router: {e}")

@router.post("/encode", response_model=GeometryEncodeResponse)
async def encode_geometry_problem(request: GeometryEncodeRequest) -> GeometryEncodeResponse:
    """
    Encode geometry problem to calculator keylog
    
    Example for 2 points intersection:
    {
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
    }
    """
    try:
        if not geometry_service:
            raise HTTPException(status_code=500, detail="Geometry service not initialized")
        
        start_time = datetime.now()
        
        # Set operation and shapes
        geometry_service.set_current_operation(request.operation)
        shape_b_type = request.shape_b.type if request.shape_b else None
        geometry_service.set_current_shapes(request.shape_a.type, shape_b_type)
        
        # Set dimensions
        dim_a = "3" if not hasattr(request.shape_a, 'dimension') or request.shape_a.dimension == "3D" else "2"
        dim_b = "3" if not request.shape_b or not hasattr(request.shape_b, 'dimension') or request.shape_b.dimension == "3D" else "2"
        geometry_service.set_kich_thuoc(dim_a, dim_b)
        
        # Extract data for shape A
        data_a = extract_shape_data(request.shape_a)
        
        # Extract data for shape B (if exists)
        data_b = {}
        if request.shape_b:
            data_b = extract_shape_data(request.shape_b)
        
        # Process shapes
        result_a, result_b = geometry_service.thuc_thi_tat_ca(data_a, data_b)
        
        # Generate final encoded result
        encoded_result = geometry_service.generate_final_result()
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Prepare detailed processing info
        processing_details = {
            "operation_code": geometry_service.geometry_data["pheptoan_map"].get(request.operation, request.operation),
            "shape_a_encoding": {
                "shape_code": geometry_service._get_shape_code_A(request.shape_a.type),
                "t_code": geometry_service._get_tcode_mapping("A", request.shape_a.type),
                "encoded_values": result_a,
                "encoded_string": geometry_service._get_encoded_values_A()
            },
            "final_format": "wj{shape_a_code}{shape_a_values}C{shape_b_code}{shape_b_values}C{operation_code}{tcode_a}R{tcode_b}="
        }
        
        # Add shape B details if exists
        if request.shape_b:
            processing_details["shape_b_encoding"] = {
                "shape_code": geometry_service._get_shape_code_B(request.shape_b.type),
                "t_code": geometry_service._get_tcode_mapping("B", request.shape_b.type),
                "encoded_values": result_b,
                "encoded_string": geometry_service._get_encoded_values_B()
            }
        
        # Input validation status
        validation_status = {
            "shape_a_valid": len(result_a) > 0,
            "shape_b_valid": len(result_b) > 0 if request.shape_b else True,
            "operation_compatible": True,
            "dimensions_match": True
        }
        
        return GeometryEncodeResponse(
            success=True,
            data={
                "encoded_result": encoded_result,
                "processing_details": processing_details,
                "input_validation": validation_status,
                "processing_time_ms": round(processing_time, 2),
                "operation": request.operation,
                "calculator_version": request.calculator_version
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

def extract_shape_data(shape_data) -> Dict[str, str]:
    """
    Extract data from shape based on its type
    """
    shape_type = shape_data.type
    data = shape_data.data
    
    if shape_type == "Điểm":
        return {"point_input": data.coordinates}
    
    elif shape_type == "Đường thẳng":
        return {
            "line_A1": data.point,
            "line_X1": data.vector
        }
    
    elif shape_type == "Mặt phẳng":
        coeffs = data.coefficients
        return {
            "plane_a": coeffs.get("a", ""),
            "plane_b": coeffs.get("b", ""),
            "plane_c": coeffs.get("c", ""),
            "plane_d": coeffs.get("d", "")
        }
    
    elif shape_type == "Đường tròn":
        return {
            "circle_center": data.center,
            "circle_radius": data.radius
        }
    
    elif shape_type == "Mặt cầu":
        return {
            "sphere_center": data.center,
            "sphere_radius": data.radius
        }
    
    return {}

@router.post("/process-batch", response_model=JobStatusResponse)
async def process_geometry_batch(
    background_tasks: BackgroundTasks,
    request: Dict[str, Any]
) -> JobStatusResponse:
    """
    Process multiple geometry problems in batch
    
    Example:
    {
        "operation": "Tương giao",
        "calculator_version": "fx799",
        "batch_data": [
            {
                "id": "calc_001",
                "shape_a": {"type": "Điểm", "dimension": "3D", "data": {"coordinates": "1,2,3"}},
                "shape_b": {"type": "Điểm", "dimension": "3D", "data": {"coordinates": "4,5,6"}}
            }
        ]
    }
    """
    try:
        if not geometry_service:
            raise HTTPException(status_code=500, detail="Geometry service not initialized")
        
        # Generate job ID
        job_id = f"geom_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Initialize job tracking
        active_jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "total_items": len(request.get("batch_data", [])),
            "processed_items": 0,
            "success_count": 0,
            "error_count": 0,
            "results": [],
            "created_at": datetime.now().isoformat()
        }
        
        # Start background processing
        background_tasks.add_task(process_batch_geometry, job_id, request)
        
        return JobStatusResponse(
            success=True,
            data={
                "job_id": job_id,
                "status": "queued",
                "total_items": len(request.get("batch_data", [])),
                "estimated_time_seconds": len(request.get("batch_data", [])) * 0.8  # Rough estimate
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start batch processing: {str(e)}"
        )

async def process_batch_geometry(job_id: str, request: Dict[str, Any]):
    """
    Background task to process batch geometry problems
    """
    try:
        job_info = active_jobs[job_id]
        job_info["status"] = "processing"
        
        operation = request.get("operation")
        calculator_version = request.get("calculator_version", "fx799")
        batch_data = request.get("batch_data", [])
        
        results = []
        
        for i, item in enumerate(batch_data):
            try:
                # Process single item
                item_id = item.get("id", f"item_{i}")
                shape_a = item.get("shape_a")
                shape_b = item.get("shape_b")
                
                start_time = datetime.now()
                
                # Set operation and shapes
                geometry_service.set_current_operation(operation)
                shape_b_type = shape_b.get("type") if shape_b else None
                geometry_service.set_current_shapes(shape_a.get("type"), shape_b_type)
                
                # Extract and process data
                data_a = extract_shape_data_from_dict(shape_a)
                data_b = extract_shape_data_from_dict(shape_b) if shape_b else {}
                
                geometry_service.thuc_thi_tat_ca(data_a, data_b)
                encoded_result = geometry_service.generate_final_result()
                
                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                
                results.append({
                    "id": item_id,
                    "success": True,
                    "encoded_result": encoded_result,
                    "processing_time_ms": round(processing_time, 2)
                })
                
                job_info["success_count"] += 1
                
            except Exception as e:
                results.append({
                    "id": item.get("id", f"item_{i}"),
                    "success": False,
                    "error": str(e)
                })
                job_info["error_count"] += 1
            
            # Update progress
            job_info["processed_items"] = i + 1
            job_info["progress"] = round((i + 1) / len(batch_data) * 100, 1)
        
        # Complete job
        job_info["status"] = "completed"
        job_info["results"] = results
        job_info["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)

def extract_shape_data_from_dict(shape_dict) -> Dict[str, str]:
    """
    Extract data from shape dictionary (for batch processing)
    """
    if not shape_dict:
        return {}
    
    shape_type = shape_dict.get("type")
    data = shape_dict.get("data", {})
    
    if shape_type == "Điểm":
        return {"point_input": data.get("coordinates", "")}
    
    elif shape_type == "Đường thẳng":
        return {
            "line_A1": data.get("point", ""),
            "line_X1": data.get("vector", "")
        }
    
    elif shape_type == "Mặt phẳng":
        coeffs = data.get("coefficients", {})
        return {
            "plane_a": coeffs.get("a", ""),
            "plane_b": coeffs.get("b", ""),
            "plane_c": coeffs.get("c", ""),
            "plane_d": coeffs.get("d", "")
        }
    
    elif shape_type == "Đường tròn":
        return {
            "circle_center": data.get("center", ""),
            "circle_radius": data.get("radius", "")
        }
    
    elif shape_type == "Mặt cầu":
        return {
            "sphere_center": data.get("center", ""),
            "sphere_radius": data.get("radius", "")
        }
    
    return {}

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_geometry_job_status(job_id: str) -> JobStatusResponse:
    """
    Get status of geometry batch processing job
    """
    try:
        if job_id not in active_jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job_info = active_jobs[job_id]
        
        return JobStatusResponse(
            success=True,
            data={
                "job_id": job_id,
                "status": job_info["status"],
                "progress": job_info["progress"],
                "processed_items": job_info["processed_items"],
                "total_items": job_info["total_items"],
                "success_count": job_info["success_count"],
                "error_count": job_info["error_count"],
                "results": job_info["results"] if job_info["status"] == "completed" else None,
                "created_at": job_info["created_at"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )

@router.post("/validate", response_model=Dict[str, Any])
async def validate_geometry_input(request: GeometryEncodeRequest) -> Dict[str, Any]:
    """
    Validate geometry input without processing
    """
    try:
        validation_errors = []
        
        # Validate shape A
        if request.shape_a:
            shape_a_errors = validate_single_shape(request.shape_a, "shape_a")
            validation_errors.extend(shape_a_errors)
        
        # Validate shape B if provided
        if request.shape_b:
            shape_b_errors = validate_single_shape(request.shape_b, "shape_b")
            validation_errors.extend(shape_b_errors)
        
        # Check operation compatibility
        if request.operation in ["Diện tích", "Thể tích"] and request.shape_b:
            validation_errors.append({
                "field": "shape_b",
                "error": f"Operation '{request.operation}' does not require shape_b",
                "expected": "Remove shape_b for single-shape operations"
            })
        
        if len(validation_errors) == 0:
            return {
                "success": True,
                "data": {
                    "valid": True,
                    "message": "Input validation passed"
                }
            }
        else:
            return {
                "success": False,
                "validation_errors": validation_errors
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )

def validate_single_shape(shape_data, field_prefix: str) -> list:
    """
    Validate a single shape's data
    """
    errors = []
    
    try:
        shape_type = shape_data.type
        data = shape_data.data
        
        if shape_type == "Điểm":
            coords = data.coordinates.split(',')
            if len(coords) < 2:
                errors.append({
                    "field": f"{field_prefix}.data.coordinates",
                    "error": "Point needs at least 2 coordinates",
                    "expected": "Format: 'x,y' or 'x,y,z'"
                })
        
        elif shape_type == "Mặt phẳng":
            coeffs = data.coefficients
            if not any(coeffs.values()):
                errors.append({
                    "field": f"{field_prefix}.data.coefficients",
                    "error": "Plane needs at least one non-zero coefficient",
                    "expected": "Provide values for a, b, c, d"
                })
        
        # Add more validation rules as needed
        
    except Exception as e:
        errors.append({
            "field": field_prefix,
            "error": f"Invalid shape data: {str(e)}",
            "expected": "Valid shape data structure"
        })
    
    return errors

@router.get("/config", response_model=Dict[str, Any])
async def get_geometry_config() -> Dict[str, Any]:
    """
    Get available geometry configurations
    """
    try:
        return {
            "success": True,
            "data": {
                "shapes": ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"],
                "operations": ["Tương giao", "Khoảng cách", "Diện tích", "Thể tích", "PT đường thẳng"],
                "calculator_versions": ["fx799", "fx800"],
                "dimensions": ["2D", "3D"],
                "total_combinations": 25,
                "operation_compatibility": {
                    "Tương giao": {
                        "requires_shape_b": True,
                        "compatible_shapes": ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"]
                    },
                    "Khoảng cách": {
                        "requires_shape_b": True,
                        "compatible_shapes": ["Điểm", "Đường thẳng", "Mặt phẳng"]
                    },
                    "Diện tích": {
                        "requires_shape_b": False,
                        "compatible_shapes": ["Đường tròn", "Mặt cầu"]
                    },
                    "Thể tích": {
                        "requires_shape_b": False,
                        "compatible_shapes": ["Mặt cầu"]
                    },
                    "PT đường thẳng": {
                        "requires_shape_b": False,
                        "compatible_shapes": ["Điểm"]
                    }
                },
                "latex_encoding_support": {
                    "functions": ["sqrt", "sin", "cos", "tan", "ln"],
                    "operators": ["frac", "^", "+", "-", "*", "/"],
                    "constants": ["pi", "e"]
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get geometry config: {str(e)}"
        )
