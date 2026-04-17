"""Thesis/Clarity of Position Agent."""
from app.agents.base import BaseGradingAgent
from app.schemas import GradingDimension


class ThesisAgent(BaseGradingAgent):
    """Evaluates clarity and strength of the thesis/position."""
    
    def __init__(self, temperature: float = 0.3, model: str = None):
        super().__init__(
            dimension=GradingDimension.THESIS,
            temperature=temperature,
            model=model,
        )
    
    @property
    def dimension_name(self) -> str:
        return "Clarity of Position (Thesis)"
    
    @property
    def evaluation_criteria(self) -> str:
        return """
## Evaluation Criteria for Thesis/Position

Evaluate how clearly and effectively the writer establishes their position:

**Score 6 (Outstanding)**
- States a clear, specific, and insightful thesis
- Position is sophisticated and shows nuanced understanding
- Thesis directly addresses the prompt's complexities
- Position is maintained consistently throughout

**Score 5 (Strong)**
- Presents a clear, well-considered position
- Thesis is specific and addresses the prompt effectively
- Position shows thoughtful engagement with the issue
- Maintains focus throughout

**Score 4 (Adequate)**
- States a clear position on the issue
- Thesis addresses the prompt appropriately
- Position may be somewhat predictable but is clear
- Generally maintains position

**Score 3 (Limited)**
- Position is present but may be vague or unclear
- Thesis may not fully address the prompt
- Position may shift or be inconsistent
- Limited insight into the issue

**Score 2 (Seriously Flawed)**
- Position is unclear or contradictory
- Thesis may be missing or very weak
- Does not effectively engage with the prompt
- Difficult to identify writer's stance

**Score 1 (Fundamentally Deficient)**
- No clear position identifiable
- Does not address the issue
- No thesis present

## What to Look For
- Is there a clear thesis statement?
- Does the position address the specific prompt?
- Is the position maintained throughout?
- Does the thesis show insight or just restate the prompt?
- How specific vs. vague is the position?
"""
