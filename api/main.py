from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
import os
import sys
import json
import uuid
from datetime import datetime
import asyncio

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.equation.equation_service import EquationService
from services.polynomial.polynomial_service import PolynomialService
from services.geometry.geometry_service import GeometryService
from services.excel.excel_processor import ExcelProcessor
from utils.config_loader import config_loader

# Initialize FastAPI app
app = FastAPI(
    title="ConvertKeylogApp API",
    description="API for mathematical expression encoding to calculator keylog",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services instances
equation_service = None
polynomial_service = None
geometry_service = None
excel_processor = None

# Job storage (in production, use Redis or database)
active_jobs = {}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global equation_service, polynomial_service, geometry_service, excel_processor
    
    try:
        # Load configurations
        config = config_loader.load_all_configs()
        
        # Initialize services
        equation_service = EquationService(config)
        polynomial_service = PolynomialService(config)
        geometry_service = GeometryService(config)
        excel_processor = ExcelProcessor(config)
        
        print("✅ API services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        raise

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
