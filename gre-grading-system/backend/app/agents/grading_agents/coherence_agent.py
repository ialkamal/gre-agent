"""Overall Coherence and Persuasiveness Agent."""
from app.agents.base import BaseGradingAgent
from app.schemas import GradingDimension


class CoherenceAgent(BaseGradingAgent):
    """Evaluates overall coherence and persuasive power of the essay."""
    
    def __init__(self, temperature: float = 0.3, model: str = None):
        super().__init__(
            dimension=GradingDimension.COHERENCE,
            temperature=temperature,
            model=model,
        )
    
    @property
    def dimension_name(self) -> str:
        return "Overall Coherence and Persuasiveness"
    
    @property
    def evaluation_criteria(self) -> str:
        return """
## Evaluation Criteria for Overall Coherence and Persuasiveness

Evaluate how well all elements work together and how persuasive the essay is as a whole:

**Score 6 (Outstanding)**
- All elements work together seamlessly
- Essay is highly persuasive and compelling
- Reader is convinced by the argument
- Ideas connect logically throughout
- Strong sense of unity and purpose
- Effective conclusion reinforces thesis
- Outstanding overall impression

**Score 5 (Strong)**
- Elements work well together
- Essay is persuasive
- Argument is convincing
- Good logical connections throughout
- Clear sense of unity
- Conclusion effectively wraps up
- Strong overall impression

**Score 4 (Adequate)**
- Elements are reasonably integrated
- Essay is adequately persuasive
- Argument makes sense
- Logical connections present
- General sense of unity
- Conclusion present and functional
- Satisfactory overall impression

**Score 3 (Limited)**
- Elements do not fully cohere
- Persuasiveness is limited
- Argument may not convince
- Logical connections weak
- Limited sense of unity
- Conclusion may be weak
- Mediocre overall impression

**Score 2 (Seriously Flawed)**
- Little coherence between elements
- Not persuasive
- Argument fails to convince
- Poor logical connections
- No sense of unity
- Conclusion missing or ineffective
- Poor overall impression

**Score 1 (Fundamentally Deficient)**
- No coherence
- Completely unpersuasive
- No argument evident
- Disjointed throughout
- Failed attempt overall

## What to Look For
- Does the essay work as a unified whole?
- Is the reader persuaded by the argument?
- Do all parts support the thesis?
- Is there a clear beginning, middle, and end?
- Does the conclusion reinforce the argument?
- What is your overall impression as a reader?
- Would this essay achieve its purpose?
"""
