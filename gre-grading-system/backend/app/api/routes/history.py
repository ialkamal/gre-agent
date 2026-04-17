"""History API routes for viewing past essays and grading results."""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional
from app.db import get_db
from app.models import Essay, EssayDimensionScore, GradingResult


router = APIRouter(prefix="/history", tags=["history"])


@router.get("/essays/{student_id}")
async def get_student_essays(
    student_id: str,
    limit: int = Query(default=10, le=50),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get a student's essay history."""
    result = await db.execute(
        select(Essay)
        .where(Essay.student_id == student_id)
        .order_by(Essay.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    essays = result.scalars().all()
    
    return {
        "student_id": student_id,
        "essays": [
            {
                "id": e.id,
                "prompt": e.prompt[:200] + "..." if len(e.prompt) > 200 else e.prompt,
                "word_count": e.word_count,
                "overall_score": e.overall_score,
                "created_at": e.created_at,
            }
            for e in essays
        ],
        "total": len(essays),
        "limit": limit,
        "offset": offset,
    }


@router.get("/essay/{essay_id}")
async def get_essay_details(essay_id: str, db: AsyncSession = Depends(get_db)):
    """Get detailed information about a specific essay."""
    result = await db.execute(
        select(Essay)
        .where(Essay.id == essay_id)
        .options(
            selectinload(Essay.dimension_scores),
            selectinload(Essay.grading_results),
        )
    )
    essay = result.scalar_one_or_none()
    
    if not essay:
        raise HTTPException(status_code=404, detail="Essay not found")
    
    # Calculate total fact checks
    total_fact_checks = sum(gr.fact_checks_count or 0 for gr in essay.grading_results)
    
    return {
        "id": essay.id,
        "student_id": essay.student_id,
        "prompt": essay.prompt,
        "text": essay.text,
        "word_count": essay.word_count,
        "overall_score": essay.overall_score,
        "created_at": essay.created_at,
        "merged_feedback": essay.merged_feedback,
        "model_essay": essay.model_essay,
        "model_essay_notes": essay.model_essay_notes,
        "total_fact_checks": total_fact_checks,
        "dimension_scores": [
            {
                "dimension": ds.dimension,
                "score": ds.score,
                "feedback": ds.feedback,
                "strengths": ds.strengths,
                "improvements": ds.improvements,
                "variance": ds.score_variance,
            }
            for ds in essay.dimension_scores
        ],
        "grader_results": [
            {
                "grader_id": gr.grader_id,
                "overall_score": gr.overall_score,
                "overall_feedback": gr.overall_feedback,
                "grading_time_ms": gr.grading_time_ms,
                "temperature": gr.temperature,
                "fact_checks_count": gr.fact_checks_count or 0,
            }
            for gr in essay.grading_results
        ],
    }


@router.get("/compare/{student_id}")
async def compare_essays(
    student_id: str,
    essay_ids: str = Query(..., description="Comma-separated essay IDs to compare"),
    db: AsyncSession = Depends(get_db),
):
    """Compare multiple essays side-by-side."""
    ids = [id.strip() for id in essay_ids.split(",")]
    
    if len(ids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 essays to compare")
    if len(ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 essays for comparison")
    
    result = await db.execute(
        select(Essay)
        .where(Essay.id.in_(ids), Essay.student_id == student_id)
        .options(selectinload(Essay.dimension_scores))
        .order_by(Essay.created_at)
    )
    essays = result.scalars().all()
    
    if len(essays) != len(ids):
        raise HTTPException(status_code=404, detail="Some essays not found")
    
    # Build comparison data
    dimensions = ["thesis", "reasoning", "evidence", "structure", "analysis", "language", "grammar", "coherence"]
    
    comparison = {
        "student_id": student_id,
        "essays": [
            {
                "id": e.id,
                "created_at": e.created_at,
                "overall_score": e.overall_score,
                "dimension_scores": {
                    ds.dimension: ds.score
                    for ds in e.dimension_scores
                },
            }
            for e in essays
        ],
        "dimensions": dimensions,
        "improvement": {},
    }
    
    # Calculate improvement from first to last
    if len(essays) >= 2:
        first = essays[0]
        last = essays[-1]
        first_scores = {ds.dimension: ds.score for ds in first.dimension_scores}
        last_scores = {ds.dimension: ds.score for ds in last.dimension_scores}
        
        comparison["improvement"] = {
            dim: round(last_scores.get(dim, 0) - first_scores.get(dim, 0), 1)
            for dim in dimensions
        }
        comparison["overall_improvement"] = round(
            (last.overall_score or 0) - (first.overall_score or 0), 1
        )
    
    return comparison


@router.get("/progress/{student_id}")
async def get_progress_chart_data(
    student_id: str,
    dimension: Optional[str] = Query(default=None, description="Filter by dimension"),
    db: AsyncSession = Depends(get_db),
):
    """Get data for progress charts."""
    result = await db.execute(
        select(Essay)
        .where(Essay.student_id == student_id)
        .options(selectinload(Essay.dimension_scores))
        .order_by(Essay.created_at)
        .limit(20)  # Last 20 essays
    )
    essays = result.scalars().all()
    
    if not essays:
        return {"student_id": student_id, "data": [], "message": "No essays found"}
    
    # Build time series data
    data_points = []
    for essay in essays:
        point = {
            "essay_id": essay.id,
            "date": essay.created_at.isoformat(),
            "overall_score": essay.overall_score,
        }
        
        for ds in essay.dimension_scores:
            if dimension is None or ds.dimension == dimension:
                point[ds.dimension] = ds.score
        
        data_points.append(point)
    
    return {
        "student_id": student_id,
        "total_essays": len(essays),
        "data": data_points,
        "available_dimensions": list(set(
            ds.dimension for e in essays for ds in e.dimension_scores
        )),
    }
