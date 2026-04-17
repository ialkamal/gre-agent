"""LangGraph workflow nodes."""
import asyncio
import time
from typing import Any
from app.agents import Grader, ConsensusAgent
from app.memory import LongTermMemory
from app.config import get_settings


settings = get_settings()


async def load_student_context(state: dict) -> dict[str, Any]:
    """
    Node: Load student's historical context from long-term memory.
    
    This includes:
    - Previous essay scores
    - Identified weak areas
    - Improvement trends
    """
    memory = LongTermMemory()
    student_id = state.get("student_id")
    
    try:
        # Ensure student exists before any FK-dependent operations
        await memory.get_or_create_student(student_id)
        
        # Load weak areas
        weak_areas = await memory.get_weak_areas(student_id)
        
        # Load previous scores per dimension
        previous_scores = await memory.get_dimension_history(student_id)
        
        # Build session context string
        context_parts = []
        if weak_areas:
            context_parts.append(
                f"Student's historical weak areas: {', '.join([w.dimension.value for w in weak_areas])}"
            )
        
        session_context = "\n".join(context_parts) if context_parts else None
        
        return {
            "weak_areas": weak_areas,
            "previous_scores": previous_scores,
            "session_context": session_context,
        }
    except Exception as e:
        return {
            "weak_areas": [],
            "previous_scores": {},
            "session_context": None,
            "errors": [f"Failed to load student context: {str(e)}"],
        }


async def run_grader(
    grader_id: int,
    temperature: float,
    state: dict,
) -> dict[str, Any]:
    """Run a single grader with all 8 agents."""
    start_time = time.time()
    
    grader = Grader(
        grader_id=grader_id,
        temperature=temperature,
    )
    
    # Extract weak area dimension names for context
    weak_areas = state.get("weak_areas", [])
    weak_area_names = [wa.dimension.value for wa in weak_areas] if weak_areas else []
    
    result = await grader.grade(
        prompt=state.get("essay_prompt", ""),
        essay=state.get("essay_text", ""),
        weak_areas=weak_area_names,
        session_context=state.get("session_context"),
    )
    
    grading_time = int((time.time() - start_time) * 1000)
    
    return {
        "grader_results": [result],
        "total_grading_time_ms": grading_time,
    }


async def run_all_graders(state: dict) -> dict[str, Any]:
    """
    Node: Run all graders in parallel.
    
    Each grader has a different temperature for diversity:
    - Grader 0: temperature=0.3 (more deterministic)
    - Grader 1: temperature=0.5 (balanced)
    - Grader 2: temperature=0.7 (more creative)
    """
    temperatures = settings.grader_temperatures
    
    # Run all graders in parallel
    tasks = [
        run_grader(i, temperatures[i], state)
        for i in range(settings.num_graders)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Combine results
    all_grader_results = []
    total_time = 0
    errors = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append(f"Grader {i} failed: {str(result)}")
        else:
            all_grader_results.extend(result.get("grader_results", []))
            total_time += result.get("total_grading_time_ms", 0)
    
    return {
        "grader_results": all_grader_results,
        "total_grading_time_ms": total_time,
        "errors": errors if errors else [],
    }


async def build_consensus(state: dict) -> dict[str, Any]:
    """
    Node: Build consensus from all grader results.
    
    - Averages scores across graders
    - Identifies high-variance dimensions
    - Merges feedback
    - Prioritizes improvements based on weak areas
    """
    grader_results = state.get("grader_results", [])
    
    if not grader_results:
        return {
            "errors": ["No grader results to build consensus from"],
        }
    
    consensus_agent = ConsensusAgent()
    
    try:
        consensus = await consensus_agent.build_consensus(
            grader_results=grader_results,
            weak_areas=state.get("weak_areas", []),
        )
        
        return {"consensus": consensus}
    except Exception as e:
        return {
            "errors": [f"Consensus building failed: {str(e)}"],
        }


async def update_memory(state: dict) -> dict[str, Any]:
    """
    Node: Update dimension history with grading results.
    
    Note: Essay storage is handled by the API route to include model essay data.
    This node only updates dimension history for weak area tracking.
    """
    consensus = state.get("consensus")
    
    if not consensus:
        return {}
    
    memory = LongTermMemory()
    
    try:
        # Only update dimension history - essay storage handled by API route
        await memory.update_dimension_history(
            student_id=state.get("student_id"),
            dimension_scores=consensus.dimension_scores,
        )
        
        return {}
    except Exception as e:
        return {
            "errors": [f"Failed to update memory: {str(e)}"],
        }
