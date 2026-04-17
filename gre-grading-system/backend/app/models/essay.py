"""Essay and grading result models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.database import Base


class Essay(Base):
    """Essay submission model."""
    __tablename__ = "essays"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    
    # Embedding for similarity search
    embedding = Column(Vector(1536), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Final consensus scores
    overall_score = Column(Float, nullable=True)
    
    # Merged feedback from consensus
    merged_feedback = Column(Text, nullable=True)
    
    # Model essay (score 6 version)
    model_essay = Column(Text, nullable=True)
    model_essay_notes = Column(Text, nullable=True)
    
    # Relationships
    student = relationship("Student", back_populates="essays")
    grading_results = relationship("GradingResult", back_populates="essay")
    dimension_scores = relationship("EssayDimensionScore", back_populates="essay")


class GradingResult(Base):
    """Individual grader result (one per grader per essay)."""
    __tablename__ = "grading_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    essay_id = Column(String, ForeignKey("essays.id"), nullable=False, index=True)
    grader_id = Column(Integer, nullable=False)  # 0, 1, or 2
    
    # Scores stored as JSON for flexibility
    dimension_scores = Column(JSON, nullable=False)
    overall_score = Column(Float, nullable=False)
    overall_feedback = Column(Text, nullable=False)
    
    # Fact checking count
    fact_checks_count = Column(Integer, default=0)
    
    # Metadata
    grading_time_ms = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    model_used = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    essay = relationship("Essay", back_populates="grading_results")


class EssayDimensionScore(Base):
    """Consensus dimension scores for an essay (for easy querying)."""
    __tablename__ = "essay_dimension_scores"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    essay_id = Column(String, ForeignKey("essays.id"), nullable=False, index=True)
    dimension = Column(String, nullable=False, index=True)
    
    score = Column(Float, nullable=False)
    feedback = Column(Text, nullable=False)
    strengths = Column(JSON, default=list)
    improvements = Column(JSON, default=list)
    
    # Variance across graders
    score_variance = Column(Float, nullable=True)
    
    # Relationships
    essay = relationship("Essay", back_populates="dimension_scores")


class DimensionHistory(Base):
    """Track dimension scores over time for weak area detection."""
    __tablename__ = "dimension_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    dimension = Column(String, nullable=False, index=True)
    
    # Running statistics
    total_essays = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    recent_scores = Column(JSON, default=list)  # Last N scores
    trend = Column(String, default="stable")  # improving, declining, stable
    
    # Timestamps
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="dimension_history")
