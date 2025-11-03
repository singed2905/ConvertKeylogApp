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
import tempfile
import pandas as pd

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
        "available_endpoints": {
            "equation": {
                "solve": "POST /api/v1/equation/solve",
                "batch": "POST /api/v1/equation/process-batch",
                "status": "GET /api/v1/equation/status/{job_id}",
                "config": "GET /api/v1/equation/config"
            },
            "geometry": {
                "encode": "POST /api/v1/geometry/encode",
                "batch": "POST /api/v1/geometry/process-batch",
                "excel_upload": "POST /api/v1/geometry/excel/upload",
                "excel_process": "POST /api/v1/geometry/excel/process",
                "config": "GET /api/v1/geometry/config"
            },
            "system": {
                "health": "GET /health",
                "status": "GET /api/v1/system/status"
            }
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


# ========== EQUATION MODE APIs ==========

@app.post("/api/v1/equation/solve")
async def solve_equation_system(request: dict) -> dict:
    """
    Solve equation system

    Example:
    {
        "num_variables": 2,
        "calculator_version": "fx799",
        "equations": [
            {"coefficients": ["2", "1", "8"]},
            {"coefficients": ["1", "-1", "1"]}
        ]
    }
    """
    try:
        if not equation_service:
            raise HTTPException(status_code=500, detail="Equation service not initialized")

        start_time = datetime.now()

        # Extract request data
        num_variables = request.get("num_variables", 2)
        calculator_version = request.get("calculator_version", "fx799")
        equations = request.get("equations", [])

        # Validate input
        if len(equations) != num_variables:
            raise HTTPException(
                status_code=400,
                detail=f"Number of equations ({len(equations)}) must match number of variables ({num_variables})"
            )

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
                "encoded_coefficients": equation_service.get_encoded_coefficients_display(),
                "workflow_success": success,
                "status_message": status_msg
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/equation/process-batch")
async def process_equation_batch(
        background_tasks: BackgroundTasks,
        request: dict
) -> dict:
    """
    Process multiple equation systems in batch

    Example:
    {
        "num_variables": 2,
        "calculator_version": "fx799",
        "batch_data": [
            {
                "id": "eq_001",
                "equations": [
                    {"coefficients": ["2", "1", "8"]},
                    {"coefficients": ["1", "-1", "1"]}
                ]
            },
            {
                "id": "eq_002",
                "equations": [
                    {"coefficients": ["3", "4", "10"]},
                    {"coefficients": ["1", "2", "5"]}
                ]
            }
        ]
    }
    """
    try:
        if not equation_service:
            raise HTTPException(status_code=500, detail="Equation service not initialized")

        # Generate job ID
        job_id = f"eq_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # Initialize job tracking
        active_jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "total_items": len(request.get("batch_data", [])),
            "processed_items": 0,
            "success_count": 0,
            "error_count": 0,
            "results": [],
            "created_at": datetime.now().isoformat(),
            "type": "equation_batch"
        }

        # Start background processing
        background_tasks.add_task(process_batch_equations, job_id, request)

        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "status": "queued",
                "total_items": len(request.get("batch_data", [])),
                "estimated_time_seconds": len(request.get("batch_data", [])) * 0.5
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start batch processing: {str(e)}")


@app.get("/api/v1/equation/status/{job_id}")
async def get_equation_job_status(job_id: str) -> dict:
    """Get status of equation batch processing job"""
    try:
        if job_id not in active_jobs:
            raise HTTPException(status_code=404, detail="Job not found")

        job_info = active_jobs[job_id]

        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "status": job_info["status"],
                "progress": job_info["progress"],
                "processed_items": job_info["processed_items"],
                "total_items": job_info["total_items"],
                "success_count": job_info["success_count"],
                "error_count": job_info["error_count"],
                "results": job_info["results"] if job_info["status"] == "completed" else None,
                "created_at": job_info["created_at"],
                "type": job_info.get("type", "unknown")
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@app.get("/api/v1/equation/config")
async def get_equation_config():
    """Get equation configuration"""
    return {
        "success": True,
        "data": {
            "mode": "equation",
            "supported_variables": [2, 3, 4],
            "calculator_versions": ["fx799", "fx800", "fx801", "fx802", "fx803"],
            "tl_mappings": {
                "fx799": {
                    "2_var": "w912",
                    "3_var": "w913",
                    "4_var": "w914"
                }
            },
            "expression_support": {
                "functions": ["sqrt", "sin", "cos", "tan", "log", "ln"],
                "constants": ["pi", "e"],
                "operators": ["^", "/", "*", "+", "-"]
            },
            "behavior": {
                "version": "2.2",
                "always_generate_keylog": True,
                "solution_analysis": "rank_based"
            }
        }
    }


# ========== GEOMETRY MODE APIs ==========

@app.post("/api/v1/geometry/encode")
async def encode_geometry_problem(request: dict) -> dict:
    """
    Encode geometry problem

    Example:
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

        # Extract request data
        operation = request.get("operation")
        calculator_version = request.get("calculator_version", "fx799")
        shape_a = request.get("shape_a", {})
        shape_b = request.get("shape_b")

        if not operation:
            raise HTTPException(status_code=400, detail="Operation is required")
        if not shape_a:
            raise HTTPException(status_code=400, detail="shape_a is required")

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
                "calculator_version": calculator_version,
                "shape_a_processed": result_a is not None,
                "shape_b_processed": result_b is not None,
                "shapes_info": {
                    "shape_a": {
                        "type": shape_a.get("type"),
                        "dimension": shape_a.get("dimension")
                    },
                    "shape_b": {
                        "type": shape_b.get("type") if shape_b else None,
                        "dimension": shape_b.get("dimension") if shape_b else None
                    }
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/geometry/process-batch")
async def process_geometry_batch(
        background_tasks: BackgroundTasks,
        request: dict
) -> dict:
    """
    Process multiple geometry problems in batch

    Example:
    {
        "operation": "Tương giao",
        "calculator_version": "fx799",
        "batch_data": [
            {
                "id": "geo_001",
                "shape_a": {
                    "type": "Điểm",
                    "dimension": "2D",
                    "data": {"coordinates": "1,2"}
                },
                "shape_b": {
                    "type": "Điểm",
                    "dimension": "2D",
                    "data": {"coordinates": "3,4"}
                }
            }
        ]
    }
    """
    try:
        if not geometry_service:
            raise HTTPException(status_code=500, detail="Geometry service not initialized")

        # Generate job ID
        job_id = f"geo_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # Initialize job tracking
        active_jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "total_items": len(request.get("batch_data", [])),
            "processed_items": 0,
            "success_count": 0,
            "error_count": 0,
            "results": [],
            "created_at": datetime.now().isoformat(),
            "type": "geometry_batch"
        }

        # Start background processing
        background_tasks.add_task(process_batch_geometry, job_id, request)

        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "status": "queued",
                "total_items": len(request.get("batch_data", [])),
                "estimated_time_seconds": len(request.get("batch_data", [])) * 0.8
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start batch processing: {str(e)}")


@app.post("/api/v1/geometry/excel/upload")
async def upload_geometry_excel(
        file: UploadFile = File(...),
        shape_a: str = Form(...),
        shape_b: str = Form(None),
        operation: str = Form(...)
):
    """Upload Excel file for geometry processing"""
    try:
        if not excel_processor:
            raise HTTPException(status_code=500, detail="Excel processor not initialized")

        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            temp_path = tmp_file.name

        try:
            # Check if large file
            is_large, file_info = excel_processor.is_large_file(temp_path)

            if is_large:
                return {
                    "success": True,
                    "file_info": file_info,
                    "message": "Large file detected - requires chunked processing",
                    "recommended_action": "use_chunked_processing",
                    "temp_file_id": os.path.basename(temp_path)
                }

            # Get file info
            file_info = excel_processor.get_file_info(temp_path)

            # Validate structure
            df = excel_processor.read_excel_data(temp_path)
            is_valid, missing_cols = excel_processor.validate_excel_structure(df, shape_a, shape_b)

            # Quality check
            quality_info = excel_processor.validate_data_quality(df, shape_a, shape_b)

            return {
                "success": True,
                "file_info": file_info,
                "structure_valid": is_valid,
                "missing_columns": missing_cols,
                "quality_info": quality_info,
                "sample_data": df.head(3).to_dict('records'),
                "temp_file_id": os.path.basename(temp_path)
            }

        except Exception as e:
            # Cleanup temp file on error
            try:
                os.unlink(temp_path)
            except:
                pass
            raise e

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel upload failed: {str(e)}")


@app.post("/api/v1/geometry/excel/process")
async def process_geometry_excel(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        shape_a: str = Form(...),
        shape_b: str = Form(None),
        operation: str = Form(...),
        dimension_a: str = Form("2D"),
        dimension_b: str = Form("2D")
):
    """Process Excel file for geometry calculations"""
    try:
        if not excel_processor or not geometry_service:
            raise HTTPException(status_code=500, detail="Services not initialized")

        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")

        # Generate job ID
        job_id = f"excel_geo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            temp_path = tmp_file.name

        # Initialize job tracking
        active_jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "total_items": 0,
            "processed_items": 0,
            "success_count": 0,
            "error_count": 0,
            "results": None,
            "created_at": datetime.now().isoformat(),
            "type": "excel_geometry",
            "temp_file": temp_path,
            "parameters": {
                "shape_a": shape_a,
                "shape_b": shape_b,
                "operation": operation,
                "dimension_a": dimension_a,
                "dimension_b": dimension_b
            }
        }

        # Start background processing
        background_tasks.add_task(process_excel_geometry_background, job_id)

        return {
            "success": True,
            "data": {
                "job_id": job_id,
                "status": "queued",
                "message": "Excel processing started"
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel processing failed: {str(e)}")


@app.get("/api/v1/geometry/config")
async def get_geometry_config():
    """Get geometry configuration"""
    return {
        "success": True,
        "data": {
            "shapes": ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"],
            "operations": ["Tương giao", "Khoảng cách", "Diện tích", "Thể tích", "PT đường thẳng"],
            "calculator_versions": ["fx799", "fx800"],
            "dimensions": ["2D", "3D"],
            "total_combinations": 25,
            "excel_support": {
                "formats": [".xlsx", ".xls"],
                "large_file_threshold_mb": 20,
                "large_file_threshold_rows": 50000,
                "chunked_processing": True
            }
        }
    }


# ========== SYSTEM APIs ==========

@app.get("/api/v1/system/status")
async def get_system_status():
    """Get system status"""
    return {
        "success": True,
        "data": {
            "version": "2.2.0",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "modes_available": ["equation", "geometry"],
            "active_jobs": len(active_jobs),
            "api_capabilities": {
                "single_processing": True,
                "batch_processing": True,
                "excel_processing": True,
                "large_file_support": True
            }
        }
    }


@app.get("/api/v1/jobs")
async def list_active_jobs():
    """List all active jobs"""
    return {
        "success": True,
        "data": {
            "active_jobs": len(active_jobs),
            "jobs": [
                {
                    "job_id": job_id,
                    "status": job_info["status"],
                    "type": job_info.get("type", "unknown"),
                    "progress": job_info["progress"],
                    "created_at": job_info["created_at"]
                }
                for job_id, job_info in active_jobs.items()
            ]
        }
    }


# ========== HELPER FUNCTIONS ==========

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


async def process_batch_equations(job_id: str, request: dict):
    """Background task to process batch equations"""
    try:
        job_info = active_jobs[job_id]
        job_info["status"] = "processing"

        num_variables = request.get("num_variables")
        calculator_version = request.get("calculator_version", "fx799")
        batch_data = request.get("batch_data", [])

        # Set service parameters
        equation_service.set_variables_count(num_variables)
        equation_service.set_version(calculator_version)

        results = []

        for i, item in enumerate(batch_data):
            try:
                # Process single item
                equations = item.get("equations", [])
                item_id = item.get("id", f"item_{i}")

                start_time = datetime.now()

                # Convert equations to input format
                equation_inputs = []
                for eq in equations:
                    coeffs = eq.get("coefficients", [])
                    equation_inputs.append(",".join(coeffs))

                # Process workflow
                success, status_msg, solutions_text, keylog = equation_service.process_complete_workflow(
                    equation_inputs)

                processing_time = (datetime.now() - start_time).total_seconds() * 1000

                results.append({
                    "id": item_id,
                    "success": success,
                    "solution_status": solutions_text,
                    "keylog": keylog,
                    "processing_time_ms": round(processing_time, 2),
                    "encoded_coefficients": equation_service.get_encoded_coefficients_display()
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


async def process_batch_geometry(job_id: str, request: dict):
    """Background task to process batch geometry"""
    try:
        job_info = active_jobs[job_id]
        job_info["status"] = "processing"

        operation = request.get("operation")
        calculator_version = request.get("calculator_version", "fx799")
        batch_data = request.get("batch_data", [])

        results = []

        for i, item in enumerate(batch_data):
            try:
                item_id = item.get("id", f"geo_item_{i}")
                shape_a = item.get("shape_a", {})
                shape_b = item.get("shape_b")

                start_time = datetime.now()

                # Set operation and shapes
                geometry_service.set_current_operation(operation)
                shape_b_type = shape_b.get("type") if shape_b else None
                geometry_service.set_current_shapes(shape_a.get("type"), shape_b_type)

                # Set dimensions
                dim_a = "3" if shape_a.get("dimension") == "3D" else "2"
                dim_b = "3" if shape_b and shape_b.get("dimension") == "3D" else "2"
                geometry_service.set_kich_thuoc(dim_a, dim_b)

                # Process data
                data_a = extract_shape_data_simple(shape_a)
                data_b = extract_shape_data_simple(shape_b) if shape_b else {}

                # Process shapes
                result_a, result_b = geometry_service.thuc_thi_tat_ca(data_a, data_b)
                encoded_result = geometry_service.generate_final_result()

                processing_time = (datetime.now() - start_time).total_seconds() * 1000

                results.append({
                    "id": item_id,
                    "success": True,
                    "encoded_result": encoded_result,
                    "processing_time_ms": round(processing_time, 2),
                    "operation": operation
                })

                job_info["success_count"] += 1

            except Exception as e:
                results.append({
                    "id": item.get("id", f"geo_item_{i}"),
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


async def process_excel_geometry_background(job_id: str):
    """Background task to process Excel geometry file"""
    try:
        job_info = active_jobs[job_id]
        job_info["status"] = "processing"

        temp_path = job_info["temp_file"]
        params = job_info["parameters"]

        # Read Excel file
        df = excel_processor.read_excel_data(temp_path)
        job_info["total_items"] = len(df)

        # Process each row
        encoded_results = []

        for index, row in df.iterrows():
            try:
                # Set geometry service parameters
                geometry_service.set_current_operation(params["operation"])
                geometry_service.set_current_shapes(params["shape_a"], params["shape_b"])

                dim_a = "3" if params["dimension_a"] == "3D" else "2"
                dim_b = "3" if params["dimension_b"] == "3D" else "2"
                geometry_service.set_kich_thuoc(dim_a, dim_b)

                # Extract row data
                data_a = excel_processor.extract_shape_data(row, params["shape_a"], 'A')
                data_b = excel_processor.extract_shape_data(row, params["shape_b"], 'B') if params["shape_b"] else {}

                # Process
                result_a, result_b = geometry_service.thuc_thi_tat_ca(data_a, data_b)
                encoded_result = geometry_service.generate_final_result()

                encoded_results.append(encoded_result)
                job_info["success_count"] += 1

            except Exception as e:
                encoded_results.append(f"Error: {str(e)}")
                job_info["error_count"] += 1

            # Update progress
            job_info["processed_items"] = index + 1
            job_info["progress"] = round((index + 1) / len(df) * 100, 1)

        # Export results
        output_path = f"results_{job_id}.xlsx"
        result_file = excel_processor.export_results(df, encoded_results, output_path)

        # Complete job
        job_info["status"] = "completed"
        job_info["results"] = {
            "total_processed": len(encoded_results),
            "success_count": job_info["success_count"],
            "error_count": job_info["error_count"],
            "output_file": result_file
        }
        job_info["completed_at"] = datetime.now().isoformat()

        # Cleanup temp file
        try:
            os.unlink(temp_path)
        except:
            pass

    except Exception as e:
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)

        # Cleanup temp file
        try:
            if "temp_file" in active_jobs[job_id]:
                os.unlink(active_jobs[job_id]["temp_file"])
        except:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
