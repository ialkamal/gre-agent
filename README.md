# GRE Issue Writing Multi-Agent Grading System

An AI-powered multi-agent system that grades GRE Issue Writing essays using LangChain and LangGraph. Three independent graders — each running 8 specialized dimension agents — evaluate essays in parallel, then a consensus agent merges their results into a single score with detailed feedback.

## Architecture

```
                         ┌──────────────────────┐
                         │   Next.js Frontend    │
                         │   (React + Tailwind)  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   FastAPI Backend     │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ▼                     ▼                     ▼
       ┌────────────┐       ┌────────────┐       ┌────────────┐
       │  Grader 0  │       │  Grader 1  │       │  Grader 2  │
       │  temp=0.3  │       │  temp=0.5  │       │  temp=0.7  │
       │ (8 agents) │       │ (8 agents) │       │ (8 agents) │
       └─────┬──────┘       └─────┬──────┘       └─────┬──────┘
             └─────────────────────┼─────────────────────┘
                                   ▼
                        ┌─────────────────────┐
                        │  Consensus Agent    │
                        └─────────┬───────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  ▼                               ▼
       ┌──────────────────┐            ┌──────────────────┐
       │ PostgreSQL +     │            │ LangSmith        │
       │ pgvector         │            │ Tracing          │
       └──────────────────┘            └──────────────────┘
```

## Features

- **3 Parallel Graders** with different temperature settings for scoring diversity
- **8 Grading Dimensions** per grader (24 specialized agents total):
  - Clarity of Position (Thesis) · Quality of Reasoning · Use of Evidence & Examples · Organization & Structure · Depth of Analysis · Language Use & Style · Grammar & Mechanics · Overall Coherence
- **Consensus Building** — averages scores, detects high variance, merges feedback
- **Fact-Checking** — the Evidence Agent uses Tavily web search to verify claims
- **Model Essay Generation** — produces a score-6 rewrite with improvement notes
- **Long-Term Memory** — tracks student performance over time via PostgreSQL + pgvector
- **Weak Area Detection** — automatically identifies dimensions needing improvement
- **Session Memory** — maintains context within a grading session

## Tech Stack

| Layer        | Technology                          |
| ------------ | ----------------------------------- |
| Frontend     | Next.js 14, React 18, Tailwind CSS |
| Backend      | FastAPI, Pydantic, Uvicorn          |
| AI Framework | LangChain, LangGraph, OpenAI GPT-4o |
| Database     | PostgreSQL 16 + pgvector            |
| Search Tool  | Tavily API                          |
| Monitoring   | LangSmith                           |
| Infra        | Docker Compose                      |

## Project Structure

```
gre-grading-system/
├── backend/
│   └── app/
│       ├── agents/              # Grader, consensus, model essay generator
│       │   └── grading_agents/  # 8 dimension-specific agents
│       ├── api/routes/          # FastAPI endpoints (grading, history, students)
│       ├── db/                  # SQLAlchemy async database layer
│       ├── graph/               # LangGraph workflow (nodes, state, orchestration)
│       ├── memory/              # Session + long-term memory managers
│       ├── models/              # ORM models (Student, Essay, GradingResult)
│       ├── schemas/             # Pydantic request/response schemas
│       └── tools/               # Web search tool for fact-checking
├── frontend/
│   └── src/
│       ├── app/                 # Next.js pages (practice, results, history, progress)
│       ├── components/          # UI components (EssayEditor, ScoreChart, etc.)
│       ├── lib/                 # API client and utilities
│       └── types/               # TypeScript type definitions
├── docs/                        # Architecture, backend, and frontend documentation
├── docker-compose.yml           # Full-stack orchestration
└── gre_labeled_dataset.csv      # Labeled essay dataset
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 16 with pgvector extension
- Docker (optional, for containerized setup)
- API Keys: **OpenAI**, **Tavily**, **LangSmith**

### Option 1 — Docker Compose (recommended)

```bash
cd gre-grading-system

# Set your API keys
export OPENAI_API_KEY=your-key
export TAVILY_API_KEY=your-key
export LANGCHAIN_API_KEY=your-key

docker compose up --build
```

The frontend will be available at `http://localhost:3000` and the API at `http://localhost:8000`.

### Option 2 — Manual Setup

**Backend:**

```bash
cd gre-grading-system/backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Fill in your API keys
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd gre-grading-system/frontend
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint                              | Description                          |
| ------ | ------------------------------------- | ------------------------------------ |
| POST   | `/api/v1/grading/grade`               | Full grading (3 graders + consensus) |
| POST   | `/api/v1/grading/grade/quick`         | Quick grading (single grader)        |
| GET    | `/api/v1/history/essays/{student_id}` | Student's essay history              |
| GET    | `/api/v1/history/essay/{essay_id}`    | Detailed essay results               |
| GET    | `/api/v1/students/{student_id}`       | Student profile                      |
| GET    | `/api/v1/students/{id}/history`       | Performance history + weak areas     |

## Scoring

Essays are scored on the GRE scale (0–6 in 0.5 increments). Each dimension has a weight that influences the overall score:

| Weight | Dimensions                         |
| ------ | ---------------------------------- |
| 1.3    | Quality of Reasoning               |
| 1.2    | Clarity of Position, Depth of Analysis |
| 1.1    | Use of Evidence, Overall Coherence |
| 1.0    | Organization & Structure, Language Use |
| 0.8    | Grammar & Mechanics                |

## License

This project is for educational and research purposes.
