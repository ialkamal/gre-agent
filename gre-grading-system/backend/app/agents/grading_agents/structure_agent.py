"""Organization and Structure Agent."""
from app.agents.base import BaseGradingAgent
from app.schemas import GradingDimension


class StructureAgent(BaseGradingAgent):
    """Evaluates essay organization and structure."""
    
    def __init__(self, temperature: float = 0.3, model: str = None):
        super().__init__(
            dimension=GradingDimension.STRUCTURE,
            temperature=temperature,
            model=model,
        )
    
    @property
    def dimension_name(self) -> str:
        return "Organization and Structure"
    
    @property
    def evaluation_criteria(self) -> str:
        return """
## Evaluation Criteria for Organization and Structure

Evaluate how well the essay is organized and structured:

**Score 6 (Outstanding)**
- Sustains a well-focused, well-organized analysis
- Clear introduction, body, and conclusion
- Excellent use of transitions between paragraphs
- Logical flow from one idea to the next
- Paragraphs are well-developed and unified
- Structure enhances the argument

**Score 5 (Strong)**
- Is focused and generally well organized
- Clear structural elements present
- Good use of transitions
- Logical progression of ideas
- Paragraphs are focused and developed
- Structure supports the argument

**Score 4 (Adequate)**
- Is adequately organized
- Has recognizable structural elements
- Uses some transitions
- Generally logical flow
- Paragraphs are reasonably focused
- Structure is functional

**Score 3 (Limited)**
- Organization is weak or inconsistent
- Structural elements may be unclear
- Limited or awkward transitions
- Flow may be disjointed
- Paragraphs may be unfocused
- Structure does not enhance argument

**Score 2 (Seriously Flawed)**
- Little organization evident
- No clear structure
- Few or no transitions
- Ideas are scattered
- Paragraphs are undeveloped
- Difficult to follow

**Score 1 (Fundamentally Deficient)**
- No discernible organization
- No structure present
- Incomprehensible arrangement

## What to Look For
- Is there a clear introduction with thesis?
- Are body paragraphs focused on single topics?
- Are transitions used between paragraphs?
- Is there a logical flow of ideas?
- Does the conclusion effectively wrap up?
- Do paragraph breaks make sense?
"""
