"""
FastAPI Backend for CFAR Framework

REST API for simulation control, configuration management, and data access
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import yaml
import subprocess
import tempfile
import os
from pathlib import Path
import uuid
from datetime import datetime

# Import CFAR Framework components
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / "engine"))
from resolution_engine.state import State
from resolution_engine.dynamics import step
from resolution_engine.controller_fluctuation import FluctuationController

app = FastAPI(
    title="CFAR Framework API",
    description="REST API for Constraint-Fluctuation-Attention-Resolution Framework",
    version="0.1.0"
)

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for simulation jobs (use database in production)
simulation_jobs = {}
simulation_results = {}

# Pydantic models for API
class SimulationConfig(BaseModel):
    target_Y: float
    horizon_days: int
    init_state: Dict[str, float]
    pid: Dict[str, float]
    fluctuation: Dict[str, Any]
    fast_arms: List[Dict[str, Any]]
    na_inputs: Dict[str, Any]
    lambda_inputs: Dict[str, Any]
    k1_inputs: Dict[str, Any]
    reward_threshold: float

class SimulationJob(BaseModel):
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    created_at: str
    config: SimulationConfig
    result_path: Optional[str] = None
    error_message: Optional[str] = None

class SimulationResult(BaseModel):
    job_id: str
    metadata: Dict[str, Any]
    summary: Dict[str, Any]
    simulation_data: List[Dict[str, Any]]

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "CFAR Framework API",
        "version": "0.1.0",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "active_jobs": len([j for j in simulation_jobs.values() if j["status"] == "running"]),
        "completed_jobs": len([j for j in simulation_jobs.values() if j["status"] == "completed"]),
        "total_jobs": len(simulation_jobs),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/simulations/", response_model=SimulationJob)
async def create_simulation(config: SimulationConfig, background_tasks: BackgroundTasks):
    """Create and start a new simulation job"""
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Create job record
    job = {
        "job_id": job_id,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "config": config.dict(),
        "result_path": None,
        "error_message": None
    }
    
    simulation_jobs[job_id] = job
    
    # Start simulation in background
    background_tasks.add_task(run_simulation_job, job_id)
    
    return SimulationJob(**job)

@app.get("/simulations/{job_id}", response_model=SimulationJob)
async def get_simulation_job(job_id: str):
    """Get simulation job status"""
    
    if job_id not in simulation_jobs:
        raise HTTPException(status_code=404, detail="Simulation job not found")
    
    job = simulation_jobs[job_id]
    return SimulationJob(**job)

@app.get("/simulations/{job_id}/result", response_model=SimulationResult)
async def get_simulation_result(job_id: str):
    """Get simulation results"""
    
    if job_id not in simulation_jobs:
        raise HTTPException(status_code=404, detail="Simulation job not found")
    
    job = simulation_jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Simulation not completed. Status: {job['status']}")
    
    if job_id in simulation_results:
        return SimulationResult(job_id=job_id, **simulation_results[job_id])
    
    # Load results from file
    if job["result_path"] and Path(job["result_path"]).exists():
        with open(job["result_path"], 'r') as f:
            results = json.load(f)
        
        simulation_results[job_id] = results
        return SimulationResult(job_id=job_id, **results)
    
    raise HTTPException(status_code=500, detail="Results not available")

@app.get("/simulations/", response_model=List[SimulationJob])
async def list_simulation_jobs():
    """List all simulation jobs"""
    
    jobs = []
    for job_data in simulation_jobs.values():
        jobs.append(SimulationJob(**job_data))
    
    return sorted(jobs, key=lambda x: x.created_at, reverse=True)

@app.delete("/simulations/{job_id}")
async def delete_simulation_job(job_id: str):
    """Delete a simulation job and its results"""
    
    if job_id not in simulation_jobs:
        raise HTTPException(status_code=404, detail="Simulation job not found")
    
    job = simulation_jobs[job_id]
    
    # Clean up result file
    if job["result_path"] and Path(job["result_path"]).exists():
        os.remove(job["result_path"])
    
    # Remove from memory
    del simulation_jobs[job_id]
    if job_id in simulation_results:
        del simulation_results[job_id]
    
    return {"message": "Simulation job deleted successfully"}

@app.get("/configs/default")
async def get_default_config():
    """Get default simulation configuration"""
    
    config_path = Path(__file__).parent.parent.parent / "engine" / "configs" / "littering.yml"
    
    if not config_path.exists():
        raise HTTPException(status_code=404, detail="Default configuration not found")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config

@app.post("/configs/validate")
async def validate_config(config: SimulationConfig):
    """Validate a simulation configuration"""
    
    try:
        # Basic validation
        errors = []
        
        if not 0 <= config.target_Y <= 1:
            errors.append("target_Y must be between 0 and 1")
        
        if config.horizon_days <= 0:
            errors.append("horizon_days must be positive")
        
        # Validate initial state
        required_state_vars = ['Y', 'N', 'A', 'C', 'B']
        for var in required_state_vars:
            if var not in config.init_state:
                errors.append(f"Missing initial state variable: {var}")
            elif not 0 <= config.init_state[var] <= 1:
                errors.append(f"Initial state {var} must be between 0 and 1")
        
        # Validate PID parameters
        if config.pid['kp'] < 0 or config.pid['ki'] < 0 or config.pid['kd'] < 0:
            errors.append("PID gains must be non-negative")
        
        if errors:
            return {"valid": False, "errors": errors}
        else:
            return {"valid": True, "message": "Configuration is valid"}
            
    except Exception as e:
        return {"valid": False, "errors": [f"Validation error: {str(e)}"]}

@app.post("/analysis/compare")
async def compare_simulations(job_ids: List[str]):
    """Compare multiple simulation results"""
    
    if len(job_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 simulations required for comparison")
    
    comparison_data = []
    
    for job_id in job_ids:
        if job_id not in simulation_jobs:
            raise HTTPException(status_code=404, detail=f"Simulation job {job_id} not found")
        
        job = simulation_jobs[job_id]
        if job["status"] != "completed":
            raise HTTPException(status_code=400, detail=f"Simulation {job_id} not completed")
        
        # Get results
        if job_id in simulation_results:
            results = simulation_results[job_id]
        else:
            with open(job["result_path"], 'r') as f:
                results = json.load(f)
                simulation_results[job_id] = results
        
        # Extract comparison metrics
        comparison_data.append({
            "job_id": job_id,
            "target_Y": results["metadata"]["target_Y"],
            "final_Y": results["summary"]["final_state"]["Y"],
            "final_error": results["summary"]["final_error"],
            "target_achieved": results["summary"]["target_achieved"],
            "max_Y": results["summary"]["max_Y_achieved"],
            "days_above_target": results["summary"]["days_above_target"],
            "precision_days": results["summary"].get("control_mode_usage", {}).get("precision_days", 0),
            "fluctuation_days": results["summary"].get("control_mode_usage", {}).get("fluctuation_days", 0),
            "fluctuation_pulses": results["summary"].get("total_fluctuation_pulses", 0),
            "created_at": simulation_jobs[job_id]["created_at"]
        })
    
    return {
        "comparison": comparison_data,
        "summary": {
            "best_performance": max(comparison_data, key=lambda x: x["final_Y"]),
            "most_stable": min(comparison_data, key=lambda x: abs(x["final_error"])),
            "most_fluctuation_pulses": max(comparison_data, key=lambda x: x["fluctuation_pulses"]),
            "comparison_count": len(comparison_data)
        }
    }

async def run_simulation_job(job_id: str):
    """Background task to run simulation"""
    
    job = simulation_jobs[job_id]
    job["status"] = "running"
    
    try:
        # Create temporary config file
        config_data = job["config"]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_data, f, default_flow_style=False)
            config_path = f.name
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name
        
        # Run simulation
        project_root = Path(__file__).parent.parent.parent
        result = subprocess.run([
            "python", "engine/cli.py", "run",
            "--config", config_path,
            "--output", output_path
        ], capture_output=True, text=True, cwd=project_root,
           encoding='utf-8', errors='replace')
        
        if result.returncode == 0:
            job["status"] = "completed"
            job["result_path"] = output_path
        else:
            job["status"] = "failed"
            job["error_message"] = result.stderr or "Unknown error"
        
        # Clean up config file
        os.remove(config_path)
        
    except Exception as e:
        job["status"] = "failed"
        job["error_message"] = str(e)
    
    simulation_jobs[job_id] = job

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
