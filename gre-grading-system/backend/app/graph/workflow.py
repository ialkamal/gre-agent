"""Main LangGraph workflow for essay grading."""
from typing import TypedDict, Annotated, Optional
from operator import add
from langgraph.graph import StateGraph, END
from app.graph.nodes import (
    load_student_context,
    run_all_graders,
    build_consensus,
    update_memory,
)
from app.schemas import GraderResult, ConsensusResult, WeakArea


class GradingStateDict(TypedDict, total=False):
    """State dictionary for the grading workflow."""
    student_id: str
    essay_prompt: str
    essay_text: str
    session_id: Optional[str]
    weak_areas: list[WeakArea]
    previous_scores: dict[str, list[float]]
    session_context: Optional[str]
    grader_results: Annotated[list[GraderResult], add]
    consensus: Optional[ConsensusResult]
    fact_checks_performed: int
    total_grading_time_ms: int
    errors: Annotated[list[str], add]


def create_grading_workflow() -> StateGraph:
    """
    Create the main grading workflow graph.
    
    Workflow:
    1. Load student context (weak areas, history)
    2. Run 3 parallel graders (each with 8 agents)
    3. Build consensus from grader results
    4. Update long-term memory
    """
    # Create the graph with dict state
    workflow = StateGraph(GradingStateDict)
    
    # Add nodes
    workflow.add_node("load_context", load_student_context)
    workflow.add_node("run_graders", run_all_graders)
    workflow.add_node("build_consensus", build_consensus)
    workflow.add_node("update_memory", update_memory)
    
    # Define edges (linear flow)
    workflow.set_entry_point("load_context")
    workflow.add_edge("load_context", "run_graders")
    workflow.add_edge("run_graders", "build_consensus")
    workflow.add_edge("build_consensus", "update_memory")
    workflow.add_edge("update_memory", END)
    
    return workflow


def compile_grading_workflow():
    """Compile the grading workflow for execution."""
    workflow = create_grading_workflow()
    return workflow.compile()


# Global compiled workflow instance
grading_app = compile_grading_workflow()


async def grade_essay(
    student_id: str,
    essay_prompt: str,
    essay_text: str,
    session_id: str = None,
) -> dict:
    """
    Grade an essay using the multi-agent workflow.
    
    Args:
        student_id: Unique student identifier
        essay_prompt: The GRE Issue Writing prompt
        essay_text: Student's essay response
        session_id: Optional session ID for context
        
    Returns:
        Final grading state with consensus results
    """
    initial_state = {
        "student_id": student_id,
        "essay_prompt": essay_prompt,
        "essay_text": essay_text,
        "session_id": session_id,
        "weak_areas": [],
        "previous_scores": {},
        "session_context": None,
        "grader_results": [],
        "consensus": None,
        "fact_checks_performed": 0,
        "total_grading_time_ms": 0,
        "errors": [],
    }
    
    # Run the workflow
    final_state = await grading_app.ainvoke(initial_state)
    
    return final_state
