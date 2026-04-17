"""Grading agents package."""
from .thesis_agent import ThesisAgent
from .reasoning_agent import ReasoningAgent
from .evidence_agent import EvidenceAgent
from .structure_agent import StructureAgent
from .analysis_agent import AnalysisAgent
from .language_agent import LanguageAgent
from .grammar_agent import GrammarAgent
from .coherence_agent import CoherenceAgent

__all__ = [
    "ThesisAgent",
    "ReasoningAgent",
    "EvidenceAgent",
    "StructureAgent",
    "AnalysisAgent",
    "LanguageAgent",
    "GrammarAgent",
    "CoherenceAgent",
]

# Mapping of dimension to agent class
DIMENSION_AGENTS = {
    "thesis": ThesisAgent,
    "reasoning": ReasoningAgent,
    "evidence": EvidenceAgent,
    "structure": StructureAgent,
    "analysis": AnalysisAgent,
    "language": LanguageAgent,
    "grammar": GrammarAgent,
    "coherence": CoherenceAgent,
}
