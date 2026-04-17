"""Student management API routes."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate, StudentResponse, StudentHistory
from app.memory import LongTermMemory


router = APIRouter(prefix="/students", tags=["students"])


@router.post("/", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: AsyncSession = Depends(get_db)):
    """Create a new student."""
    # Check if email already exists
    result = await db.execute(
        select(Student).where(Student.email == student.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_student = Student(
        email=student.email,
        name=student.name,
        target_score=student.target_score,
    )
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    
    return db_student


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: str, db: AsyncSession = Depends(get_db)):
    """Get student by ID."""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    update: StudentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update student information."""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if update.name is not None:
        student.name = update.name
    if update.target_score is not None:
        student.target_score = update.target_score
    
    await db.commit()
    await db.refresh(student)
    
    return student


@router.get("/{student_id}/history", response_model=StudentHistory)
async def get_student_history(student_id: str, db: AsyncSession = Depends(get_db)):
    """Get student's grading history and weak areas."""
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    memory = LongTermMemory()
    
    # Get weak areas
    weak_areas = await memory.get_weak_areas(student_id)
    
    # Get dimension history
    dimension_history = await memory.get_dimension_history(student_id)
    dimension_averages = {
        dim: sum(scores) / len(scores) if scores else 0
        for dim, scores in dimension_history.items()
    }
    
    # Get recent overall scores
    from app.models import Essay
    result = await db.execute(
        select(Essay)
        .where(Essay.student_id == student_id)
        .order_by(Essay.created_at.desc())
        .limit(10)
    )
    essays = result.scalars().all()
    score_trend = [e.overall_score for e in reversed(essays) if e.overall_score]
    
    return StudentHistory(
        student_id=student_id,
        total_essays=student.total_essays or 0,
        average_overall_score=student.average_score or 0,
        dimension_averages=dimension_averages,
        weak_areas=weak_areas,
        score_trend=score_trend,
        last_grading=essays[0].created_at if essays else None,
    )


@router.get("/{student_id}/weak-areas")
async def get_weak_areas(student_id: str):
    """Get student's weak areas with recommendations."""
    memory = LongTermMemory()
    weak_areas = await memory.get_weak_areas(student_id)
    
    return {
        "student_id": student_id,
        "weak_areas": [
            {
                "dimension": wa.dimension.value,
                "average_score": wa.average_score,
                "trend": wa.trend,
                "recommendation": wa.recommendation,
            }
            for wa in weak_areas
        ],
    }
