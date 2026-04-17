# Backend Documentation

## Overview

The backend is a FastAPI application that orchestrates the multi-agent grading system using LangChain and LangGraph. It provides REST APIs for essay submission, grading, and history retrieval.

## Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Settings from environment variables
│   │
│   ├── agents/                    # Agent implementations
│   │   ├── __init__.py
│   │   ├── base.py               # BaseGradingAgent abstract class
│   │   ├── grader.py             # Grader orchestrator
│   │   ├── consensus_agent.py    # Consensus building
│   │   └── grading_agents/       # 8 dimension-specific agents
│   │       ├── __init__.py
│   │       ├── thesis_agent.py
│   │       ├── reasoning_agent.py
│   │       ├── evidence_agent.py
│   │       ├── structure_agent.py
│   │       ├── analysis_agent.py
│   │       ├── language_agent.py
│   │       ├── grammar_agent.py
│   │       └── coherence_agent.py
│   │
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── grading.py        # Grading endpoints
│   │       ├── students.py       # Student management
│   │       └── history.py        # Essay history
│   │
│   ├── db/                       # Database layer
│   │   ├── __init__.py
│   │   └── database.py           # SQLAlchemy async setup
│   │
│   ├── graph/                    # LangGraph workflow
│   │   ├── __init__.py
│   │   ├── state.py              # State definitions
│   │   ├── nodes.py              # Node functions
│   │   └── workflow.py           # Graph compilation
│   │
│   ├── memory/                   # Memory systems
│   │   ├── __init__.py
│   │   ├── session_memory.py     # Session-scoped memory
│   │   └── long_term_memory.py   # PostgreSQL persistence
│   │
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   └── models.py             # SQLAlchemy ORM models
│   │
│   ├── schemas/                  # API schemas
│   │   ├── __init__.py
│   │   └── grading.py            # Pydantic models
│   │
│   └── tools/                    # Agent tools
│       ├── __init__.py
│       └── web_search.py         # Tavily integration
│
├── requirements.txt
├── Dockerfile
└── .env.example
```

---

## Agent System

### BaseGradingAgent (base.py)

Abstract base class for all grading agents.

```python
class BaseGradingAgent(ABC):
    """Base class for all grading agents."""

    def __init__(
        self,
        dimension: GradingDimension,
        temperature: float = 0.3,
        model: Optional[str] = None,
    ):
        self.dimension = dimension
        self.temperature = temperature
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.parser = PydanticOutputParser(pydantic_object=AgentScore)
        self.prompt = self._build_prompt()

    @property
    @abstractmethod
    def dimension_name(self) -> str:
        """Human-readable name of the dimension."""
        pass

    @property
    @abstractmethod
    def evaluation_criteria(self) -> str:
        """Specific criteria for this dimension."""
        pass

    async def evaluate(
        self,
        prompt: str,
        essay: str,
        weak_areas: Optional[list[str]] = None,
        session_context: Optional[str] = None,
    ) -> AgentScore:
        """Evaluate the essay for this dimension."""
        # Uses retry_with_backoff for rate limit handling
        pass
```

### AgentScore Output

All agents return this structured output:

```python
class AgentScore(BaseModel):
    score: float           # 0-6 in 0.5 increments
    feedback: str          # Detailed feedback
    strengths: list[str]   # Specific strengths
    improvements: list[str] # Areas to improve (with examples)
    evidence: list[str]    # Quotes from essay
```

---

### Dimension Agents

#### 1. ThesisAgent

- Evaluates clarity and strength of position statement
- Checks if thesis directly addresses the prompt
- Looks for focused, debatable claims

#### 2. ReasoningAgent

- Evaluates logical argument structure
- Checks cause-and-effect relationships
- Identifies logical fallacies

#### 3. EvidenceAgent (with Tools)

- Evaluates quality of examples and evidence
- HAS ACCESS TO WEB SEARCH TOOLS:
  - `search_web(query)` - General web search
  - `fact_check_claim(claim, context)` - Verify specific claims
- Tracks fact checks performed

```python
class EvidenceAgent(BaseGradingAgent):
    def __init__(self, temperature: float = 0.3, model: str = None):
        super().__init__(dimension=GradingDimension.EVIDENCE, ...)
        self._tools = get_evidence_tools()
        self._agent_executor = self._build_agent_executor()

    def _build_agent_executor(self) -> AgentExecutor:
        """Creates OpenAI tools agent with Tavily search."""
        agent = create_openai_tools_agent(self.llm, self._tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self._tools,
            return_intermediate_steps=True,  # Track tool usage
        )

    async def evaluate(...) -> tuple[AgentScore, int]:
        """Returns (score, fact_check_count)"""
        pass
```

#### 4. StructureAgent

- Evaluates organization (intro, body, conclusion)
- Checks paragraph structure
- Looks for transitions

#### 5. AnalysisAgent

- Evaluates depth of thinking
- Checks for multiple perspectives
- Looks for implications/consequences

#### 6. LanguageAgent

- Evaluates vocabulary sophistication
- Checks sentence variety
- Assesses stylistic effectiveness

#### 7. GrammarAgent

- Evaluates grammatical correctness
- Checks punctuation and spelling
- Identifies mechanical errors

#### 8. CoherenceAgent

- Evaluates overall flow
- Checks idea connections
- Assesses persuasive power

---

### Grader (grader.py)

Orchestrates all 8 dimension agents for a single grading pass.

```python
class Grader:
    def __init__(
        self,
        grader_id: int,
        temperature: float = 0.3,
        model: Optional[str] = None,
    ):
        self.grader_id = grader_id
        self.temperature = temperature
        self.fact_checks_count = 0

        # Initialize all 8 agents with same temperature
        self.agents = {
            GradingDimension.THESIS: ThesisAgent(temperature=temperature),
            GradingDimension.REASONING: ReasoningAgent(temperature=temperature),
            # ... all 8 agents
        }

    async def grade(
        self,
        prompt: str,
        essay: str,
        weak_areas: Optional[list[str]] = None,
        session_context: Optional[str] = None,
    ) -> GraderResult:
        """Run all 8 agents in parallel."""

        # Parallel execution
        tasks = [
            self._evaluate_dimension(dim, agent, prompt, essay, ...)
            for dim, agent in self.agents.items()
        ]
        results = await asyncio.gather(*tasks)

        # Calculate weighted overall score
        overall_score = self._calculate_overall_score(dimension_scores)

        return GraderResult(
            grader_id=self.grader_id,
            dimension_scores=dimension_scores,
            overall_score=overall_score,
            overall_feedback=overall_feedback,
            fact_checks_count=self.fact_checks_count,
        )
```

---

### ConsensusAgent (consensus_agent.py)

Combines results from all 3 graders into final consensus.

```python
class ConsensusAgent:
    async def build_consensus(
        self,
        grader_results: list[GraderResult],
        weak_areas: Optional[list[WeakArea]] = None,
    ) -> ConsensusResult:

        # 1. Average scores per dimension (round to 0.5)
        dimension_scores = self._average_dimension_scores(grader_results)

        # 2. Calculate variance to identify disagreements
        score_variance = self._calculate_variance(grader_results)

        # 3. Find high-variance dimensions (variance > 1.5)
        high_variance = [dim for dim, var in score_variance.items() if var > 1.5]

        # 4. Calculate weighted overall score
        overall_score = self._calculate_overall_score(dimension_scores)

        # 5. Use LLM to merge feedback with examples
        merged_feedback = await self._merge_feedback(grader_results)

        # 6. Prioritize improvements based on weak areas
        improvements = self._prioritize_improvements(dimension_scores, weak_areas)

        return ConsensusResult(...)

    def _round_to_half(self, score: float) -> float:
        """Round to nearest 0.5 (GRE scale)."""
        return round(score * 2) / 2
```

---

## LangGraph Workflow

### State Definition (state.py)

```python
class GradingStateDict(TypedDict, total=False):
    student_id: str
    essay_prompt: str
    essay_text: str
    session_id: Optional[str]
    weak_areas: list[WeakArea]
    previous_scores: dict[str, list[float]]
    session_context: Optional[str]
    grader_results: Annotated[list[GraderResult], add]  # Accumulates
    consensus: Optional[ConsensusResult]
    fact_checks_performed: int
    total_grading_time_ms: int
    errors: Annotated[list[str], add]  # Accumulates
```

### Workflow Nodes (nodes.py)

```python
async def load_student_context(state: dict) -> dict:
    """Load weak areas and history from long-term memory."""
    memory = LongTermMemory()
    weak_areas = await memory.get_weak_areas(state["student_id"])
    previous_scores = await memory.get_dimension_history(state["student_id"])
    return {"weak_areas": weak_areas, "previous_scores": previous_scores}

async def run_all_graders(state: dict) -> dict:
    """Run 3 graders in parallel."""
    tasks = [run_grader(i, temps[i], state) for i in range(3)]
    results = await asyncio.gather(*tasks)
    return {"grader_results": all_results, "total_grading_time_ms": total_time}

async def build_consensus(state: dict) -> dict:
    """Build consensus from grader results."""
    consensus_agent = ConsensusAgent()
    consensus = await consensus_agent.build_consensus(
        state["grader_results"],
        state["weak_areas"],
    )
    return {"consensus": consensus}

async def update_memory(state: dict) -> dict:
    """Store results and update weak areas."""
    memory = LongTermMemory()
    await memory.store_grading_result(...)
    await memory.update_dimension_history(...)
    return {}
```

### Graph Definition (workflow.py)

```python
def create_grading_workflow() -> StateGraph:
    workflow = StateGraph(GradingStateDict)

    # Add nodes
    workflow.add_node("load_context", load_student_context)
    workflow.add_node("run_graders", run_all_graders)
    workflow.add_node("build_consensus", build_consensus)
    workflow.add_node("update_memory", update_memory)

    # Linear flow
    workflow.set_entry_point("load_context")
    workflow.add_edge("load_context", "run_graders")
    workflow.add_edge("run_graders", "build_consensus")
    workflow.add_edge("build_consensus", "update_memory")
    workflow.add_edge("update_memory", END)

    return workflow

# Compile once at startup
grading_app = compile_grading_workflow()

async def grade_essay(student_id, essay_prompt, essay_text, session_id=None):
    initial_state = {...}
    final_state = await grading_app.ainvoke(initial_state)
    return final_state
```

---

## Memory Systems

### Long-Term Memory (PostgreSQL)

```python
class LongTermMemory:
    async def get_weak_areas(self, student_id: str) -> list[WeakArea]:
        """Get dimensions with avg score < 4.0 over last 5 essays."""
        pass

    async def get_dimension_history(self, student_id: str) -> dict[str, list[float]]:
        """Get recent scores per dimension."""
        pass

    async def store_grading_result(
        self,
        student_id: str,
        essay_prompt: str,
        essay_text: str,
        consensus: ConsensusResult,
        grader_results: list[GraderResult],
    ) -> str:
        """Store essay and all grading data."""
        pass

    async def update_dimension_history(
        self,
        student_id: str,
        dimension_scores: list[DimensionScore],
    ) -> None:
        """Update running averages and trends."""
        pass

    def _calculate_trend(self, scores: list[float]) -> str:
        """Returns 'improving', 'declining', or 'stable'."""
        pass
```

### Database Models

```python
class Student(Base):
    id: str (PK)
    email: str
    name: str
    total_essays: int
    average_score: float
    created_at: datetime

class Essay(Base):
    id: str (PK)
    student_id: str (FK)
    prompt: str
    text: str
    word_count: int
    overall_score: float
    created_at: datetime

class EssayDimensionScore(Base):
    id: int (PK)
    essay_id: str (FK)
    dimension: str
    score: float
    feedback: str
    strengths: list[str]
    improvements: list[str]
    score_variance: float

class DimensionHistory(Base):
    id: int (PK)
    student_id: str (FK)
    dimension: str
    total_essays: int
    average_score: float
    recent_scores: list[float]  # Last N scores
    trend: str  # improving, stable, declining

class GradingResult(Base):
    id: int (PK)
    essay_id: str (FK)
    grader_id: int
    dimension_scores: dict
    overall_score: float
    overall_feedback: str
    temperature: float
    model_used: str
    grading_time_ms: int
```

---

## API Endpoints

### POST /api/v1/grading/grade

Grade an essay using the full multi-agent system.

Request:

```json
{
  "student_id": "student-123",
  "essay_prompt": "As people rely more on technology...",
  "essay_text": "Technology has become increasingly...",
  "session_id": "optional-session-id"
}
```

Response:

```json
{
    "request_id": "uuid",
    "student_id": "student-123",
    "timestamp": "2024-01-15T10:30:00Z",
    "grader_results": [
        {
            "grader_id": 0,
            "overall_score": 5.0,
            "dimension_scores": [...],
            "overall_feedback": "...",
            "fact_checks_count": 2
        },
        // ... graders 1 and 2
    ],
    "consensus": {
        "overall_score": 5.0,
        "dimension_scores": [...],
        "merged_feedback": "...",
        "score_variance": {"thesis": 0.3, ...},
        "high_variance_dimensions": [],
        "strengths": [...],
        "priority_improvements": [...]
    },
    "weak_areas": [...],
    "improvement_from_last": {"thesis": 0.5, ...},
    "total_grading_time_ms": 45000,
    "fact_checks_performed": 6
}
```

### POST /api/v1/grading/grade/quick

Quick grading with single grader (faster, less accurate).

### GET /api/v1/grading/dimensions

Get list of all 8 grading dimensions with descriptions.

### GET /api/v1/students/{student_id}/history

Get student's essay history.

### GET /api/v1/students/{student_id}/progress

Get student's progress and weak area analysis.

---

## Configuration

Environment variables (.env):

```bash
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# LangSmith (Monitoring)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls-...
LANGCHAIN_PROJECT=gre-grading-system

# Tavily (Fact-checking)
TAVILY_API_KEY=tvly-...

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/gre_grading

# Grading Config
NUM_GRADERS=3
GRADER_TEMPERATURES=[0.3, 0.5, 0.7]
WEAK_AREA_THRESHOLD=4.0
WEAK_AREA_LOOKBACK=5
```

---

## Rate Limit Handling

All LLM calls use exponential backoff retry:

```python
async def retry_with_backoff(func, max_retries=5, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if "rate_limit" in str(e).lower() or "429" in str(e):
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)
            else:
                raise
```

---

## Running the Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment
copy .env.example .env
# Edit .env with your API keys

# Start PostgreSQL (Docker)
docker run -d --name gre-postgres \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=gre_grading \
    -p 5432:5432 \
    pgvector/pgvector:pg16

# Run the server
python -m uvicorn app.main:app --reload --port 8000
```

Access:

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- LangSmith: https://smith.langchain.com
