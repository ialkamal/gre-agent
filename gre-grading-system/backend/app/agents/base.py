"""Base agent class for all grading agents."""
import asyncio
from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.config import get_settings
from app.schemas import GradingDimension


async def retry_with_backoff(func, max_retries=5, base_delay=1.0):
    """Retry an async function with exponential backoff for rate limits."""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            err_str = str(e).lower()
            if "rate_limit" in err_str or "429" in err_str or "rate limit" in err_str:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                print(f"Rate limit hit, waiting {delay}s before retry {attempt + 1}/{max_retries}")
                await asyncio.sleep(delay)
            else:
                raise


class AgentScore(BaseModel):
    """Output schema for a single dimension score."""
    score: float = Field(ge=0, le=6, description="Score from 0-6 on GRE scale")
    feedback: str = Field(description="Detailed feedback explaining the score")
    strengths: list[str] = Field(default_factory=list, description="Specific strengths observed")
    improvements: list[str] = Field(default_factory=list, description="Specific areas for improvement")
    evidence: list[str] = Field(default_factory=list, description="Quotes or examples from essay supporting the evaluation")


GRE_SCORING_RUBRIC = """
## GRE Issue Writing Scoring Rubric (0-6 Scale)

**Score 6 - Outstanding**
- Presents an insightful position on the issue
- Develops ideas with compelling reasons and/or persuasive examples
- Sustains a well-focused, well-organized analysis
- Demonstrates superior facility with language
- May have minor errors that do not interfere with meaning

**Score 5 - Strong**  
- Presents a clear and considered position
- Develops ideas with logically sound reasons and/or well-chosen examples
- Is focused and generally well organized
- Demonstrates facility with language
- May have minor errors

**Score 4 - Adequate**
- Presents a clear position on the issue
- Develops ideas with relevant reasons and/or examples
- Is adequately organized
- Demonstrates adequate control of language
- May have some errors that affect clarity

**Score 3 - Limited**
- Shows some competence but is flawed
- Vague or limited analysis
- Weak development or organization
- Problems with language or sentence structure
- Accumulation of errors

**Score 2 - Seriously Flawed**
- Shows little evidence of ability to develop position
- Provides little support or irrelevant support
- Serious and frequent problems with language
- Serious errors obscure meaning

**Score 1 - Fundamentally Deficient**
- Shows little or no evidence of understanding the issue
- Little or no development
- Severe problems with language
- Pervasive errors

**Score 0 - Off Topic/Blank**
- Does not address the prompt or is blank
"""


class BaseGradingAgent(ABC):
    """Base class for all grading agents."""
    
    def __init__(
        self,
        dimension: GradingDimension,
        temperature: float = 0.3,
        model: Optional[str] = None,
    ):
        self.dimension = dimension
        self.temperature = temperature
        self.settings = get_settings()
        self.model_name = model or self.settings.openai_model
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=self.settings.openai_api_key,
            model=self.model_name,
            temperature=temperature,
        )
        
        # Output parser
        self.parser = PydanticOutputParser(pydantic_object=AgentScore)
        
        # Build prompt
        self.prompt = self._build_prompt()
    
    @property
    @abstractmethod
    def dimension_name(self) -> str:
        """Human-readable name of the dimension being evaluated."""
        pass
    
    @property
    @abstractmethod
    def evaluation_criteria(self) -> str:
        """Specific criteria for this dimension."""
        pass
    
    @property
    def tools(self) -> list:
        """Tools available to this agent. Override in subclasses if needed."""
        return []
    
    def _build_prompt(self) -> ChatPromptTemplate:
        """Build the evaluation prompt."""
        system_template = f"""You are an expert GRE Issue Writing evaluator specializing in {self.dimension_name}.

{GRE_SCORING_RUBRIC}

## Your Specific Evaluation Focus: {self.dimension_name}

{self.evaluation_criteria}

## Evaluation Guidelines
1. Read the essay prompt and response carefully
2. Evaluate ONLY the {self.dimension_name} dimension
3. Provide a score from 0-6 in 0.5 increments based on GRE standards
4. Be specific in feedback - cite examples from the essay
5. List concrete strengths and areas for improvement
6. For EACH improvement suggestion, include a brief example showing how to apply it
7. Consider the student's weak areas from previous attempts when providing feedback

Example improvement format:
- "Vary your sentence structure. Example: Instead of 'Technology is helpful. Technology saves time.' try 'While technology proves helpful in many contexts, its greatest benefit lies in the time it saves.'"

{{format_instructions}}
"""
        
        human_template = """## Essay Prompt
{prompt}

## Student's Essay
{essay}

## Student's Historical Weak Areas (if any)
{weak_areas}

## Session Context
{session_context}

Evaluate this essay for {dimension_name}. Provide your score, feedback, and for each improvement suggestion include a short example."""

        return ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("human", human_template),
        ])
    
    async def evaluate(
        self,
        prompt: str,
        essay: str,
        weak_areas: Optional[list[str]] = None,
        session_context: Optional[str] = None,
    ) -> AgentScore:
        """Evaluate the essay for this dimension."""
        chain = self.prompt | self.llm | self.parser
        
        async def invoke_chain():
            return await chain.ainvoke({
                "prompt": prompt,
                "essay": essay,
                "weak_areas": ", ".join(weak_areas) if weak_areas else "No previous history",
                "session_context": session_context or "New session",
                "dimension_name": self.dimension_name,
                "format_instructions": self.parser.get_format_instructions(),
            })
        
        return await retry_with_backoff(invoke_chain)
