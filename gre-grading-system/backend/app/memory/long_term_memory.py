"""Long-term memory using PostgreSQL with pgvector for student history and weak area tracking."""
from typing import Optional
from datetime import datetime
import statistics
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app.models import Student, Essay, EssayDimensionScore, DimensionHistory, GradingResult
from app.schemas import WeakArea, GradingDimension, ConsensusResult, GraderResult, DimensionScore
from app.config import get_settings


settings = get_settings()


class LongTermMemory:
    """
    Manages long-term memory stored in PostgreSQL.
    
    Responsibilities:
    - Store essay submissions and grading results
    - Track dimension scores over time
    - Identify weak areas based on historical performance
    - Calculate improvement trends
    """
    
    async def get_or_create_student(self, student_id: str, email: str = None, name: str = None) -> Student:
        """Get existing student or create a new one."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Student).where(Student.id == student_id)
            )
            student = result.scalar_one_or_none()
            
            if not student:
                student = Student(
                    id=student_id,
                    email=email or f"{student_id}@example.com",
                    name=name or f"Student {student_id}",
                )
                session.add(student)
                await session.commit()
                await session.refresh(student)
            
            return student
    
    async def get_weak_areas(self, student_id: str) -> list[WeakArea]:
        """
        Get student's weak areas based on historical performance.
        
        A dimension is considered "weak" if:
        - Average score over last N essays < threshold (default: 4.0)
        - Trend is not improving
        """
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(DimensionHistory).where(
                    DimensionHistory.student_id == student_id
                )
            )
            histories = result.scalars().all()
            
            weak_areas = []
            for hist in histories:
                if hist.average_score < settings.weak_area_threshold:
                    weak_areas.append(WeakArea(
                        dimension=GradingDimension(hist.dimension),
                        average_score=hist.average_score,
                        trend=hist.trend,
                        recommendation=self._generate_recommendation(
                            hist.dimension, hist.average_score, hist.trend
                        ),
                    ))
            
            # Sort by severity (lowest score first)
            weak_areas.sort(key=lambda x: x.average_score)
            
            return weak_areas
    
    async def get_dimension_history(self, student_id: str) -> dict[str, list[float]]:
        """Get historical scores per dimension for a student."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(DimensionHistory).where(
                    DimensionHistory.student_id == student_id
                )
            )
            histories = result.scalars().all()
            
            return {
                hist.dimension: hist.recent_scores
                for hist in histories
            }
    
    async def store_grading_result(
        self,
        student_id: str,
        essay_prompt: str,
        essay_text: str,
        consensus: ConsensusResult,
        grader_results: list[GraderResult],
        model_essay: Optional[str] = None,
        model_essay_notes: Optional[str] = None,
    ) -> str:
        """Store a complete grading result."""
        # Ensure student exists first
        await self.get_or_create_student(student_id)
        
        async with AsyncSessionLocal() as session:
            # Create essay record
            essay = Essay(
                student_id=student_id,
                prompt=essay_prompt,
                text=essay_text,
                word_count=len(essay_text.split()),
                overall_score=consensus.overall_score,
                merged_feedback=consensus.merged_feedback,
                model_essay=model_essay,
                model_essay_notes=model_essay_notes,
            )
            session.add(essay)
            await session.flush()  # Get essay ID
            
            # Store individual grader results
            for gr in grader_results:
                grading_result = GradingResult(
                    essay_id=essay.id,
                    grader_id=gr.grader_id,
                    dimension_scores={
                        ds.dimension.value: {
                            "score": ds.score,
                            "feedback": ds.feedback,
                        }
                        for ds in gr.dimension_scores
                    },
                    overall_score=gr.overall_score,
                    overall_feedback=gr.overall_feedback,
                    fact_checks_count=gr.fact_checks_count or 0,
                    grading_time_ms=gr.grading_time_ms,
                    temperature=settings.grader_temperatures[gr.grader_id],
                    model_used=settings.openai_model,
                )
                session.add(grading_result)
            
            # Store consensus dimension scores
            for ds in consensus.dimension_scores:
                dim_score = EssayDimensionScore(
                    essay_id=essay.id,
                    dimension=ds.dimension.value,
                    score=ds.score,
                    feedback=ds.feedback,
                    strengths=ds.strengths,
                    improvements=ds.improvements,
                    score_variance=consensus.score_variance.get(ds.dimension.value, 0),
                )
                session.add(dim_score)
            
            # Update student stats
            result = await session.execute(
                select(Student).where(Student.id == student_id)
            )
            student = result.scalar_one_or_none()
            if student:
                student.total_essays = (student.total_essays or 0) + 1
                # Update running average
                if student.average_score:
                    student.average_score = (
                        (student.average_score * (student.total_essays - 1) + consensus.overall_score)
                        / student.total_essays
                    )
                else:
                    student.average_score = consensus.overall_score
            
            await session.commit()
            return essay.id
    
    async def update_dimension_history(
        self,
        student_id: str,
        dimension_scores: list[DimensionScore],
    ) -> None:
        """Update dimension history with new scores."""
        async with AsyncSessionLocal() as session:
            for ds in dimension_scores:
                # Get or create dimension history
                result = await session.execute(
                    select(DimensionHistory).where(
                        DimensionHistory.student_id == student_id,
                        DimensionHistory.dimension == ds.dimension.value,
                    )
                )
                hist = result.scalar_one_or_none()
                
                if not hist:
                    hist = DimensionHistory(
                        student_id=student_id,
                        dimension=ds.dimension.value,
                        total_essays=0,
                        average_score=0.0,
                        recent_scores=[],
                    )
                    session.add(hist)
                
                # Update with new score
                hist.total_essays += 1
                hist.recent_scores = (hist.recent_scores or [])[-settings.weak_area_lookback:] + [ds.score]
                hist.average_score = statistics.mean(hist.recent_scores)
                
                # Calculate trend
                hist.trend = self._calculate_trend(hist.recent_scores)
            
            await session.commit()
    
    async def get_improvement_from_last(
        self,
        student_id: str,
        current_scores: list[DimensionScore],
    ) -> Optional[dict[str, float]]:
        """Calculate improvement from the last essay."""
        async with AsyncSessionLocal() as session:
            # Get the student's most recent essay (before current)
            result = await session.execute(
                select(Essay)
                .where(Essay.student_id == student_id)
                .order_by(Essay.created_at.desc())
                .limit(2)
            )
            essays = result.scalars().all()
            
            if len(essays) < 2:
                return None
            
            previous_essay = essays[1]  # Second most recent
            
            # Get previous dimension scores
            result = await session.execute(
                select(EssayDimensionScore)
                .where(EssayDimensionScore.essay_id == previous_essay.id)
            )
            prev_scores = {s.dimension: s.score for s in result.scalars().all()}
            
            # Calculate differences
            improvements = {}
            for ds in current_scores:
                prev_score = prev_scores.get(ds.dimension.value)
                if prev_score is not None:
                    improvements[ds.dimension.value] = round(ds.score - prev_score, 1)
            
            return improvements
    
    def _calculate_trend(self, scores: list[float]) -> str:
        """Calculate trend from a list of scores."""
        if len(scores) < 2:
            return "stable"
        
        # Simple trend: compare first half average to second half
        mid = len(scores) // 2
        first_half = statistics.mean(scores[:mid]) if mid > 0 else scores[0]
        second_half = statistics.mean(scores[mid:])
        
        diff = second_half - first_half
        
        if diff > 0.3:
            return "improving"
        elif diff < -0.3:
            return "declining"
        else:
            return "stable"
    
    def _generate_recommendation(
        self, dimension: str, score: float, trend: str
    ) -> str:
        """Generate a personalized recommendation for a weak area."""
        recommendations = {
            "thesis": "Focus on clearly stating your position in the opening paragraph. Practice writing thesis statements that directly address the prompt.",
            "reasoning": "Work on developing logical arguments with clear cause-and-effect relationships. Practice identifying and addressing counterarguments.",
            "evidence": "Collect a bank of versatile examples from history, current events, and literature. Practice integrating evidence smoothly into your arguments.",
            "structure": "Use a clear essay template: introduction, 2-3 body paragraphs, conclusion. Practice using transition words between paragraphs.",
            "analysis": "Push beyond surface-level observations. Ask 'why?' and 'what are the implications?' for each point you make.",
            "language": "Read high-scoring sample essays to absorb sophisticated vocabulary and sentence structures. Practice varying your sentence length.",
            "grammar": "Review common grammar rules. Proofread your essays specifically for your most common errors.",
            "coherence": "Ensure each paragraph connects to your thesis. Read your essay aloud to check flow and persuasiveness.",
        }
        
        base_rec = recommendations.get(dimension, "Focus on improving this area with targeted practice.")
        
        if trend == "declining":
            return f"[URGENT] {base_rec} This area has been declining - give it extra attention."
        elif trend == "improving":
            return f"{base_rec} You're making progress here - keep it up!"
        else:
            return base_rec
    
    async def update_essay_model(
        self,
        essay_id: str,
        model_essay: str,
        model_essay_notes: str,
    ) -> None:
        """Update an essay with model essay data."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Essay).where(Essay.id == essay_id)
            )
            essay = result.scalar_one_or_none()
            
            if essay:
                essay.model_essay = model_essay
                essay.model_essay_notes = model_essay_notes
                await session.commit()
