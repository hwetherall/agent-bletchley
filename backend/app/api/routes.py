"""
REST API routes for research jobs.
"""
import logging
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.research_job import ResearchJob, ResearchJobCreate, ResearchJobStatus
from app.orchestrator.research_engine import ResearchEngine
from app.api.websocket import manager as connection_manager
from app.db.supabase_client import create_job, get_job, list_jobs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/research", tags=["research"])
research_engine = ResearchEngine()


@router.post("/jobs", response_model=ResearchJob)
async def create_research_job(
    job_data: ResearchJobCreate,
    background_tasks: BackgroundTasks
) -> ResearchJob:
    """
    Create a new research job.
    
    Args:
        job_data: Research job creation data
        background_tasks: FastAPI background tasks
        
    Returns:
        Created research job
    """
    # Store job in database
    job_id = await create_job(job_data.query, job_data.context)
    logger.info(f"Created research job {job_id} with query: {job_data.query}")
    
    # Start research in background with WebSocket support
    background_tasks.add_task(
        research_engine.start_research,
        job_data.query,
        job_id,
        connection_manager
    )
    
    # Fetch and return the created job
    db_job = await get_job(job_id)
    if not db_job:
        raise HTTPException(status_code=500, detail="Failed to retrieve created job")
    
    # Convert database dict to ResearchJob model
    job = _dict_to_research_job(db_job)
    return job


@router.get("/jobs/{job_id}", response_model=ResearchJob)
async def get_research_job(job_id: str) -> ResearchJob:
    """
    Get a research job by ID.
    
    Args:
        job_id: Research job ID
        
    Returns:
        Research job
    """
    # Fetch job from database
    db_job = await get_job(job_id)
    
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Convert database dict to ResearchJob model
    job = _dict_to_research_job(db_job)
    return job


@router.get("/jobs", response_model=List[ResearchJob])
async def list_research_jobs(
    skip: int = 0,
    limit: int = 100
) -> List[ResearchJob]:
    """
    List all research jobs.
    
    Args:
        skip: Number of jobs to skip
        limit: Maximum number of jobs to return
        
    Returns:
        List of research jobs
    """
    # Fetch jobs from database with pagination
    db_jobs = await list_jobs(skip, limit)
    
    # Convert list of dicts to list of ResearchJob models
    jobs = [_dict_to_research_job(db_job) for db_job in db_jobs]
    return jobs


def _dict_to_research_job(db_job: dict) -> ResearchJob:
    """
    Convert database dictionary to ResearchJob model.
    
    Args:
        db_job: Database job dictionary
        
    Returns:
        ResearchJob model instance
    """
    # Parse timestamps
    created_at = db_job.get("created_at")
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    
    updated_at = db_job.get("updated_at")
    if updated_at and isinstance(updated_at, str):
        updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    
    completed_at = db_job.get("completed_at")
    if completed_at and isinstance(completed_at, str):
        completed_at = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
    
    return ResearchJob(
        id=str(db_job["id"]),
        query=db_job["query"],
        status=ResearchJobStatus(db_job["status"]),
        progress=float(db_job.get("progress", 0.0)),
        created_at=created_at or datetime.utcnow(),
        updated_at=updated_at,
        completed_at=completed_at,
        sources=db_job.get("sources", []),
        iterations=db_job.get("iterations", []),
        report=db_job.get("report"),
        error=db_job.get("error")
    )


@router.delete("/jobs/{job_id}")
async def delete_research_job(job_id: str) -> dict:
    """
    Delete a research job.
    
    Args:
        job_id: Research job ID
        
    Returns:
        Success message
    """
    # TODO: Delete job from database
    
    return {"message": "Job deleted"}

