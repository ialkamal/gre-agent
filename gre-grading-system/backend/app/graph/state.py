"""LangGraph state definitions."""
from typing import Optional, Annotated
from pydantic import BaseModel, Field
from operator import add
from app.schemas import (
    GraderResult,
    ConsensusResult,
    WeakArea,
    GradingDimension,
)


class GradingState(BaseModel):
    """State object for the grading workflow."""
    
    # Input
    student_id: str
    essay_prompt: str
    essay_text: str
    session_id: Optional[str] = None
    
    # Historical context (loaded from memory)
    weak_areas: list[WeakArea] = Field(default_factory=list)
    previous_scores: dict[str, list[float]] = Field(default_factory=dict)
    session_context: Optional[str] = None
    
    # Grading results (accumulated as graders complete)
    grader_results: Annotated[list[GraderResult], add] = Field(default_factory=list)
    
    # Consensus (final output)
    consensus: Optional[ConsensusResult] = None
    
    # Metadata
    fact_checks_performed: int = 0
    total_grading_time_ms: int = 0
    errors: list[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True


class SessionMemoryState(BaseModel):
    """Session memory state for maintaining conversation context."""
    session_id: str
    student_id: str
    
    # Current session data
    essays_graded: int = 0
    current_essay_id: Optional[str] = None
    
    # Conversation history (for context)
    messages: list[dict] = Field(default_factory=list)
    
    # Session-specific insights
    session_weak_areas: list[str] = Field(default_factory=list)
    session_improvements: list[str] = Field(default_factory=list)
