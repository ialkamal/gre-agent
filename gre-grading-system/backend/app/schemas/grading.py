"""Pydantic schemas for grading requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class GradingDimension(str, Enum):
    """The 8 grading dimensions for GRE Issue Writing."""
    THESIS = "thesis"
    REASONING = "reasoning"
    EVIDENCE = "evidence"
    STRUCTURE = "structure"
    ANALYSIS = "analysis"
    LANGUAGE = "language"
    GRAMMAR = "grammar"
    COHERENCE = "coherence"


class DimensionScore(BaseModel):
    """Score and feedback for a single dimension."""
    dimension: GradingDimension
    score: float = Field(ge=0, le=6, description="Score from 0-6 (GRE scale)")
    feedback: str = Field(description="Specific feedback for this dimension")
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)


class GraderResult(BaseModel):
    """Result from a single grader (containing all 8 dimension scores)."""
    grader_id: int
    dimension_scores: list[DimensionScore]
    overall_score: float = Field(ge=0, le=6)
    overall_feedback: str
    grading_time_ms: int
    fact_checks_count: int = Field(default=0, description="Number of fact checks performed")


class GradingRequest(BaseModel):
    """Request to grade an essay."""
    student_id: str
    essay_prompt: str = Field(description="The GRE Issue Writing prompt")
    essay_text: str = Field(description="Student's essay response")
    session_id: Optional[str] = Field(default=None, description="Session ID for memory")


class ConsensusResult(BaseModel):
    """Consensus result combining all graders."""
    dimension_scores: list[DimensionScore]
    overall_score: float = Field(ge=0, le=6)
    score_variance: dict[str, float] = Field(description="Variance per dimension")
    high_variance_dimensions: list[GradingDimension] = Field(
        default_factory=list,
        description="Dimensions with variance > 1.5"
    )
    merged_feedback: str
    strengths: list[str]
    priority_improvements: list[str] = Field(
        description="Improvements prioritized by weak areas"
    )


class WeakArea(BaseModel):
    """A weak area identified from historical performance."""
    dimension: GradingDimension
    average_score: float
    trend: str = Field(description="improving, declining, or stable")
    recommendation: str


class ModelEssay(BaseModel):
    """A rewritten model essay that would score 6 across all dimensions."""
    model_essay: str = Field(description="The rewritten essay demonstrating excellence")
    improvement_notes: str = Field(description="Notes explaining key improvements made")
    word_count: int


class GradingResponse(BaseModel):
    """Full grading response including consensus and weak areas."""
    request_id: str
    student_id: str
    timestamp: datetime
    
    # Individual grader results (for transparency)
    grader_results: list[GraderResult]
    
    # Consensus result
    consensus: ConsensusResult
    
    # Historical context
    weak_areas: list[WeakArea] = Field(default_factory=list)
    improvement_from_last: Optional[dict[str, float]] = Field(
        default=None,
        description="Score changes from last essay per dimension"
    )
    
    # Model essay (rewritten version scoring 6)
    model_essay: Optional[ModelEssay] = Field(
        default=None,
        description="Rewritten version of essay that would score 6 across all dimensions"
    )
    
    # Metadata
    total_grading_time_ms: int
    fact_checks_performed: int = 0


class StudentHistory(BaseModel):
    """Student's historical performance summary."""
    student_id: str
    total_essays: int
    average_overall_score: float
    dimension_averages: dict[str, float]
    weak_areas: list[WeakArea]
    score_trend: list[float] = Field(description="Last N overall scores")
    last_grading: Optional[datetime] = None
