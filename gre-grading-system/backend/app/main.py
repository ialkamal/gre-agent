"""FastAPI main application."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.routes import grading_router, students_router, history_router


settings = get_settings()

# Set environment variables for LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langchain_tracing_v2).lower()
os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 Starting GRE Grading System...")
    print(f"📊 LangSmith tracing: {settings.langchain_tracing_v2}")
    print(f"🗄️ Database: {settings.database_url[:50]}...")
    
    # Initialize database tables
    try:
        from app.db import init_db
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down GRE Grading System...")


app = FastAPI(
    title="GRE Issue Writing Grading System",
    description="""
    A multi-agent system for grading GRE Issue Writing essays.
    
    ## Features
    - 3 parallel graders, each with 8 specialized dimension agents
    - Consensus building with variance detection
    - Long-term memory for tracking student weak areas
    - Web search integration for fact-checking evidence
    - LangSmith monitoring for all agent interactions
    
    ## Grading Dimensions
    1. Clarity of Position (Thesis)
    2. Quality of Reasoning
    3. Use of Evidence & Examples
    4. Organization & Structure
    5. Depth of Analysis
    6. Language Use & Style
    7. Grammar & Mechanics
    8. Overall Coherence & Persuasiveness
    
    ## Scoring Scale
    - 6: Outstanding
    - 5: Strong
    - 4: Adequate
    - 3: Limited
    - 2: Seriously Flawed
    - 1: Fundamentally Deficient
    - 0: Off-topic or blank
    """,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(grading_router, prefix="/api/v1")
app.include_router(students_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "GRE Issue Writing Grading System",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "langsmith_enabled": settings.langchain_tracing_v2,
        "database_configured": bool(settings.database_url),
    }


@app.get("/api/v1/sample-prompts")
async def get_sample_prompts():
    """Get sample GRE Issue Writing prompts for practice."""
    return {
        "prompts": [
            {
                "id": 1,
                "prompt": "As people rely more and more on technology to solve problems, the ability of humans to think for themselves will surely deteriorate.",
                "instructions": "Discuss the extent to which you agree or disagree with the statement and explain your reasoning for the position you take. In developing and supporting your position, you should consider ways in which the statement might or might not hold true and explain how these considerations shape your position.",
            },
            {
                "id": 2,
                "prompt": "The best ideas arise from a passionate interest in commonplace things.",
                "instructions": "Write a response in which you discuss the extent to which you agree or disagree with the statement and explain your reasoning for the position you take. In developing and supporting your position, you should consider ways in which the statement might or might not hold true and explain how these considerations shape your position.",
            },
            {
                "id": 3,
                "prompt": "Educational institutions should actively encourage their students to choose fields of study that will prepare them for lucrative careers.",
                "instructions": "Write a response in which you discuss the extent to which you agree or disagree with the recommendation and explain your reasoning for the position you take. In developing and supporting your position, describe specific circumstances in which adopting the recommendation would or would not be advantageous and explain how these examples shape your position.",
            },
            {
                "id": 4,
                "prompt": "Governments should focus on solving the immediate problems of today rather than on trying to solve the anticipated problems of the future.",
                "instructions": "Write a response in which you discuss the extent to which you agree or disagree with the recommendation and explain your reasoning for the position you take. In developing and supporting your position, describe specific circumstances in which adopting the recommendation would or would not be advantageous and explain how these examples shape your position.",
            },
            {
                "id": 5,
                "prompt": "In any field of inquiry, the beginner is more likely than the expert to make important contributions.",
                "instructions": "Write a response in which you discuss the extent to which you agree or disagree with the statement and explain your reasoning for the position you take. In developing and supporting your position, you should consider ways in which the statement might or might not hold true and explain how these considerations shape your position.",
            },
        ]
    }
