"""Student database model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.orm import relationship
from app.db.database import Base


class Student(Base):
    """Student model for tracking users."""
    __tablename__ = "students"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    target_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Aggregated stats (updated after each grading)
    total_essays = Column(Integer, default=0)
    average_score = Column(Float, nullable=True)
    
    # Relationships
    essays = relationship("Essay", back_populates="student")
    dimension_history = relationship("DimensionHistory", back_populates="student")
