"""
Supabase database client for Agent Bletchley research jobs.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID
from supabase import create_client, Client
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Supabase client singleton
_supabase_client: Optional[Client] = None


def get_client() -> Client:
    """Get or create Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Initialized Supabase client")
    return _supabase_client


async def create_job(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a new research job in the database.
    
    Args:
        query: The research query
        context: Optional context dictionary
        
    Returns:
        Job ID as string
    """
    try:
        client = get_client()
        
        job_data = {
            "query": query,
            "status": "pending",
            "progress": 0.0,
            "context": context or {}
        }
        
        response = await asyncio.to_thread(
            lambda: client.table("research_jobs").insert(job_data).execute()
        )
        
        if response.data and len(response.data) > 0:
            job_id = str(response.data[0]["id"])
            logger.info(f"Created research job {job_id} with query: {query}")
            return job_id
        else:
            raise ValueError("No data returned from database insert")
            
    except Exception as e:
        logger.error(f"Error creating research job: {e}", exc_info=True)
        raise


async def update_job_status(
    job_id: str, 
    status: str, 
    progress: Optional[float] = None
) -> None:
    """
    Update research job status and progress.
    
    Args:
        job_id: The job ID
        status: New status (pending, running, completed, failed, cancelled)
        progress: Optional progress percentage (0-100)
    """
    try:
        client = get_client()
        
        update_data: Dict[str, Any] = {"status": status}
        
        if progress is not None:
            # Ensure progress is within bounds
            update_data["progress"] = max(0.0, min(100.0, float(progress)))
        
        # Set completed_at timestamp if status is "completed"
        if status == "completed":
            from datetime import datetime, timezone
            update_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        await asyncio.to_thread(
            lambda: client.table("research_jobs")
            .update(update_data)
            .eq("id", job_id)
            .execute()
        )
        
        logger.info(f"Updated job {job_id} status to {status}" + 
                   (f" with progress {progress}" if progress is not None else ""))
        
    except Exception as e:
        logger.error(f"Error updating job {job_id} status: {e}", exc_info=True)
        raise


async def update_job_report(job_id: str, report: str) -> None:
    """
    Update research job report.
    
    Args:
        job_id: The job ID
        report: The final research report
    """
    try:
        client = get_client()
        
        await asyncio.to_thread(
            lambda: client.table("research_jobs")
            .update({"report": report})
            .eq("id", job_id)
            .execute()
        )
        
        logger.info(f"Updated job {job_id} report")
        
    except Exception as e:
        logger.error(f"Error updating job {job_id} report: {e}", exc_info=True)
        raise


async def add_iteration(
    job_id: str, 
    step: int, 
    action: str, 
    results: Optional[Dict[str, Any]] = None
) -> str:
    """
    Add a research iteration to the database.
    
    Args:
        job_id: The job ID
        step: Step number
        action: Action description
        results: Optional results dictionary
        
    Returns:
        Iteration ID as string
    """
    try:
        client = get_client()
        
        iteration_data = {
            "job_id": job_id,
            "step": step,
            "action": action,
            "results": results or {}
        }
        
        response = await asyncio.to_thread(
            lambda: client.table("research_iterations")
            .insert(iteration_data)
            .execute()
        )
        
        if response.data and len(response.data) > 0:
            iteration_id = str(response.data[0]["id"])
            logger.info(f"Added iteration {iteration_id} for job {job_id}, step {step}")
            return iteration_id
        else:
            raise ValueError("No data returned from database insert")
            
    except Exception as e:
        logger.error(f"Error adding iteration for job {job_id}: {e}", exc_info=True)
        raise


async def add_source(
    job_id: str,
    url: str,
    title: Optional[str] = None,
    snippet: Optional[str] = None,
    content: Optional[str] = None
) -> str:
    """
    Add a research source to the database (with upsert for duplicate URLs).
    
    Args:
        job_id: The job ID
        url: Source URL
        title: Optional source title
        snippet: Optional snippet
        content: Optional full content
        
    Returns:
        Source ID as string
    """
    try:
        client = get_client()
        
        source_data = {
            "job_id": job_id,
            "url": url,
            "title": title,
            "snippet": snippet,
            "content": content
        }
        
        # Use upsert to handle duplicate URLs per job
        # The UNIQUE constraint on (job_id, url) will handle conflicts
        # Supabase will automatically detect the unique constraint
        try:
            # Try insert first
            response = await asyncio.to_thread(
                lambda: client.table("research_sources")
                .insert(source_data)
                .execute()
            )
        except Exception as insert_error:
            # If insert fails due to duplicate, try update
            if "duplicate" in str(insert_error).lower() or "unique" in str(insert_error).lower():
                # Update existing source
                response = await asyncio.to_thread(
                    lambda: client.table("research_sources")
                    .update(source_data)
                    .eq("job_id", job_id)
                    .eq("url", url)
                    .execute()
                )
            else:
                raise
        
        if response.data and len(response.data) > 0:
            source_id = str(response.data[0]["id"])
            logger.info(f"Added/updated source {source_id} for job {job_id}: {url}")
            return source_id
        else:
            raise ValueError("No data returned from database upsert")
            
    except Exception as e:
        logger.error(f"Error adding source for job {job_id}: {e}", exc_info=True)
        raise


async def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a research job with related iterations and sources.
    
    Args:
        job_id: The job ID
        
    Returns:
        Complete job data as dictionary, or None if not found
    """
    try:
        client = get_client()
        
        # Fetch job
        job_response = await asyncio.to_thread(
            lambda: client.table("research_jobs")
            .select("*")
            .eq("id", job_id)
            .execute()
        )
        
        if not job_response.data or len(job_response.data) == 0:
            logger.warning(f"Job {job_id} not found")
            return None
        
        job = job_response.data[0]
        
        # Convert UUID to string
        job["id"] = str(job["id"])
        
        # Fetch iterations
        iterations_response = await asyncio.to_thread(
            lambda: client.table("research_iterations")
            .select("*")
            .eq("job_id", job_id)
            .order("step")
            .execute()
        )
        
        iterations = []
        if iterations_response.data:
            for iteration in iterations_response.data:
                iteration["id"] = str(iteration["id"])
                iteration["job_id"] = str(iteration["job_id"])
                iterations.append(iteration)
        
        # Fetch sources
        sources_response = await asyncio.to_thread(
            lambda: client.table("research_sources")
            .select("*")
            .eq("job_id", job_id)
            .order("fetched_at")
            .execute()
        )
        
        sources = []
        if sources_response.data:
            for source in sources_response.data:
                source["id"] = str(source["id"])
                source["job_id"] = str(source["job_id"])
                sources.append(source)
        
        # Combine job with iterations and sources
        job["iterations"] = iterations
        job["sources"] = sources
        
        logger.info(f"Retrieved job {job_id} with {len(iterations)} iterations and {len(sources)} sources")
        return job
        
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}", exc_info=True)
        raise


async def list_jobs(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """
    List research jobs with pagination.
    
    Args:
        skip: Number of jobs to skip
        limit: Maximum number of jobs to return
        
    Returns:
        List of job dictionaries
    """
    try:
        client = get_client()
        
        response = await asyncio.to_thread(
            lambda: client.table("research_jobs")
            .select("*")
            .order("created_at", desc=True)
            .range(skip, skip + limit - 1)
            .execute()
        )
        
        jobs = []
        if response.data:
            for job in response.data:
                job["id"] = str(job["id"])
                jobs.append(job)
        
        logger.info(f"Listed {len(jobs)} jobs (skip={skip}, limit={limit})")
        return jobs
        
    except Exception as e:
        logger.error(f"Error listing jobs: {e}", exc_info=True)
        raise

