# INTERNAL IMPORTS
from utils import CacheManager
from data_models import JDWRequest, StartResponse, StatusResponse
from graph import graphbuilder
# from graph import create_multi_job_comparison_graph

# REQUEST PROCESSING MODULE
from langchain.schema import Document
from uuid import uuid4

# API HANDLING MODULE
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Security, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager

# UTILITIES 
import os
import sys
from typing_extensions import Callable, Dict, List, AnyStr, Any
from dotenv import load_dotenv
import logging

# LOAD ENVIRONMENT VARIABLES 
load_dotenv()

# INITIALIZE CACHE MANAGER
cache_manager = CacheManager()

# DEFINE GLOBAL VARIABLES
validate_extract_agent = None

# INITIALIZE LOGGING
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_langgraph_app():
    """
    Import and initialize your LangGraph application.
    This is separated to avoid circular imports and to allow for dynamic loading.
    """
    # Import your actual LangGraph application components here
    # This is placeholder code - replace with actual imports for your app
    try:
        from graph import graphbuilder
        
        # Create and return the graph
        return graphbuilder()
    except ImportError:
        # For development/testing, return a placeholder
        print("WARNING: Using mock LangGraph application!")
        return None

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        cache_manager.set('compiled_jdw_graph', create_langgraph_app())
        yield  # Yield control to the application
    except Exception as e:
        print(f"Warning: Failed to initialize LangGraph application: {e}")
        print("API will run in mock mode.")
        yield  # Still yield, allowing the app to start (mock mode)

# INITIALIZE FASTAPI APPLICATION
app = FastAPI(
    title="AI-POWERED JOB DESCRIPTION WRITER TOOL API",
    description="API for compiling job descriptions using pre-defined job credentials.",
    version="1.0.0",
    lifespan=lifespan
)

# CONFIGURE RATE LIMITING
limiter = Limiter(key_func=get_remote_address, application_limits=["5/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# SECURITY HEADERS MIDDLEWARE
@app.middleware("http")
async def add_security_headers(request: Request, call_next: Callable) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# CONFIGURE CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IN-MEMORY JOB TRACKING
jobs = {}

# API KEY SECURITY
API_KEY_NAME = "DIREC-AI-JDW-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# CONFIGURE DEFAULT OR ALLOWED API KEYS
API_KEYS = {
    os.getenv("JDW_AGENT_API_KEY"): "USER-ADMIN"
}

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header in API_KEYS:
        return api_key_header
    raise HTTPException(
        status_code=403,
        detail="INVALID API KEY"
    )

def run_jdwriter(trace_id: str, job_openings: List[Dict[AnyStr, Any]]):
    """BACKGROUND TASK TO RUN ANALYSIS"""
    try:
        # Update job status to running
        jobs[trace_id]["status"] = "running"
        
        # Convert request models to the format expected by LangGraph
        input_data = {
            "job_openings": job_openings,
        }
        
        # Update progress tracking
        for job in job_openings:
            jobs[trace_id]["progress"][job['name']] = "pending"
        
        # COMPILE THE JOB DESCRIPTION WRITER (JDW) GRAPH
        if not cache_manager.has('compiled_jdw_graph'):
            cache_manager.set('compiled_jdw_graph', graphbuilder())

        jdw_graph = cache_manager.get('compiled_jdw_graph')

        if jdw_graph:
            # EXECUTE THE GRAPH
            result = jdw_graph.invoke(input_data)
            print(f'---JDW GRAPH WROTE: {result}---')
            
            # Store results
            jobs[trace_id]["results"] = result
            jobs[trace_id]["status"] = "completed"
    except Exception as e:
        # Update job status to failed
        jobs[trace_id]["status"] = "failed"
        jobs[trace_id]["error"] = str(e)
        print(f"Error processing job {trace_id}: {e}")


# DEFINE ROOT ENDPOINT
@app.get("/ai")
def root(api_key: str = Depends(get_api_key)):
    return {"Welcome": "You are now inside DBTI's AI ENDPOINT!"}

@app.get("/ai/jdw/v1/health")
async def health_check(api_key: str = Depends(get_api_key)):
    """Health check endpoint"""
    return {"status": "ok"}

# DEFINE AND SECURE ENDPOINT FOR THE JDW AGENTS
@app.post("/ai/jdw/v1/job_description_writer", response_model=StartResponse, status_code=200)
@limiter.limit("5/minute") # 5 CLIENT REQUESTS PER MINUTE
async def start_writing(request:Request, writer_request: JDWRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    try:
        # LOG THE REQUEST
        logger.info(f"PROCESSING REQUEST FOR API KEY: {api_key[:8]}...")
        
        # GENERATE UNIQUE TRACE ID
        trace_id = str(uuid4())

        # INITIALIZE JOB TRACKING
        jobs[trace_id] = {
            "status": "pending",
            "progress": {},
            "results": None,
            "error": None
        }

        # START BACKGROUND TASK
        background_tasks.add_task(
            run_jdwriter, 
            trace_id=trace_id,
            job_openings=writer_request.job_openings
        )
        
        return {
            "trace_id": trace_id,
            "message": "Writer started"
        }
    except HTTPException as http_exc:
        logger.error(f"HTTP EXCEPTION: {str(http_exc)}")
        raise http_exc
    except Exception as e:
        logger.error(f"GENERAL EXCEPTION: {str(e)}")
        return JSONResponse(content={"status":"error", "message": str(e)}, status_code=500)

@app.get("/ai/jdw/v1/status/{trace_id}", response_model=StatusResponse)
async def get_status(trace_id: str):
    """Get the status of an analysis job"""
    if trace_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[trace_id]
    
    return {
        "trace_id": trace_id,
        "status": job["status"],
        "progress": job["progress"],
        "results": job["results"] if job["status"] == "completed" else None
    }

# ERROR HANDLER FOR INVALID API KEYS
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )