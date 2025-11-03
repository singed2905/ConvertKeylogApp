from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import uuid
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.models import (
    PolynomialSolveRequest, PolynomialSolveResponse,
    JobStatusResponse, ErrorDetail
)
from services.polynomial.polynomial_service import PolynomialService
from utils.config_loader import config_loader

router = APIRouter(prefix="/api/v1/polynomial", tags=["polynomial"])

# Global service instance
polynomial_service = None
active_jobs = {}

@router.on_event("startup")
async def startup_polynomial_router():
    """Initialize polynomial service"""
    global polynomial_service
    try:
        config = config_loader.load_all_configs()
        polynomial_service = PolynomialService(config)
        print("✅ Polynomial router initialized")
    except Exception as e:
        print(f"❌ Failed to initialize polynomial router: {e}")

@router.post("/solve", response_model=PolynomialSolveResponse)
async def solve_polynomial(request: PolynomialSolveRequest) -> PolynomialSolveResponse:
    """
    Solve polynomial equation and return encoded keylog
    
    Example:
    {
        "degree": 2,
        "calculator_version": "fx799",
        "coefficients": {
            "a": "1",
            "b": "-5",
            "c": "6"
        }
    }
    """
    try:
        if not polynomial_service:
            raise HTTPException(status_code=500, detail="Polynomial service not initialized")
        
        start_time = datetime.now()
        
        # Set service parameters
        polynomial_service.set_bac(request.degree)
        polynomial_service.set_phien_ban(request.calculator_version)
        
        # Extract coefficients based on degree
        coeffs = request.coefficients
        
        if request.degree == 2:
            # Quadratic: ax² + bx + c = 0
            polynomial_service.set_he_so_a(coeffs.a or "0")
            polynomial_service.set_he_so_b(coeffs.b or "0")
            polynomial_service.set_he_so_c(coeffs.c or "0")
            
        elif request.degree == 3:
            # Cubic: ax³ + bx² + cx + d = 0
            polynomial_service.set_he_so_a(coeffs.a or "0")
            polynomial_service.set_he_so_b(coeffs.b or "0")
            polynomial_service.set_he_so_c(coeffs.c or "0")
            polynomial_service.set_he_so_d(coeffs.d or "0")
            
        elif request.degree == 4:
            # Quartic: ax⁴ + bx³ + cx² + dx + e = 0
            polynomial_service.set_he_so_a(coeffs.a or "0")
            polynomial_service.set_he_so_b(coeffs.b or "0")
            polynomial_service.set_he_so_c(coeffs.c or "0")
            polynomial_service.set_he_so_d(coeffs.d or "0")
            polynomial_service.set_he_so_e(coeffs.e or "0")
        
        # Solve polynomial
        roots = polynomial_service.giai_va_hien_thi_nghiem()
        
        # Generate standard form
        standard_form = polynomial_service.tao_dang_chuan()
        
        # Generate encoded coefficients and keylog
        encoded_coeffs = polynomial_service.ma_hoa_he_so()
        keylog = polynomial_service.tao_keylog_hoan_chinh()
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Format roots for response
        formatted_roots = []
        if roots:
            for root in roots:
                if isinstance(root, complex):
                    if abs(root.imag) < 1e-10:  # Essentially real
                        formatted_roots.append({
                            "value": f"{root.real:.6f}".rstrip('0').rstrip('.'),
                            "type": "real"
                        })
                    else:
                        # Complex root
                        real_part = f"{root.real:.6f}".rstrip('0').rstrip('.')
                        imag_part = f"{abs(root.imag):.6f}".rstrip('0').rstrip('.')
                        sign = "+" if root.imag >= 0 else "-"
                        formatted_roots.append({
                            "value": f"{real_part} {sign} {imag_part}i",
                            "type": "complex"
                        })
                else:
                    # Real root
                    formatted_roots.append({
                        "value": f"{float(root):.6f}".rstrip('0').rstrip('.'),
                        "type": "real"
                    })
        
        return PolynomialSolveResponse(
            success=True,
            data={
                "standard_form": standard_form,
                "roots": formatted_roots,
                "keylog": keylog,
                "encoded_coefficients": encoded_coeffs,
                "processing_time_ms": round(processing_time, 2),
                "degree": request.degree,
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
async def process_polynomial_batch(
    background_tasks: BackgroundTasks,
    request: Dict[str, Any]
) -> JobStatusResponse:
    """
    Process multiple polynomial equations in batch
    
    Example:
    {
        "degree": 2,
        "calculator_version": "fx799",
        "batch_data": [
            {
                "id": "poly_001",
                "coefficients": {"a": "1", "b": "-5", "c": "6"}
            },
            {
                "id": "poly_002",
                "coefficients": {"a": "1", "b": "1", "c": "1"}
            }
        ]
    }
    """
    try:
        if not polynomial_service:
            raise HTTPException(status_code=500, detail="Polynomial service not initialized")
        
        # Generate job ID
        job_id = f"poly_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
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
        background_tasks.add_task(process_batch_polynomials, job_id, request)
        
        return JobStatusResponse(
            success=True,
            data={
                "job_id": job_id,
                "status": "queued",
                "total_items": len(request.get("batch_data", [])),
                "estimated_time_seconds": len(request.get("batch_data", [])) * 0.7  # Rough estimate
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start batch processing: {str(e)}"
        )

async def process_batch_polynomials(job_id: str, request: Dict[str, Any]):
    """
    Background task to process batch polynomials
    """
    try:
        job_info = active_jobs[job_id]
        job_info["status"] = "processing"
        
        degree = request.get("degree")
        calculator_version = request.get("calculator_version", "fx799")
        batch_data = request.get("batch_data", [])
        
        # Set service parameters
        polynomial_service.set_bac(degree)
        polynomial_service.set_phien_ban(calculator_version)
        
        results = []
        
        for i, item in enumerate(batch_data):
            try:
                # Process single item
                item_id = item.get("id", f"item_{i}")
                coeffs = item.get("coefficients", {})
                
                start_time = datetime.now()
                
                # Set coefficients based on degree
                if degree == 2:
                    polynomial_service.set_he_so_a(coeffs.get("a", "0"))
                    polynomial_service.set_he_so_b(coeffs.get("b", "0"))
                    polynomial_service.set_he_so_c(coeffs.get("c", "0"))
                    
                elif degree == 3:
                    polynomial_service.set_he_so_a(coeffs.get("a", "0"))
                    polynomial_service.set_he_so_b(coeffs.get("b", "0"))
                    polynomial_service.set_he_so_c(coeffs.get("c", "0"))
                    polynomial_service.set_he_so_d(coeffs.get("d", "0"))
                    
                elif degree == 4:
                    polynomial_service.set_he_so_a(coeffs.get("a", "0"))
                    polynomial_service.set_he_so_b(coeffs.get("b", "0"))
                    polynomial_service.set_he_so_c(coeffs.get("c", "0"))
                    polynomial_service.set_he_so_d(coeffs.get("d", "0"))
                    polynomial_service.set_he_so_e(coeffs.get("e", "0"))
                
                # Solve and generate results
                roots = polynomial_service.giai_va_hien_thi_nghiem()
                standard_form = polynomial_service.tao_dang_chuan()
                keylog = polynomial_service.tao_keylog_hoan_chinh()
                encoded_coeffs = polynomial_service.ma_hoa_he_so()
                
                processing_time = (datetime.now() - start_time).total_seconds() * 1000
                
                # Format roots
                formatted_roots = format_polynomial_roots(roots)
                
                results.append({
                    "id": item_id,
                    "success": True,
                    "standard_form": standard_form,
                    "roots": formatted_roots,
                    "keylog": keylog,
                    "encoded_coefficients": encoded_coeffs,
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

def format_polynomial_roots(roots):
    """
    Format polynomial roots for API response
    """
    formatted_roots = []
    if roots:
        for root in roots:
            if isinstance(root, complex):
                if abs(root.imag) < 1e-10:  # Essentially real
                    formatted_roots.append({
                        "value": f"{root.real:.6f}".rstrip('0').rstrip('.'),
                        "type": "real"
                    })
                else:
                    # Complex root
                    real_part = f"{root.real:.6f}".rstrip('0').rstrip('.')
                    imag_part = f"{abs(root.imag):.6f}".rstrip('0').rstrip('.')
                    sign = "+" if root.imag >= 0 else "-"
                    formatted_roots.append({
                        "value": f"{real_part} {sign} {imag_part}i",
                        "type": "complex"
                    })
            else:
                # Real root
                formatted_roots.append({
                    "value": f"{float(root):.6f}".rstrip('0').rstrip('.'),
                    "type": "real"
                })
    return formatted_roots

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_polynomial_job_status(job_id: str) -> JobStatusResponse:
    """
    Get status of polynomial batch processing job
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

@router.get("/config", response_model=Dict[str, Any])
async def get_polynomial_config() -> Dict[str, Any]:
    """
    Get available polynomial configurations
    """
    try:
        return {
            "success": True,
            "data": {
                "mode": "polynomial",
                "supported_degrees": [2, 3, 4],
                "calculator_versions": {
                    "fx799": {"prefix": "P", "suffix_pattern": "=="},
                    "fx991": {"prefix": "EQN", "suffix_pattern": "=0"},
                    "fx570": {"prefix": "POL", "suffix_pattern": "=ROOT"},
                    "fx580": {"prefix": "POLY", "suffix_pattern": "=SOLVE"},
                    "fx115": {"prefix": "QUAD/CUB/QUAT", "suffix_pattern": "="}
                },
                "keylog_examples": {
                    "degree_2": {
                        "fx799": "P2=1=o5=6==",
                        "fx991": "EQN2=1=o5=6=0",
                        "fx570": "POL2=1=o5=6=ROOT"
                    },
                    "degree_3": {
                        "fx799": "P3=1=0=o1=1===",
                        "fx991": "EQN3=1=0=o1=1==0"
                    }
                },
                "expression_support": {
                    "functions": ["sqrt", "sin", "cos", "tan", "log", "ln"],
                    "constants": ["pi", "e"],
                    "operators": ["^", "/", "*", "+", "-"]
                },
                "solver_info": {
                    "primary_engine": "NumPy roots finding",
                    "fallback_engine": "Analytical methods",
                    "complex_root_support": True,
                    "precision_configurable": True
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get polynomial config: {str(e)}"
        )
