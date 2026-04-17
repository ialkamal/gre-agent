"""Model Essay Generator - Creates an improved version of the essay scoring 6 across all dimensions."""
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import get_settings
from app.schemas import ConsensusResult, DimensionScore
import asyncio


settings = get_settings()


async def retry_with_backoff(func, max_retries=5, base_delay=1.0):
    """Retry with exponential backoff for rate limits."""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
            else:
                raise


class ModelEssayGenerator:
    """
    Generates a model essay that would score 6 across all dimensions.
    
    Uses the original essay structure and ideas but rewrites to demonstrate
    excellent execution in all 8 grading dimensions.
    """
    
    def __init__(self, model: Optional[str] = None):
        self.model_name = model or settings.openai_model
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=self.model_name,
            temperature=0.4,  # Slightly creative but consistent
        )
    
    async def generate_model_essay(
        self,
        essay_prompt: str,
        original_essay: str,
        consensus: ConsensusResult,
    ) -> dict:
        """
        Generate a model essay based on the original, addressing all weaknesses.
        
        Returns:
            dict with 'model_essay' and 'improvement_notes'
        """
        # Extract weak dimensions for focused improvement
        weak_dimensions = [
            ds for ds in consensus.dimension_scores 
            if ds.score < 5.0
        ]
        
        weak_areas_text = "\n".join([
            f"- {ds.dimension.value.title()} (scored {ds.score}): {ds.improvements[0] if ds.improvements else 'Needs improvement'}"
            for ds in weak_dimensions
        ]) if weak_dimensions else "Minor refinements needed across all areas."
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert GRE writing tutor who creates model essays that score 6 (Outstanding) across all dimensions.

Your task is to rewrite the student's essay to demonstrate excellence in ALL 8 dimensions:

1. THESIS (Score 6): Present an insightful, nuanced position that directly addresses the prompt. The thesis should be debatable and sophisticated.

2. REASONING (Score 6): Develop compelling logical arguments with clear cause-and-effect. Address counterarguments thoughtfully.

3. EVIDENCE (Score 6): Use specific, persuasive examples from diverse sources (history, science, literature, current events). Integrate evidence smoothly.

4. STRUCTURE (Score 6): Organize with a compelling introduction, well-developed body paragraphs with clear topic sentences, smooth transitions, and a powerful conclusion.

5. ANALYSIS (Score 6): Demonstrate deep, sophisticated analysis. Explore multiple perspectives and implications. Show nuanced thinking.

6. LANGUAGE (Score 6): Use sophisticated vocabulary precisely. Vary sentence structure elegantly. Maintain an engaging, academic tone.

7. GRAMMAR (Score 6): Write with flawless grammar, punctuation, and mechanics. Every sentence should be polished.

8. COHERENCE (Score 6): Ensure all elements work together seamlessly. The essay should flow naturally and be highly persuasive.

IMPORTANT GUIDELINES:
- Keep the student's core argument and position
- Maintain approximately the same length (within 100 words)
- Preserve good elements from the original
- Demonstrate HOW to execute each dimension excellently
- Make the improvements feel natural, not artificial

FORMATTING RULES (CRITICAL):
- Do NOT use ** or any markdown bold/italic formatting
- Do NOT use asterisks for emphasis
- Use plain text only
- For the improvement notes section, use numbered lists like "1. Thesis:" not "1. **Thesis**:" """),
            ("human", """ESSAY PROMPT:
{prompt}

ORIGINAL STUDENT ESSAY:
{original_essay}

AREAS THAT NEED IMPROVEMENT:
{weak_areas}

Please rewrite this essay to score 6 across all dimensions. After the essay, provide brief notes explaining the key improvements made for each dimension. Remember: NO markdown formatting, use plain text with numbered sections like "1. Thesis:" not "1. **Thesis**:" """),
        ])
        
        chain = prompt | self.llm
        
        async def invoke():
            return await chain.ainvoke({
                "prompt": essay_prompt,
                "original_essay": original_essay,
                "weak_areas": weak_areas_text,
            })
        
        result = await retry_with_backoff(invoke)
        
        # Parse response - split essay from notes
        content = result.content
        
        # Try to find the notes section
        notes_markers = ["Key Improvements:", "Improvement Notes:", "Notes:", "Changes Made:"]
        essay_text = content
        improvement_notes = ""
        
        for marker in notes_markers:
            if marker in content:
                parts = content.split(marker, 1)
                essay_text = parts[0].strip()
                improvement_notes = marker + parts[1].strip()
                break
        
        # If no marker found, check for a clear paragraph break pattern
        if not improvement_notes:
            # Look for double newline followed by numbered list or bullets
            import re
            match = re.search(r'\n\n((?:\d\.|[-•])\s*\w)', content)
            if match:
                split_pos = match.start()
                essay_text = content[:split_pos].strip()
                improvement_notes = content[split_pos:].strip()
        
        # Remove any markdown ** formatting that slipped through
        essay_text = essay_text.replace("**", "")
        improvement_notes = improvement_notes.replace("**", "")
        
        return {
            "model_essay": essay_text,
            "improvement_notes": improvement_notes,
            "word_count": len(essay_text.split()),
        }
    
    async def generate_dimension_examples(
        self,
        essay_prompt: str,
        original_essay: str,
        dimension_scores: list[DimensionScore],
    ) -> dict[str, str]:
        """
        Generate specific rewritten examples for weak dimensions only.
        
        Returns dict mapping dimension name to improved example paragraph.
        """
        weak_dims = [ds for ds in dimension_scores if ds.score < 4.5]
        
        if not weak_dims:
            return {}
        
        examples = {}
        
        for ds in weak_dims[:3]:  # Limit to 3 weakest
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"""You are a GRE writing expert. Generate a brief example showing how to improve the {ds.dimension.value.title()} dimension from the student's essay.

Show a "Before" excerpt and an "After" improved version.
Keep it concise - one paragraph comparison.
Focus specifically on {ds.dimension.value.title()} improvements."""),
                ("human", """Essay prompt: {prompt}

Original essay excerpt (focus on {dimension} weaknesses):
{original_essay}

Current feedback: {feedback}

Generate a Before/After example showing how to improve {dimension}."""),
            ])
            
            chain = prompt | self.llm
            
            async def invoke():
                return await chain.ainvoke({
                    "prompt": essay_prompt,
                    "original_essay": original_essay[:1000],  # First part
                    "dimension": ds.dimension.value.title(),
                    "feedback": ds.feedback,
                })
            
            try:
                result = await retry_with_backoff(invoke)
                examples[ds.dimension.value] = result.content
            except Exception:
                continue
        
        return examples
