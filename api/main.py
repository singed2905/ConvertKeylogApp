from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from contextlib import asynccontextmanager
import os
import sys
import json
import uuid
from datetime import datetime
import asyncio

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Global services instances
equation_service = None
polynomial_service = None
geometry_service = None
excel_processor = None

# Job storage (in production, use Redis or database)
active_jobs = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    global equation_service, polynomial_service, geometry_service, excel_processor
    
    try:
        # Import services
        from services.equation.equation_service import EquationService
        from services.polynomial.polynomial_service import PolynomialService
        from services.geometry.geometry_service import GeometryService
        from services.excel.excel_processor import ExcelProcessor
        from utils.config_loader import config_loader
        
        print("📂 Loading configuration files...")
        
        # Load proper configurations for each service
        try:
            equation_config = config_loader.get_mode_config("Equation Mode")
            print("✅ Equation config loaded")
        except Exception as e:
            print(f"⚠️ Equation config failed: {e}, using fallback")
            equation_config = {}
            
        try:
            polynomial_config = config_loader.get_mode_config("Polynomial Equation Mode")
            print("✅ Polynomial config loaded")
        except Exception as e:
            print(f"⚠️ Polynomial config failed: {e}, using fallback")
            polynomial_config = {}
            
        try:
            geometry_config = config_loader.get_mode_config("Geometry Mode")
            print("✅ Geometry config loaded")
        except Exception as e:
            print(f"⚠️ Geometry config failed: {e}, using fallback")
            geometry_config = {}
        
        # Initialize services with their respective configs
        equation_service = EquationService(equation_config)
        polynomial_service = PolynomialService(polynomial_config)
        geometry_service = GeometryService(geometry_config)
        excel_processor = ExcelProcessor({})
        
        print("✅ API services initialized successfully with config files")
        
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        print("🔄 Trying fallback initialization...")
        try:
            # Fallback without config
            from services.equation.equation_service import EquationService
            from services.polynomial.polynomial_service import PolynomialService
            from services.geometry.geometry_service import GeometryService
            from services.excel.excel_processor import ExcelProcessor
            
            equation_service = EquationService({})
            polynomial_service = PolynomialService({})
            geometry_service = GeometryService({})
            excel_processor = ExcelProcessor({})
            print("⚠️ API initialized with fallback config (limited functionality)")
        except Exception as fallback_error:
            print(f"💥 Complete initialization failure: {fallback_error}")
            print("API will start with limited functionality")
    
    yield
    
    # Shutdown
    print("📋 Shutting down API services")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="ConvertKeylogApp API",
    description="API for mathematical expression encoding to calculator keylog",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "ConvertKeylogApp API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "equation": "/api/v1/equation/",
            "polynomial": "/api/v1/polynomial/", 
            "geometry": "/api/v1/geometry/",
            "excel": "/api/v1/excel/",
            "system": "/api/v1/system/"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "equation": equation_service is not None,
            "polynomial": polynomial_service is not None,
            "geometry": geometry_service is not None,
            "excel": excel_processor is not None
        }
    }

# Simple inline routers to avoid import issues
@app.post("/api/v1/equation/solve")
async def solve_equation_system(request: dict) -> dict:
    """Solve equation system"""
    try:
        if not equation_service:
            raise HTTPException(status_code=500, detail="Equation service not initialized")
        
        start_time = datetime.now()
        
        # Extract request data
        num_variables = request.get("num_variables", 2)
        calculator_version = request.get("calculator_version", "fx799")
        equations = request.get("equations", [])
        
        # Set service parameters
        equation_service.set_variables_count(num_variables)
        equation_service.set_version(calculator_version)
        
        # Convert equations to input format
        equation_inputs = []
        for eq in equations:
            coeffs = eq.get("coefficients", [])
            equation_inputs.append(",".join(coeffs))
        
        # Process workflow
        success, status_msg, solutions_text, keylog = equation_service.process_complete_workflow(equation_inputs)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "success": True,
            "data": {
                "solution_status": solutions_text,
                "keylog": keylog,
                "processing_time_ms": round(processing_time, 2),
                "num_variables": num_variables,
                "calculator_version": calculator_version,
                "encoded_coefficients": equation_service.get_encoded_coefficients_display()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/v1/geometry/encode")
async def encode_geometry_problem(request: dict) -> dict:
    """Encode geometry problem"""
    try:
        if not geometry_service:
            raise HTTPException(status_code=500, detail="Geometry service not initialized")
        
        start_time = datetime.now()
        
        # Extract request data
        operation = request.get("operation")
        calculator_version = request.get("calculator_version", "fx799")
        shape_a = request.get("shape_a", {})
        shape_b = request.get("shape_b")
        
        # Set operation and shapes
        geometry_service.set_current_operation(operation)
        shape_b_type = shape_b.get("type") if shape_b else None
        geometry_service.set_current_shapes(shape_a.get("type"), shape_b_type)
        
        # Set dimensions
        dim_a = "3" if shape_a.get("dimension") == "3D" else "2"
        dim_b = "3" if shape_b and shape_b.get("dimension") == "3D" else "2"
        geometry_service.set_kich_thuoc(dim_a, dim_b)
        
        # Extract and process data
        data_a = extract_shape_data_simple(shape_a)
        data_b = extract_shape_data_simple(shape_b) if shape_b else {}
        
        # Process shapes
        result_a, result_b = geometry_service.thuc_thi_tat_ca(data_a, data_b)
        encoded_result = geometry_service.generate_final_result()
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "success": True,
            "data": {
                "encoded_result": encoded_result,
                "processing_time_ms": round(processing_time, 2),
                "operation": operation,
                "calculator_version": calculator_version
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

def extract_shape_data_simple(shape_dict) -> Dict[str, str]:
    """Extract data from shape dictionary"""
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

@app.get("/api/v1/equation/config")
async def get_equation_config():
    """Get equation configuration"""
    return {
        "success": True,
        "data": {
            "mode": "equation",
            "supported_variables": [2, 3, 4],
            "calculator_versions": ["fx799", "fx800", "fx801", "fx802", "fx803"],
            "behavior": {
                "version": "2.2",
                "always_generate_keylog": True,
                "solution_analysis": "rank_based"
            }
        }
    }

@app.get("/api/v1/geometry/config")
async def get_geometry_config():
    """Get geometry configuration"""
    return {
        "success": True,
        "data": {
            "shapes": ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"],
            "operations": ["Tương giao", "Khoảng cách", "Diện tích", "Thể tích", "PT đường thẳng"],
            "calculator_versions": ["fx799", "fx800"],
            "total_combinations": 25
        }
    }

@app.get("/api/v1/system/status")
async def get_system_status():
    """Get system status"""
    return {
        "success": True,
        "data": {
            "version": "2.2.0",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "modes_available": ["equation", "polynomial", "geometry"],
            "api_capabilities": {
                "single_processing": True,
                "batch_processing": True,
                "excel_processing": True,
                "large_file_support": True
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)