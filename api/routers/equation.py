from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import uuid
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.models import (
    EquationSolveRequest, EquationSolveResponse,
    JobStatusResponse, ErrorDetail
)
from services.equation.equation_service import EquationService
from utils.config_loader import config_loader

router = APIRouter(prefix="/api/v1/equation", tags=["equation"])

# Global service instance
equation_service = None
active_jobs = {}

@router.on_event("startup")
async def startup_equation_router():
    """Initialize equation service"""
    global equation_service
    try:
        config = config_loader.load_all_configs()
        equation_service = EquationService(config)
        print("✅ Equation router initialized")
    except Exception as e:
        print(f"❌ Failed to initialize equation router: {e}")

@router.post("/solve", response_model=EquationSolveResponse)
async def solve_equation_system(request: EquationSolveRequest) -> EquationSolveResponse:
    """
    Solve equation system and return encoded keylog
    
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
        
        # Validate input
        if len(request.equations) != request.num_variables:
            raise HTTPException(
                status_code=400,
                detail=f"Number of equations ({len(request.equations)}) must match number of variables ({request.num_variables})"
            )
        
        # Set service parameters
        equation_service.set_so_an(request.num_variables)
        equation_service.set_phien_ban(request.calculator_version)
        
        # Process equations
        equations_data = []
        for i, eq in enumerate(request.equations):
            equation_data = ",".join(eq.coefficients)
            equations_data.append(equation_data)
        
        # Execute solving and encoding
        encoded_coefficients = []
        for i, eq_data in enumerate(equations_data):
            equation_service.set_current_equation(i + 1)
            encoded_row = equation_service.xu_ly_phuong_trinh_hien_tai(eq_data)
            encoded_coefficients.append(encoded_row)
        
        # Generate final keylog
        keylog = equation_service.tao_chuoi_ket_qua_cuoi_cung()
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return EquationSolveResponse(
            success=True,
            data={
                "encoded_coefficients": encoded_coefficients,
                "solution_status": "Hệ vô nghiệm hoặc vô số nghiệm",  # v2.2 behavior
                "keylog": keylog,
                "processing_time_ms": round(processing_time, 2),
                "num_variables": request.num_variables,
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

@router.post("/process-batch", response_model=JobStatusResponse)
async def process_equation_batch(
    background_tasks: BackgroundTasks,
    request: Dict[str, Any]
) -> JobStatusResponse:
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
            "created_at": datetime.now().isoformat()
        }
        
        # Start background processing
        background_tasks.add_task(process_batch_equations, job_id, request)
        
        return JobStatusResponse(
            success=True,
            data={
                "job_id": job_id,
                "status": "queued",
                "total_items": len(request.get("batch_data", [])),
                "estimated_time_seconds": len(request.get("batch_data", [])) * 0.5  # Rough estimate
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start batch processing: {str(e)}"
        )

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get status of equation batch processing job
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

async def process_batch_equations(job_id: str, request: Dict[str, Any]):
    """
    Background task to process batch equations
    """
    try:
        job_info = active_jobs[job_id]
        job_info["status"] = "processing"
        
        num_variables = request.get("num_variables")
        calculator_version = request.get("calculator_version", "fx799")
        batch_data = request.get("batch_data", [])
        
        # Set service parameters
        equation_service.set_so_an(num_variables)
        equation_service.set_phien_ban(calculator_version)
        
        results = []
        
        for i, item in enumerate(batch_data):
            try:
                # Process single item
                equations = item.get("equations", [])
                item_id = item.get("id", f"item_{i}")
                
                start_time = datetime.now()
                
                # Process equations for this item
                encoded_coefficients = []
                for j, eq in enumerate(equations):
                    equation_service.set_current_equation(j + 1)
                    eq_data = ",".join(eq.get("coefficients", []))
                    encoded_row = equation_service.xu_ly_phuong_trinh_hien_tai(eq_data)
                    encoded_coefficients.append(encoded_row)
                
                # Generate keylog
                keylog = equation_service.tao_chuoi_ket_qua_cuoi_cung()
                
                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                
                results.append({
                    "id": item_id,
                    "success": True,
                    "encoded_coefficients": encoded_coefficients,
                    "keylog": keylog,
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

@router.get("/config", response_model=Dict[str, Any])
async def get_equation_config() -> Dict[str, Any]:
    """
    Get available equation mode configurations
    """
    try:
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
                    "solution_display": "Hệ vô nghiệm hoặc vô số nghiệm"
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get equation config: {str(e)}"
        )
