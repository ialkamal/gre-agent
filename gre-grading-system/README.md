# GRE Issue Writing Multi-Agent Grading System

A sophisticated multi-agent system built with LangChain and LangGraph for grading GRE Issue Writing essays. The system provides detailed feedback across 8 dimensions using 3 independent parallel graders that reach consensus.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Student Interface                             │
│                     (React/Next.js Frontend)                         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FastAPI Backend                              │
│              (Session Management, API Endpoints)                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                            │
│                                                                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│  │  Grader 1   │    │  Grader 2   │    │  Grader 3   │  (Parallel)  │
│  │  (8 agents) │    │  (8 agents) │    │  (8 agents) │              │
│  │  temp=0.3   │    │  temp=0.5   │    │  temp=0.7   │              │
│  └─────────────┘    └─────────────┘    └─────────────┘              │
│         │                  │                  │                      │
│         └──────────────────┼──────────────────┘                      │
│                            ▼                                         │
│                 ┌─────────────────────┐                              │
│                 │  Consensus Agent    │                              │
│                 │  (Average + Merge)  │                              │
│                 └─────────────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
                                  │
          ┌───────────────────────┴───────────────────────┐
          ▼                                               ▼
┌──────────────────────┐                    ┌──────────────────────┐
│   PostgreSQL + pgvector                   │      LangSmith       │
│   - Student profiles                      │   - Trace monitoring │
│   - Historical scores                     │   - Agent performance│
│   - Weak area tracking                    │   - Latency metrics  │
└──────────────────────┘                    └──────────────────────┘
```

## ✨ Features

### Multi-Agent Grading

- **3 Independent Graders**: Each with different temperature settings for grading diversity
- **8 Specialized Agents per Grader**: Each evaluates a specific dimension
- **Consensus Building**: Averages scores, identifies high-variance dimensions, merges feedback

### 8 Grading Dimensions

| #   | Dimension                    | Description                                           | Weight |
| --- | ---------------------------- | ----------------------------------------------------- | ------ |
| 1   | Clarity of Position (Thesis) | How clearly the writer establishes their position     | 1.2    |
| 2   | Quality of Reasoning         | Logical strength of arguments                         | 1.3    |
| 3   | Use of Evidence & Examples   | Quality and accuracy of evidence (with fact-checking) | 1.1    |
| 4   | Organization & Structure     | Essay structure and flow                              | 1.0    |
| 5   | Depth of Analysis            | Sophistication of analysis                            | 1.2    |
| 6   | Language Use & Style         | Vocabulary and style                                  | 1.0    |
| 7   | Grammar & Mechanics          | Grammatical correctness                               | 0.8    |
| 8   | Overall Coherence            | Persuasiveness and coherence                          | 1.1    |

### Memory Systems

- **Session Memory**: Maintains context within a grading session
- **Long-Term Memory**: Tracks student performance over time using PostgreSQL + pgvector
- **Weak Area Detection**: Automatically identifies dimensions that need improvement

### Tools

- **Tavily Web Search**: Evidence Agent can fact-check claims and examples
- **LangSmith Monitoring**: Full tracing of all agent interactions

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16 with pgvector extension
- Docker (optional)
- API Keys:
  - OpenAI API key
  - Tavily API key (for fact-checking)
  - LangSmith API key (for monitoring)

### Installation

1. **Clone and setup environment**

```bash
cd gre-grading-system/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start PostgreSQL** (with Docker)

```bash
docker run -d --name gre-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=gre_grading \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

4. **Run the API**

```bash
uvicorn app.main:app --reload
```

5. **Access the API**

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Using Docker Compose

```bash
# Set your API keys in environment
export OPENAI_API_KEY=your-key
export TAVILY_API_KEY=your-key
export LANGCHAIN_API_KEY=your-key

# Start all services
docker-compose up -d
```

## 📡 API Endpoints

### Grading

- `POST /api/v1/grading/grade` - Full grading with 3 parallel graders
- `POST /api/v1/grading/grade/quick` - Quick grading with single grader
- `GET /api/v1/grading/dimensions` - List all grading dimensions

### Students

- `POST /api/v1/students/` - Create new student
- `GET /api/v1/students/{id}` - Get student info
- `GET /api/v1/students/{id}/history` - Get grading history
- `GET /api/v1/students/{id}/weak-areas` - Get weak areas with recommendations

### History

- `GET /api/v1/history/essays/{student_id}` - List student's essays
- `GET /api/v1/history/essay/{essay_id}` - Get essay details
- `GET /api/v1/history/compare/{student_id}` - Compare multiple essays
- `GET /api/v1/history/progress/{student_id}` - Get progress chart data

## 📊 Example Request

```bash
curl -X POST http://localhost:8000/api/v1/grading/grade \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student-123",
    "essay_prompt": "As people rely more and more on technology to solve problems, the ability of humans to think for themselves will surely deteriorate.",
    "essay_text": "Technology has become an integral part of modern life..."
  }'
```

## 📈 LangSmith Monitoring

All agent interactions are traced to LangSmith for:

- Performance monitoring
- Debugging agent behavior
- Analyzing grading patterns
- Identifying bottlenecks

View traces at: https://smith.langchain.com

## 🗂️ Project Structure

```
gre-grading-system/
├── backend/
│   ├── app/
│   │   ├── agents/           # All grading agents
│   │   │   ├── grading_agents/  # 8 dimension agents
│   │   │   ├── base.py       # Base agent class
│   │   │   ├── grader.py     # Grader orchestrator
│   │   │   └── consensus_agent.py
│   │   ├── api/              # FastAPI routes
│   │   ├── graph/            # LangGraph workflow
│   │   ├── memory/           # Session & long-term memory
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── tools/            # Tavily web search
│   │   └── db/               # Database connection
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # Next.js frontend (to be built)
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

| Variable               | Description                      | Default                     |
| ---------------------- | -------------------------------- | --------------------------- |
| `OPENAI_API_KEY`       | OpenAI API key                   | Required                    |
| `OPENAI_MODEL`         | Model to use                     | gpt-4o                      |
| `TAVILY_API_KEY`       | Tavily API key for fact-checking | Required for evidence agent |
| `DATABASE_URL`         | PostgreSQL connection string     | See .env.example            |
| `LANGCHAIN_TRACING_V2` | Enable LangSmith tracing         | true                        |
| `LANGCHAIN_API_KEY`    | LangSmith API key                | Optional                    |
| `NUM_GRADERS`          | Number of parallel graders       | 3                           |
| `GRADER_TEMPERATURES`  | Temperature per grader           | [0.3, 0.5, 0.7]             |
| `WEAK_AREA_THRESHOLD`  | Score below which is "weak"      | 4.0                         |

## 📝 Scoring Scale

| Score | Level                   | Description                            |
| ----- | ----------------------- | -------------------------------------- |
| 6     | Outstanding             | Insightful, compelling, well-organized |
| 5     | Strong                  | Clear, logically sound, well-developed |
| 4     | Adequate                | Clear position, relevant support       |
| 3     | Limited                 | Vague analysis, weak development       |
| 2     | Seriously Flawed        | Little support, language problems      |
| 1     | Fundamentally Deficient | No clear position, severe issues       |
| 0     | Off-topic               | Does not address prompt                |

## 🛣️ Roadmap

- [x] Core grading agents
- [x] LangGraph workflow
- [x] Memory systems
- [x] FastAPI backend
- [ ] React/Next.js frontend
- [ ] Real-time progress via WebSocket
- [ ] Essay similarity search
- [ ] Practice mode with timed essays
- [ ] Detailed analytics dashboard

## 📄 License

MIT
