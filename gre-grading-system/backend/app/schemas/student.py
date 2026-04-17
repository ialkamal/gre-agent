"""Pydantic schemas for student data."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StudentCreate(BaseModel):
    """Schema for creating a new student."""
    email: str
    name: str
    target_score: Optional[float] = Field(default=None, ge=0, le=6)


class StudentUpdate(BaseModel):
    """Schema for updating student info."""
    name: Optional[str] = None
    target_score: Optional[float] = Field(default=None, ge=0, le=6)


class StudentResponse(BaseModel):
    """Schema for student API responses."""
    id: str
    email: str
    name: str
    target_score: Optional[float]
    created_at: datetime
    total_essays: int = 0
    average_score: Optional[float] = None
    
    model_config = {"from_attributes": True}
