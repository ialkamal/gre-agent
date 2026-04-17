"""Evidence and Examples Agent - Has access to web search for fact-checking."""
from app.agents.base import BaseGradingAgent, AgentScore
from app.schemas import GradingDimension
from app.tools import get_evidence_tools
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Optional


class EvidenceAgent(BaseGradingAgent):
    """Evaluates use of evidence and examples. Has web search capability for fact-checking."""
    
    def __init__(self, temperature: float = 0.3, model: str = None):
        super().__init__(
            dimension=GradingDimension.EVIDENCE,
            temperature=temperature,
            model=model,
        )
        # This agent has tools for fact-checking
        self._tools = get_evidence_tools()
        self._agent_executor = self._build_agent_executor()
    
    @property
    def dimension_name(self) -> str:
        return "Use of Evidence and Examples"
    
    @property
    def tools(self) -> list:
        return self._tools
    
    @property
    def evaluation_criteria(self) -> str:
        return """
## Evaluation Criteria for Evidence and Examples

Evaluate the quality, relevance, and accuracy of evidence and examples:

**Score 6 (Outstanding)**
- Uses persuasive, well-chosen examples
- Evidence is specific, relevant, and compelling
- Examples effectively illustrate key points
- May draw from diverse sources (history, literature, current events, personal experience)
- Evidence is accurate and well-integrated

**Score 5 (Strong)**
- Uses well-chosen examples that support the position
- Evidence is specific and relevant
- Examples effectively support arguments
- Draws from appropriate sources
- Evidence is generally accurate

**Score 4 (Adequate)**
- Uses relevant examples to support position
- Evidence is reasonably specific
- Examples support the arguments made
- Sources are appropriate if limited
- Evidence is mostly accurate

**Score 3 (Limited)**
- Examples are present but may be weak or generic
- Evidence lacks specificity
- Examples may not clearly support arguments
- Limited variety in sources
- Some evidence may be inaccurate

**Score 2 (Seriously Flawed)**
- Examples are irrelevant or missing
- Little or no specific evidence
- Examples do not support the position
- Evidence may be inaccurate
- Relies on unsupported assertions

**Score 1 (Fundamentally Deficient)**
- No examples or evidence provided
- Completely unsupported claims
- No attempt to illustrate points

## What to Look For
- Are examples specific or vague?
- Do examples support the thesis?
- Are facts and claims accurate? (Use web search to verify if needed)
- Is there variety in types of evidence?
- Are examples well-integrated or just listed?
- Does the evidence persuade?

## IMPORTANT: Fact-Checking
When the essay contains specific claims, statistics, historical facts, or references to 
real-world events, USE THE WEB SEARCH TOOLS to verify accuracy. Note any factual 
inaccuracies in your feedback.
"""
    
    def _build_agent_executor(self) -> AgentExecutor:
        """Build an agent executor with fact-checking tools."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert GRE evaluator for {self.dimension_name}.
            
{self.evaluation_criteria}

You have access to web search tools to fact-check claims in essays.

IMPORTANT: You MUST use the search_web or fact_check_claim tools at least once to verify any specific factual claims, statistics, historical events, or examples mentioned in the essay. Even if claims seem accurate, verify at least one.

After using tools and evaluating, provide your assessment in JSON format with these fields:
- "score": a number from 0-6 (use 0.5 increments)
- "feedback": detailed feedback string
- "strengths": array of strength strings  
- "improvements": array of improvement strings
- "evidence": array of quotes or examples from essay
- "fact_checks": array of fact-checking results from your tool usage
"""),
            ("human", """Essay Prompt: {prompt}

Student's Essay: {essay}

Weak Areas: {weak_areas}

INSTRUCTIONS:
1. First, identify any factual claims, statistics, or specific examples in the essay
2. Use search_web or fact_check_claim to verify at least one claim
3. Then evaluate the use of evidence and examples
4. Provide your JSON assessment"""),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, self._tools, prompt)
        return AgentExecutor(
            agent=agent, 
            tools=self._tools, 
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )
    
    async def evaluate(
        self,
        prompt: str,
        essay: str,
        weak_areas: Optional[list[str]] = None,
        session_context: Optional[str] = None,
    ) -> tuple[AgentScore, int]:
        """Evaluate with fact-checking capability. Returns (score, fact_check_count)."""
        from app.agents.base import retry_with_backoff
        
        async def invoke_agent():
            return await self._agent_executor.ainvoke({
                "prompt": prompt,
                "essay": essay,
                "weak_areas": ", ".join(weak_areas) if weak_areas else "No previous history",
            })
        
        result = await retry_with_backoff(invoke_agent)
        
        # Count fact checks from intermediate steps
        fact_check_count = 0
        intermediate_steps = result.get("intermediate_steps", [])
        for step in intermediate_steps:
            if len(step) >= 1:
                action = step[0]
                if hasattr(action, 'tool') and action.tool in ['search_web', 'fact_check_claim']:
                    fact_check_count += 1
        
        # Parse the output into AgentScore
        import json
        try:
            output = result.get("output", "")
            # Try to extract JSON from the output
            if "{" in output:
                json_str = output[output.find("{"):output.rfind("}")+1]
                data = json.loads(json_str)
                score = AgentScore(
                    score=self._round_to_half(data.get("score", 3)),
                    feedback=data.get("feedback", output),
                    strengths=data.get("strengths", []),
                    improvements=data.get("improvements", []),
                    evidence=data.get("evidence", []),
                )
                return score, fact_check_count
        except (json.JSONDecodeError, KeyError):
            pass
        
        # Fallback: use base evaluation
        base_score = await super().evaluate(prompt, essay, weak_areas, session_context)
        return base_score, fact_check_count
    
    def _round_to_half(self, score: float) -> float:
        """Round score to nearest 0.5 (GRE uses 0-6 in 0.5 increments)."""
        return round(score * 2) / 2
