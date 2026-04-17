"""Grader - Orchestrates 8 grading agents for a single grading pass."""
import asyncio
import time
from typing import Optional
from app.agents.grading_agents import (
    ThesisAgent,
    ReasoningAgent,
    EvidenceAgent,
    StructureAgent,
    AnalysisAgent,
    LanguageAgent,
    GrammarAgent,
    CoherenceAgent,
)
from app.agents.base import AgentScore
from app.schemas import DimensionScore, GraderResult, GradingDimension


class Grader:
    """
    A single grader that runs all 8 dimension agents.
    
    Each grader uses the same prompts but can have different temperatures
    to introduce diversity in grading perspectives.
    """
    
    def __init__(
        self,
        grader_id: int,
        temperature: float = 0.3,
        model: Optional[str] = None,
    ):
        self.grader_id = grader_id
        self.temperature = temperature
        self.model = model
        self.fact_checks_count = 0
        
        # Initialize all 8 agents
        self.agents = {
            GradingDimension.THESIS: ThesisAgent(temperature=temperature, model=model),
            GradingDimension.REASONING: ReasoningAgent(temperature=temperature, model=model),
            GradingDimension.EVIDENCE: EvidenceAgent(temperature=temperature, model=model),
            GradingDimension.STRUCTURE: StructureAgent(temperature=temperature, model=model),
            GradingDimension.ANALYSIS: AnalysisAgent(temperature=temperature, model=model),
            GradingDimension.LANGUAGE: LanguageAgent(temperature=temperature, model=model),
            GradingDimension.GRAMMAR: GrammarAgent(temperature=temperature, model=model),
            GradingDimension.COHERENCE: CoherenceAgent(temperature=temperature, model=model),
        }
    
    async def grade(
        self,
        prompt: str,
        essay: str,
        weak_areas: Optional[list[str]] = None,
        session_context: Optional[str] = None,
    ) -> GraderResult:
        """
        Run all 8 agents to grade the essay.
        
        Agents run in parallel for efficiency.
        """
        start_time = time.time()
        self.fact_checks_count = 0
        
        # Run all agents in parallel
        tasks = [
            self._evaluate_dimension(dimension, agent, prompt, essay, weak_areas, session_context)
            for dimension, agent in self.agents.items()
        ]
        
        results = await asyncio.gather(*tasks)
        dimension_scores = [r for r in results if r is not None]
        
        # Calculate overall score (weighted average)
        overall_score = self._calculate_overall_score(dimension_scores)
        overall_feedback = self._generate_overall_feedback(dimension_scores)
        
        grading_time_ms = int((time.time() - start_time) * 1000)
        
        return GraderResult(
            grader_id=self.grader_id,
            dimension_scores=dimension_scores,
            overall_score=overall_score,
            overall_feedback=overall_feedback,
            grading_time_ms=grading_time_ms,
            fact_checks_count=self.fact_checks_count,
        )
    
    async def _evaluate_dimension(
        self,
        dimension: GradingDimension,
        agent,
        prompt: str,
        essay: str,
        weak_areas: Optional[list[str]],
        session_context: Optional[str],
    ) -> Optional[DimensionScore]:
        """Evaluate a single dimension."""
        try:
            # Evidence agent returns tuple (score, fact_check_count)
            if dimension == GradingDimension.EVIDENCE:
                result, fact_count = await agent.evaluate(
                    prompt=prompt,
                    essay=essay,
                    weak_areas=weak_areas,
                    session_context=session_context,
                )
                self.fact_checks_count += fact_count
            else:
                result: AgentScore = await agent.evaluate(
                    prompt=prompt,
                    essay=essay,
                    weak_areas=weak_areas,
                    session_context=session_context,
                )
            
            return DimensionScore(
                dimension=dimension,
                score=self._round_to_half(result.score),
                feedback=result.feedback,
                strengths=result.strengths,
                improvements=result.improvements,
            )
        except Exception as e:
            # Log error but don't fail the entire grading
            print(f"Error in {dimension} evaluation: {e}")
            return DimensionScore(
                dimension=dimension,
                score=3.0,  # Default to middle score on error
                feedback=f"Evaluation error: {str(e)}",
                strengths=[],
                improvements=["Unable to fully evaluate this dimension"],
            )
    
    def _round_to_half(self, score: float) -> float:
        """Round score to nearest 0.5 (GRE uses 0-6 in 0.5 increments)."""
        return round(score * 2) / 2
    
    def _calculate_overall_score(self, dimension_scores: list[DimensionScore]) -> float:
        """Calculate weighted overall score from dimension scores."""
        # GRE weights certain dimensions more heavily
        weights = {
            GradingDimension.THESIS: 1.2,
            GradingDimension.REASONING: 1.3,
            GradingDimension.EVIDENCE: 1.1,
            GradingDimension.STRUCTURE: 1.0,
            GradingDimension.ANALYSIS: 1.2,
            GradingDimension.LANGUAGE: 1.0,
            GradingDimension.GRAMMAR: 0.8,
            GradingDimension.COHERENCE: 1.1,
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for ds in dimension_scores:
            weight = weights.get(ds.dimension, 1.0)
            weighted_sum += ds.score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return self._round_to_half(weighted_sum / total_weight)
    
    def _generate_overall_feedback(self, dimension_scores: list[DimensionScore]) -> str:
        """Generate overall feedback summarizing the evaluation."""
        # Find strongest and weakest dimensions
        sorted_scores = sorted(dimension_scores, key=lambda x: x.score, reverse=True)
        strongest = sorted_scores[:2]
        weakest = sorted_scores[-2:]
        
        feedback_parts = []
        
        # Strengths (no ** markdown)
        feedback_parts.append("Strengths:")
        for ds in strongest:
            if ds.strengths:
                feedback_parts.append(f"- {ds.dimension.value.title()}: {ds.strengths[0]}")
        
        # Areas for improvement (no ** markdown)
        feedback_parts.append("\nPriority Areas for Improvement:")
        for ds in weakest:
            if ds.improvements:
                feedback_parts.append(f"- {ds.dimension.value.title()}: {ds.improvements[0]}")
        
        return "\n".join(feedback_parts)
