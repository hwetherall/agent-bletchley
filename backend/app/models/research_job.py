"""
Pydantic models for research jobs.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class ResearchJobStatus(str, Enum):
    """Research job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResearchJobCreate(BaseModel):
    """Model for creating a new research job."""
    query: str = Field(..., description="The research query or question")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context for the research")


class ResearchJob(BaseModel):
    """Model representing a research job."""
    id: str = Field(..., description="Unique job identifier")
    query: str = Field(..., description="The research query")
    status: ResearchJobStatus = Field(..., description="Current job status")
    progress: float = Field(0.0, ge=0.0, le=100.0, description="Progress percentage")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Gathered sources")
    iterations: List[Dict[str, Any]] = Field(default_factory=list, description="Research iterations")
    report: Optional[str] = Field(None, description="Final research report")
    error: Optional[str] = Field(None, description="Error message if job failed")
    
    class Config:
        """Pydantic config."""
        use_enum_values = True

