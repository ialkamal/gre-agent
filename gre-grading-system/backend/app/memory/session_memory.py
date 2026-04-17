"""Session memory for maintaining conversation context within a grading session."""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class Message(BaseModel):
    """A message in the session conversation."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionMemory:
    """
    Manages session-level memory for a grading interaction.
    
    This includes:
    - Current essay being graded
    - Conversation history within the session
    - Session-specific insights and feedback
    """
    
    def __init__(self, session_id: Optional[str] = None, student_id: Optional[str] = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.student_id = student_id
        self.created_at = datetime.utcnow()
        
        # Session state
        self.current_essay_id: Optional[str] = None
        self.current_essay_prompt: Optional[str] = None
        self.current_essay_text: Optional[str] = None
        
        # Conversation history
        self.messages: list[Message] = []
        
        # Grading results for this session
        self.essays_graded: int = 0
        self.session_scores: list[float] = []
        
        # Session insights
        self.session_weak_areas: list[str] = []
        self.session_improvements: list[str] = []
    
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.messages.append(Message(role=role, content=content))
    
    def get_recent_messages(self, n: int = 10) -> list[Message]:
        """Get the N most recent messages."""
        return self.messages[-n:]
    
    def get_context_string(self) -> str:
        """Get conversation context as a formatted string."""
        recent = self.get_recent_messages(5)
        context_parts = []
        
        for msg in recent:
            context_parts.append(f"[{msg.role}]: {msg.content[:200]}...")
        
        return "\n".join(context_parts)
    
    def set_current_essay(self, essay_id: str, prompt: str, text: str) -> None:
        """Set the current essay being graded."""
        self.current_essay_id = essay_id
        self.current_essay_prompt = prompt
        self.current_essay_text = text
    
    def record_grading_result(self, score: float, weak_areas: list[str]) -> None:
        """Record a grading result for this session."""
        self.essays_graded += 1
        self.session_scores.append(score)
        
        # Update session weak areas (accumulate unique ones)
        for area in weak_areas:
            if area not in self.session_weak_areas:
                self.session_weak_areas.append(area)
    
    def get_session_summary(self) -> dict:
        """Get a summary of this session."""
        return {
            "session_id": self.session_id,
            "student_id": self.student_id,
            "essays_graded": self.essays_graded,
            "average_score": sum(self.session_scores) / len(self.session_scores) if self.session_scores else None,
            "weak_areas_identified": self.session_weak_areas,
            "duration_minutes": (datetime.utcnow() - self.created_at).seconds // 60,
        }
    
    def to_dict(self) -> dict:
        """Serialize session memory to dictionary."""
        return {
            "session_id": self.session_id,
            "student_id": self.student_id,
            "created_at": self.created_at.isoformat(),
            "current_essay_id": self.current_essay_id,
            "essays_graded": self.essays_graded,
            "session_scores": self.session_scores,
            "session_weak_areas": self.session_weak_areas,
            "messages": [
                {"role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat()}
                for m in self.messages
            ],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionMemory":
        """Deserialize session memory from dictionary."""
        memory = cls(
            session_id=data["session_id"],
            student_id=data.get("student_id"),
        )
        memory.created_at = datetime.fromisoformat(data["created_at"])
        memory.current_essay_id = data.get("current_essay_id")
        memory.essays_graded = data.get("essays_graded", 0)
        memory.session_scores = data.get("session_scores", [])
        memory.session_weak_areas = data.get("session_weak_areas", [])
        
        for msg_data in data.get("messages", []):
            memory.messages.append(Message(
                role=msg_data["role"],
                content=msg_data["content"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
            ))
        
        return memory


# In-memory session store (for demo; use Redis in production)
_sessions: dict[str, SessionMemory] = {}


def get_session(session_id: str) -> Optional[SessionMemory]:
    """Get a session by ID."""
    return _sessions.get(session_id)


def create_session(student_id: str) -> SessionMemory:
    """Create a new session."""
    session = SessionMemory(student_id=student_id)
    _sessions[session.session_id] = session
    return session


def delete_session(session_id: str) -> bool:
    """Delete a session."""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False
