# GRE Multi-Agent Grading System Architecture

## Overview

This system uses a multi-agent architecture built with LangChain and LangGraph to grade GRE Issue Writing essays. It employs 3 independent graders, each containing 8 specialized agents, followed by a consensus-building phase.

```
                                    ┌─────────────────────────────────────┐
                                    │          Student Essay              │
                                    └─────────────────┬───────────────────┘
                                                      │
                                                      ▼
                                    ┌─────────────────────────────────────┐
                                    │     Load Student Context            │
                                    │  (Weak Areas, Previous Scores)      │
                                    └─────────────────┬───────────────────┘
                                                      │
                          ┌───────────────────────────┼───────────────────────────┐
                          │                           │                           │
                          ▼                           ▼                           ▼
              ┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
              │     Grader 1      │       │     Grader 2      │       │     Grader 3      │
              │   (temp=0.3)      │       │   (temp=0.5)      │       │   (temp=0.7)      │
              │                   │       │                   │       │                   │
              │  ┌─────────────┐  │       │  ┌─────────────┐  │       │  ┌─────────────┐  │
              │  │ 8 Dimension │  │       │  │ 8 Dimension │  │       │  │ 8 Dimension │  │
              │  │   Agents    │  │       │  │   Agents    │  │       │  │   Agents    │  │
              │  └─────────────┘  │       │  └─────────────┘  │       │  └─────────────┘  │
              └─────────┬─────────┘       └─────────┬─────────┘       └─────────┬─────────┘
                        │                           │                           │
                        └───────────────────────────┼───────────────────────────┘
                                                    │
                                                    ▼
                                    ┌─────────────────────────────────────┐
                                    │        Consensus Agent              │
                                    │   - Average scores                  │
                                    │   - Merge feedback                  │
                                    │   - Identify high variance          │
                                    └─────────────────┬───────────────────┘
                                                      │
                                                      ▼
                                    ┌─────────────────────────────────────┐
                                    │        Update Memory                │
                                    │   - Store results                   │
                                    │   - Update weak areas               │
                                    └─────────────────────────────────────┘
```

## Agent Hierarchy

### Level 1: Graders (3 instances)

Each grader operates with a different temperature to provide diverse perspectives:

| Grader   | Temperature | Behavior                       |
| -------- | ----------- | ------------------------------ |
| Grader 0 | 0.3         | More deterministic, consistent |
| Grader 1 | 0.5         | Balanced                       |
| Grader 2 | 0.7         | More creative, varied          |

### Level 2: Dimension Agents (8 per grader = 24 total)

Each grader contains 8 specialized agents, one for each GRE scoring dimension:

| #   | Dimension                          | Agent Class      | Weight | Has Tools        |
| --- | ---------------------------------- | ---------------- | ------ | ---------------- |
| 1   | Clarity of Position (Thesis)       | `ThesisAgent`    | 1.2    | No               |
| 2   | Quality of Reasoning               | `ReasoningAgent` | 1.3    | No               |
| 3   | Use of Evidence & Examples         | `EvidenceAgent`  | 1.1    | Yes (Web Search) |
| 4   | Organization & Structure           | `StructureAgent` | 1.0    | No               |
| 5   | Depth of Analysis                  | `AnalysisAgent`  | 1.2    | No               |
| 6   | Language Use & Style               | `LanguageAgent`  | 1.0    | No               |
| 7   | Grammar & Mechanics                | `GrammarAgent`   | 0.8    | No               |
| 8   | Overall Coherence & Persuasiveness | `CoherenceAgent` | 1.1    | No               |

### Level 3: Consensus Agent

The `ConsensusAgent` combines results from all 3 graders:

- Averages scores per dimension (rounded to 0.5 increments)
- Calculates score variance to identify disagreements
- Uses LLM to merge feedback into coherent guidance
- Prioritizes improvements based on historical weak areas

## Scoring System

### GRE Scale (0-6 in 0.5 increments)

| Score | Label                   |
| ----- | ----------------------- |
| 6.0   | Outstanding             |
| 5.5   | Strong+                 |
| 5.0   | Strong                  |
| 4.5   | Adequate+               |
| 4.0   | Adequate                |
| 3.5   | Limited+                |
| 3.0   | Limited                 |
| 2.5   | Flawed+                 |
| 2.0   | Seriously Flawed        |
| 1.5   | Deficient+              |
| 1.0   | Fundamentally Deficient |
| 0.0   | Off Topic/Blank         |

### Weighted Overall Score

```python
weights = {
    "reasoning": 1.3,    # Highest weight
    "thesis": 1.2,
    "analysis": 1.2,
    "evidence": 1.1,
    "coherence": 1.1,
    "structure": 1.0,
    "language": 1.0,
    "grammar": 0.8,      # Lowest weight
}
```

## Key Technologies

| Component              | Technology            |
| ---------------------- | --------------------- |
| LLM Framework          | LangChain 0.1.9       |
| Workflow Orchestration | LangGraph             |
| Monitoring             | LangSmith             |
| LLM                    | OpenAI GPT-4o         |
| Web Search             | Tavily API            |
| Backend Framework      | FastAPI               |
| Database               | PostgreSQL + pgvector |
| Frontend Framework     | Next.js 14            |
| Styling                | Tailwind CSS          |
