"""Depth of Analysis Agent."""
from app.agents.base import BaseGradingAgent
from app.schemas import GradingDimension


class AnalysisAgent(BaseGradingAgent):
    """Evaluates depth and sophistication of analysis."""
    
    def __init__(self, temperature: float = 0.3, model: str = None):
        super().__init__(
            dimension=GradingDimension.ANALYSIS,
            temperature=temperature,
            model=model,
        )
    
    @property
    def dimension_name(self) -> str:
        return "Depth of Analysis"
    
    @property
    def evaluation_criteria(self) -> str:
        return """
## Evaluation Criteria for Depth of Analysis

Evaluate the sophistication and depth of the analysis:

**Score 6 (Outstanding)**
- Insightful analysis that probes the issue deeply
- Considers multiple perspectives and nuances
- Addresses complexities and exceptions
- Goes beyond surface-level examination
- Demonstrates sophisticated thinking
- Makes meaningful connections

**Score 5 (Strong)**
- Thoughtful analysis with good depth
- Considers the issue from multiple angles
- Addresses some complexities
- Shows analytical thinking
- Makes relevant connections
- Goes beyond obvious points

**Score 4 (Adequate)**
- Adequate analysis of the issue
- Some consideration of different perspectives
- May touch on complexities
- Reasonable analytical effort
- Some connections made
- Mostly surface-level but competent

**Score 3 (Limited)**
- Limited analysis of the issue
- Mainly one-sided perspective
- Does not address complexities
- Superficial examination
- Few connections made
- Lacks depth

**Score 2 (Seriously Flawed)**
- Very shallow or no real analysis
- Does not engage meaningfully with issue
- No consideration of perspectives
- Assertions without analysis
- No depth evident

**Score 1 (Fundamentally Deficient)**
- No analysis present
- Does not engage with the issue
- No meaningful content

## What to Look For
- Does the writer go beyond restating the prompt?
- Are multiple perspectives considered?
- Does the analysis address nuances and exceptions?
- Are ideas developed in depth?
- Does the writer show original thinking?
- Are connections made between ideas?
"""
