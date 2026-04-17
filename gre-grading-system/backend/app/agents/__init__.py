"""Agents package."""
from .base import BaseGradingAgent, AgentScore
from .grader import Grader
from .consensus_agent import ConsensusAgent
from .model_essay_generator import ModelEssayGenerator
from .grading_agents import (
    ThesisAgent,
    ReasoningAgent,
    EvidenceAgent,
    StructureAgent,
    AnalysisAgent,
    LanguageAgent,
    GrammarAgent,
    CoherenceAgent,
    DIMENSION_AGENTS,
)

__all__ = [
    "BaseGradingAgent",
    "AgentScore",
    "Grader",
    "ConsensusAgent",
    "ModelEssayGenerator",
    "ThesisAgent",
    "ReasoningAgent",
    "EvidenceAgent",
    "StructureAgent",
    "AnalysisAgent",
    "LanguageAgent",
    "GrammarAgent",
    "CoherenceAgent",
    "DIMENSION_AGENTS",
]
