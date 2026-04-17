"""Language Use and Style Agent."""
from app.agents.base import BaseGradingAgent
from app.schemas import GradingDimension


class LanguageAgent(BaseGradingAgent):
    """Evaluates language use, vocabulary, and style."""
    
    def __init__(self, temperature: float = 0.3, model: str = None):
        super().__init__(
            dimension=GradingDimension.LANGUAGE,
            temperature=temperature,
            model=model,
        )
    
    @property
    def dimension_name(self) -> str:
        return "Language Use and Style"
    
    @property
    def evaluation_criteria(self) -> str:
        return """
## Evaluation Criteria for Language Use and Style

Evaluate vocabulary, sentence variety, and stylistic choices:

**Score 6 (Outstanding)**
- Demonstrates superior facility with language
- Uses appropriate and precise vocabulary
- Excellent sentence variety and complexity
- Fluent and effective style
- Tone is appropriate and engaging
- Language enhances the argument

**Score 5 (Strong)**
- Demonstrates facility with language
- Uses appropriate vocabulary effectively
- Good sentence variety
- Clear and engaging style
- Appropriate tone
- Language supports the argument

**Score 4 (Adequate)**
- Demonstrates adequate control of language
- Uses appropriate vocabulary
- Some sentence variety
- Generally clear style
- Mostly appropriate tone
- Language is functional

**Score 3 (Limited)**
- Language use is adequate but limited
- Basic vocabulary
- Limited sentence variety
- Style may be awkward or unclear
- Tone may be inconsistent
- Language does not enhance

**Score 2 (Seriously Flawed)**
- Serious problems with language
- Poor vocabulary choices
- Little sentence variety
- Unclear or inappropriate style
- Problems affect communication
- Language obscures meaning

**Score 1 (Fundamentally Deficient)**
- Severe language deficiencies
- Fundamental lack of control
- Language prevents understanding

## What to Look For
- Is vocabulary appropriate and varied?
- Are sentences varied in structure?
- Is the style engaging or flat?
- Is word choice precise?
- Is the tone appropriate for academic writing?
- Does language enhance or detract from the argument?
"""
