"""Grading API routes."""
import uuid
import time
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from app.schemas import GradingRequest, GradingResponse, GradingDimension, ModelEssay
from app.graph import grade_essay
from app.memory import LongTermMemory, create_session, get_session
from app.agents import ModelEssayGenerator


router = APIRouter(prefix="/grading", tags=["grading"])


@router.post("/grade", response_model=GradingResponse)
async def grade_essay_endpoint(request: GradingRequest):
    """
    Grade a GRE Issue Writing essay.
    
    This endpoint:
    1. Loads student's historical context (weak areas)
    2. Runs 3 parallel graders (each with 8 dimension agents)
    3. Builds consensus from grader results
    4. Generates a model essay showing how to score 6
    5. Updates long-term memory
    6. Returns comprehensive feedback
    
    The grading process takes 30-60 seconds due to multiple LLM calls.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Validate essay length
    word_count = len(request.essay_text.split())
    if word_count < 50:
        raise HTTPException(
            status_code=400,
            detail="Essay is too short. Please write at least 50 words."
        )
    
    try:
        # Run the grading workflow (returns dict)
        final_state = await grade_essay(
            student_id=request.student_id,
            essay_prompt=request.essay_prompt,
            essay_text=request.essay_text,
            session_id=request.session_id,
        )
        
        # Check for errors
        errors = final_state.get("errors", [])
        if errors:
            raise HTTPException(
                status_code=500,
                detail=f"Grading errors: {'; '.join(errors)}"
            )
        
        consensus = final_state.get("consensus")
        if not consensus:
            raise HTTPException(
                status_code=500,
                detail="Failed to build consensus from grader results"
            )
        
        # Generate model essay (rewritten version scoring 6)
        model_essay_data = None
        model_essay_text = None
        model_essay_notes = None
        try:
            generator = ModelEssayGenerator()
            model_result = await generator.generate_model_essay(
                essay_prompt=request.essay_prompt,
                original_essay=request.essay_text,
                consensus=consensus,
            )
            model_essay_text = model_result["model_essay"]
            model_essay_notes = model_result["improvement_notes"]
            model_essay_data = ModelEssay(
                model_essay=model_essay_text,
                improvement_notes=model_essay_notes,
                word_count=model_result["word_count"],
            )
        except Exception as e:
            # Don't fail the whole request if model essay generation fails
            print(f"Model essay generation failed: {e}")
        
        # Get improvement from last essay
        memory = LongTermMemory()
        improvement = await memory.get_improvement_from_last(
            student_id=request.student_id,
            current_scores=consensus.dimension_scores,
        )
        
        # Store the model essay in the database (update after workflow)
        grader_results = final_state.get("grader_results", [])
        try:
            await memory.store_grading_result(
                student_id=request.student_id,
                essay_prompt=request.essay_prompt,
                essay_text=request.essay_text,
                consensus=consensus,
                grader_results=grader_results,
                model_essay=model_essay_text,
                model_essay_notes=model_essay_notes,
            )
        except Exception as e:
            print(f"Failed to store grading result with model essay: {e}")
        
        total_time = int((time.time() - start_time) * 1000)
        
        # Calculate total fact checks from all graders
        total_fact_checks = sum(gr.fact_checks_count for gr in grader_results)
        
        return GradingResponse(
            request_id=request_id,
            student_id=request.student_id,
            timestamp=datetime.utcnow(),
            grader_results=grader_results,
            consensus=consensus,
            weak_areas=final_state.get("weak_areas", []),
            improvement_from_last=improvement,
            model_essay=model_essay_data,
            total_grading_time_ms=total_time,
            fact_checks_performed=total_fact_checks,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Grading failed: {str(e)}"
        )


@router.post("/grade/quick")
async def quick_grade_endpoint(request: GradingRequest):
    """
    Quick grading with a single grader (faster but less accurate).
    
    Use this for testing or when speed is more important than accuracy.
    """
    from app.agents import Grader
    
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        grader = Grader(grader_id=0, temperature=0.3)
        
        # Get weak areas for context
        memory = LongTermMemory()
        weak_areas = await memory.get_weak_areas(request.student_id)
        weak_area_names = [wa.dimension.value for wa in weak_areas]
        
        result = await grader.grade(
            prompt=request.essay_prompt,
            essay=request.essay_text,
            weak_areas=weak_area_names,
        )
        
        total_time = int((time.time() - start_time) * 1000)
        
        return {
            "request_id": request_id,
            "student_id": request.student_id,
            "grader_result": result,
            "total_grading_time_ms": total_time,
            "note": "This is a quick grade with single grader. Use /grade for full consensus grading."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quick grading failed: {str(e)}"
        )


@router.get("/dimensions")
async def get_grading_dimensions():
    """Get list of all grading dimensions with descriptions."""
    dimensions = [
        {
            "id": "thesis",
            "name": "Clarity of Position (Thesis)",
            "description": "How clearly and effectively the writer establishes their position on the issue.",
            "weight": 1.2,
        },
        {
            "id": "reasoning",
            "name": "Quality of Reasoning",
            "description": "The logical strength and persuasiveness of the arguments.",
            "weight": 1.3,
        },
        {
            "id": "evidence",
            "name": "Use of Evidence & Examples",
            "description": "Quality, relevance, and accuracy of evidence and examples.",
            "weight": 1.1,
        },
        {
            "id": "structure",
            "name": "Organization & Structure",
            "description": "How well the essay is organized with clear introduction, body, and conclusion.",
            "weight": 1.0,
        },
        {
            "id": "analysis",
            "name": "Depth of Analysis",
            "description": "Sophistication and depth of the analysis, considering multiple perspectives.",
            "weight": 1.2,
        },
        {
            "id": "language",
            "name": "Language Use & Style",
            "description": "Vocabulary, sentence variety, and stylistic effectiveness.",
            "weight": 1.0,
        },
        {
            "id": "grammar",
            "name": "Grammar & Mechanics",
            "description": "Grammatical correctness, punctuation, and spelling.",
            "weight": 0.8,
        },
        {
            "id": "coherence",
            "name": "Overall Coherence & Persuasiveness",
            "description": "How well all elements work together and the overall persuasive power.",
            "weight": 1.1,
        },
    ]
    return {"dimensions": dimensions}
