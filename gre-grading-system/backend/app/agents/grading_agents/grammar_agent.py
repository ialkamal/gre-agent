"""Grammar and Mechanics Agent."""
from app.agents.base import BaseGradingAgent
from app.schemas import GradingDimension


class GrammarAgent(BaseGradingAgent):
    """Evaluates grammar, punctuation, and mechanics."""
    
    def __init__(self, temperature: float = 0.3, model: str = None):
        super().__init__(
            dimension=GradingDimension.GRAMMAR,
            temperature=temperature,
            model=model,
        )
    
    @property
    def dimension_name(self) -> str:
        return "Grammar and Mechanics"
    
    @property
    def evaluation_criteria(self) -> str:
        return """
## Evaluation Criteria for Grammar and Mechanics

Evaluate grammatical correctness, punctuation, and mechanical accuracy:

**Score 6 (Outstanding)**
- Demonstrates excellent command of standard written English
- May have minor errors that do not interfere with meaning
- Correct grammar and usage throughout
- Proper punctuation and capitalization
- Correct spelling
- Errors are rare and minor

**Score 5 (Strong)**
- Demonstrates strong command of standard written English
- Few errors, none significant
- Generally correct grammar and usage
- Good punctuation and capitalization
- Minor spelling errors at most
- Errors do not distract

**Score 4 (Adequate)**
- Demonstrates adequate control of conventions
- Some errors but none serious
- Generally correct grammar
- Mostly correct punctuation
- Some spelling errors
- Errors may occasionally distract

**Score 3 (Limited)**
- Problems with grammar or mechanics
- Errors accumulate
- Some serious grammatical errors
- Punctuation problems
- Spelling errors present
- Errors affect clarity at times

**Score 2 (Seriously Flawed)**
- Serious and frequent errors
- Major grammatical problems
- Severe punctuation issues
- Many spelling errors
- Errors seriously affect meaning
- Difficult to read due to errors

**Score 1 (Fundamentally Deficient)**
- Pervasive errors throughout
- Fundamental grammatical problems
- Errors prevent understanding
- No control of conventions

## What to Look For
- Subject-verb agreement
- Verb tense consistency
- Pronoun reference and agreement
- Sentence fragments and run-ons
- Comma usage and punctuation
- Spelling errors
- Capitalization
- Parallel structure
"""
