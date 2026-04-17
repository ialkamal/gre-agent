"""API routes package."""
from .grading import router as grading_router
from .students import router as students_router
from .history import router as history_router

__all__ = ["grading_router", "students_router", "history_router"]
