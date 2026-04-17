"""Quality of Reasoning Agent."""
from app.agents.base import BaseGradingAgent
from app.schemas import GradingDimension


class ReasoningAgent(BaseGradingAgent):
    """Evaluates the quality and logic of reasoning."""
    
    def __init__(self, temperature: float = 0.3, model: str = None):
        super().__init__(
            dimension=GradingDimension.REASONING,
            temperature=temperature,
            model=model,
        )
    
    @property
    def dimension_name(self) -> str:
        return "Quality of Reasoning"
    
    @property
    def evaluation_criteria(self) -> str:
        return """
## Evaluation Criteria for Quality of Reasoning

Evaluate the logical strength and persuasiveness of arguments:

**Score 6 (Outstanding)**
- Develops position with compelling, logically sound reasons
- Reasoning is sophisticated and addresses complexities
- Anticipates and effectively addresses counterarguments
- Arguments build logically upon each other
- Demonstrates excellent critical thinking

**Score 5 (Strong)**
- Develops position with logically sound reasons
- Reasoning is clear and well-articulated
- May address counterarguments or complications
- Arguments are well-connected
- Shows strong critical thinking

**Score 4 (Adequate)**
- Develops position with relevant reasons
- Logic is sound but may be predictable
- May not fully address counterarguments
- Arguments are connected but may lack depth
- Adequate critical thinking

**Score 3 (Limited)**
- Some relevant reasons but development is weak
- Logic may have gaps or inconsistencies
- Does not address counterarguments
- Arguments may be disconnected
- Limited critical thinking

**Score 2 (Seriously Flawed)**
- Reasons are weak, irrelevant, or missing
- Logic is flawed or contradictory
- Reasoning does not support the position
- Arguments are incoherent
- Little critical thinking evident

**Score 1 (Fundamentally Deficient)**
- No logical reasoning present
- Arguments are incomprehensible
- No attempt at analysis

## What to Look For
- Are reasons logical and relevant?
- Do arguments support the thesis?
- Are there logical fallacies?
- Does the writer anticipate objections?
- How deep is the analysis?
- Are cause-effect relationships valid?
"""
