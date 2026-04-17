"""Web search tool using Tavily API for fact-checking evidence and examples."""
import os
from typing import Optional
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from app.config import get_settings


class FactCheckResult(BaseModel):
    """Result of a fact-check operation."""
    claim: str
    is_verified: bool
    confidence: float = Field(ge=0, le=1)
    sources: list[str]
    summary: str


def _ensure_tavily_env():
    """Ensure TAVILY_API_KEY is set in environment from config."""
    settings = get_settings()
    if settings.tavily_api_key and not os.environ.get("TAVILY_API_KEY"):
        os.environ["TAVILY_API_KEY"] = settings.tavily_api_key


def create_tavily_search_tool(max_results: int = 3) -> TavilySearchResults:
    """Create a Tavily search tool instance."""
    _ensure_tavily_env()
    return TavilySearchResults(
        max_results=max_results,
        search_depth="basic",
    )


@tool
def search_web(query: str) -> str:
    """
    Search the web for information to verify facts, claims, or examples.
    
    Use this tool when you need to:
    - Verify historical facts mentioned in an essay
    - Check accuracy of statistics or data
    - Confirm details about real-world examples
    - Find context for current events referenced
    
    Args:
        query: The search query to find relevant information
        
    Returns:
        Search results with relevant information
    """
    _ensure_tavily_env()
    search = TavilySearchResults(max_results=3)
    results = search.invoke(query)
    return str(results)


@tool
def fact_check_claim(claim: str, context: Optional[str] = None) -> str:
    """
    Fact-check a specific claim made in the essay.
    
    Use this tool to verify factual claims, statistics, historical events,
    or specific examples cited by the student.
    
    Args:
        claim: The specific factual claim to verify
        context: Additional context about the claim
        
    Returns:
        Verification result with sources
    """
    _ensure_tavily_env()
    search = TavilySearchResults(
        max_results=3,
        search_depth="advanced",
    )
    
    query = f"verify: {claim}"
    if context:
        query += f" context: {context}"
    
    results = search.invoke(query)
    return f"Fact check for '{claim}':\n{results}"


def get_evidence_tools() -> list:
    """Get all tools available to the Evidence Agent."""
    _ensure_tavily_env()
    return [search_web, fact_check_claim]
