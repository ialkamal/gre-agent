"""Consensus Agent - Combines results from multiple graders."""
import asyncio
import statistics
from typing import Optional
from app.schemas import (
    GraderResult,
    ConsensusResult,
    DimensionScore,
    GradingDimension,
    WeakArea,
)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import get_settings
from openai import RateLimitError


async def retry_with_backoff(func, max_retries=5, base_delay=1.0):
    """Retry an async function with exponential backoff for rate limits."""
    for attempt in range(max_retries):
        try:
            return await func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            print(f"Rate limit hit, waiting {delay}s before retry {attempt + 1}/{max_retries}")
            await asyncio.sleep(delay)
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                print(f"Rate limit hit, waiting {delay}s before retry {attempt + 1}/{max_retries}")
                await asyncio.sleep(delay)
            else:
                raise


class ConsensusAgent:
    """
    Combines results from multiple graders to reach consensus.
    
    Responsibilities:
    1. Average scores across graders
    2. Identify high-variance dimensions (disagreement)
    3. Merge and deduplicate feedback
    4. Prioritize improvements based on weak areas
    """
    
    def __init__(self, model: Optional[str] = None):
        self.settings = get_settings()
        self.model_name = model or self.settings.openai_model
        self.llm = ChatOpenAI(
            api_key=self.settings.openai_api_key,
            model=self.model_name,
            temperature=0.2,  # Lower temperature for consistency
        )
    
    async def build_consensus(
        self,
        grader_results: list[GraderResult],
        weak_areas: Optional[list[WeakArea]] = None,
    ) -> ConsensusResult:
        """Build consensus from multiple grader results."""
        
        # Step 1: Average scores per dimension
        dimension_scores = self._average_dimension_scores(grader_results)
        
        # Step 2: Calculate variance per dimension
        score_variance = self._calculate_variance(grader_results)
        
        # Step 3: Identify high-variance dimensions
        high_variance = [
            GradingDimension(dim) for dim, var in score_variance.items()
            if var > 1.5  # Threshold for "high variance"
        ]
        
        # Step 4: Calculate overall score
        overall_score = self._calculate_overall_score(dimension_scores)
        
        # Step 5: Merge feedback using LLM
        merged_feedback = await self._merge_feedback(grader_results, dimension_scores)
        
        # Step 6: Extract strengths and improvements
        strengths = self._extract_strengths(dimension_scores)
        improvements = self._prioritize_improvements(dimension_scores, weak_areas)
        
        return ConsensusResult(
            dimension_scores=dimension_scores,
            overall_score=overall_score,
            score_variance=score_variance,
            high_variance_dimensions=high_variance,
            merged_feedback=merged_feedback,
            strengths=strengths,
            priority_improvements=improvements,
        )
    
    def _average_dimension_scores(
        self, grader_results: list[GraderResult]
    ) -> list[DimensionScore]:
        """Average scores across graders for each dimension."""
        dimension_scores_map: dict[GradingDimension, list[DimensionScore]] = {}
        
        for result in grader_results:
            for ds in result.dimension_scores:
                if ds.dimension not in dimension_scores_map:
                    dimension_scores_map[ds.dimension] = []
                dimension_scores_map[ds.dimension].append(ds)
        
        averaged = []
        for dimension, scores in dimension_scores_map.items():
            avg_score = self._round_to_half(statistics.mean([s.score for s in scores]))
            
            # Combine feedback from all graders
            all_feedback = [s.feedback for s in scores]
            all_strengths = list(set(s for ds in scores for s in ds.strengths))
            all_improvements = list(set(i for ds in scores for i in ds.improvements))
            
            averaged.append(DimensionScore(
                dimension=dimension,
                score=avg_score,
                feedback=all_feedback[0],  # Primary feedback (will be merged later)
                strengths=all_strengths[:3],  # Top 3 strengths
                improvements=all_improvements[:3],  # Top 3 improvements
            ))
        
        return averaged
    
    def _calculate_variance(
        self, grader_results: list[GraderResult]
    ) -> dict[str, float]:
        """Calculate score variance per dimension."""
        dimension_scores_map: dict[str, list[float]] = {}
        
        for result in grader_results:
            for ds in result.dimension_scores:
                key = ds.dimension.value
                if key not in dimension_scores_map:
                    dimension_scores_map[key] = []
                dimension_scores_map[key].append(ds.score)
        
        variance = {}
        for dimension, scores in dimension_scores_map.items():
            if len(scores) > 1:
                variance[dimension] = round(statistics.variance(scores), 2)
            else:
                variance[dimension] = 0.0
        
        return variance
    
    def _round_to_half(self, score: float) -> float:
        """Round score to nearest 0.5 (GRE uses 0-6 in 0.5 increments)."""
        return round(score * 2) / 2
    
    def _calculate_overall_score(self, dimension_scores: list[DimensionScore]) -> float:
        """Calculate overall score from averaged dimension scores."""
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
        
        return self._round_to_half(weighted_sum / total_weight)
    
    async def _merge_feedback(
        self,
        grader_results: list[GraderResult],
        dimension_scores: list[DimensionScore],
    ) -> str:
        """Use LLM to merge and synthesize feedback from all graders."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a GRE writing expert tasked with synthesizing feedback from multiple graders.

Your job is to:
1. Combine insights from all graders into coherent feedback
2. Remove redundant points
3. Organize feedback by priority
4. Keep the tone constructive and encouraging
5. Be specific with actionable advice AND include brief examples

IMPORTANT FORMATTING RULES:
- Do NOT use ** or any markdown bold/italic formatting
- Use plain text headers like "Key Strengths:" followed by a newline
- Use simple bullet points with - 
- Keep formatting clean and readable
- For EACH improvement, use the EXACT format below for before/after examples

Output format:
Start with overall impression (2-3 sentences)

Key Strengths:
- strength 1
- strength 2

Priority Areas for Improvement:

[IMPROVEMENT]
Area: Language & Style
Tip: Vary your sentence structure to create more engaging prose.
[BEFORE]
Technology is helpful. Technology saves time. Technology makes life easier.
[AFTER]
While technology proves helpful in many contexts, its greatest value lies in the time it saves, ultimately making daily life more manageable.
[/IMPROVEMENT]

[IMPROVEMENT]
Area: Reasoning
Tip: Strengthen your logical connections with explicit cause-and-effect language.
[BEFORE]
Social media affects mental health. Many teenagers feel anxious.
[AFTER]
The constant comparison fostered by social media directly contributes to anxiety among teenagers, as they measure their lives against curated highlight reels.
[/IMPROVEMENT]

Next Steps:
1. First actionable step
2. Second actionable step
3. Third actionable step
"""),
            ("human", """Here are the evaluation results from {num_graders} independent graders:

{grader_feedback}

Dimension Scores (averaged):
{dimension_summary}

Please synthesize this into unified, constructive feedback for the student. Use the [IMPROVEMENT][BEFORE][AFTER][/IMPROVEMENT] format for each improvement suggestion."""),
        ])
        
        # Prepare grader feedback
        grader_feedback = ""
        for i, result in enumerate(grader_results):
            grader_feedback += f"\n--- Grader {i+1} (Score: {result.overall_score}) ---\n"
            grader_feedback += result.overall_feedback + "\n"
        
        # Prepare dimension summary
        dimension_summary = "\n".join([
            f"- {ds.dimension.value.title()}: {ds.score}/6"
            for ds in sorted(dimension_scores, key=lambda x: x.score, reverse=True)
        ])
        
        chain = prompt | self.llm
        
        async def invoke_chain():
            return await chain.ainvoke({
                "num_graders": len(grader_results),
                "grader_feedback": grader_feedback,
                "dimension_summary": dimension_summary,
            })
        
        result = await retry_with_backoff(invoke_chain)
        
        return result.content
    
    def _extract_strengths(self, dimension_scores: list[DimensionScore]) -> list[str]:
        """Extract top strengths from high-scoring dimensions."""
        strengths = []
        
        # Sort by score descending
        sorted_dims = sorted(dimension_scores, key=lambda x: x.score, reverse=True)
        
        for ds in sorted_dims[:3]:  # Top 3 dimensions
            if ds.score >= 4 and ds.strengths:
                strengths.append(f"{ds.dimension.value.title()}: {ds.strengths[0]}")
        
        return strengths
    
    def _prioritize_improvements(
        self,
        dimension_scores: list[DimensionScore],
        weak_areas: Optional[list[WeakArea]] = None,
    ) -> list[str]:
        """Prioritize improvements based on scores and historical weak areas."""
        improvements = []
        
        # Sort by score ascending (lowest first)
        sorted_dims = sorted(dimension_scores, key=lambda x: x.score)
        
        # Get weak area dimensions
        weak_dimensions = set()
        if weak_areas:
            weak_dimensions = {wa.dimension for wa in weak_areas}
        
        # Prioritize: weak areas that are still weak
        for ds in sorted_dims:
            if ds.dimension in weak_dimensions and ds.improvements:
                improvements.append(
                    f"[PRIORITY] {ds.dimension.value.title()}: {ds.improvements[0]}"
                )
        
        # Then add other low-scoring dimensions
        for ds in sorted_dims:
            if ds.dimension not in weak_dimensions and ds.score < 4 and ds.improvements:
                improvements.append(f"{ds.dimension.value.title()}: {ds.improvements[0]}")
        
        return improvements[:5]  # Top 5 improvements
