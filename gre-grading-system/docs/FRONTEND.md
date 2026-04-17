# Frontend Documentation

## Overview

The frontend is a Next.js 14 application providing a user interface for the GRE essay grading system. It allows students to submit essays, view detailed feedback, and track their progress over time.

## Directory Structure

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router pages
│   │   ├── layout.tsx               # Root layout with navigation
│   │   ├── page.tsx                 # Home page
│   │   ├── practice/
│   │   │   └── page.tsx             # Essay submission page
│   │   ├── results/
│   │   │   └── [id]/
│   │   │       └── page.tsx         # Individual result page
│   │   ├── history/
│   │   │   └── page.tsx             # Essay history list
│   │   └── progress/
│   │       └── page.tsx             # Progress tracking dashboard
│   │
│   ├── components/                   # Reusable React components
│   │   ├── Navigation.tsx           # Top navigation bar
│   │   ├── EssayEditor.tsx          # Essay input form
│   │   ├── GradingResults.tsx       # Full results display
│   │   ├── ScoreChart.tsx           # Radar chart for dimensions
│   │   └── ProgressChart.tsx        # Progress over time chart
│   │
│   ├── lib/                         # Utilities
│   │   ├── api.ts                   # API client functions
│   │   └── utils.ts                 # Helper functions
│   │
│   └── types/                       # TypeScript definitions
│       └── index.ts                 # All type definitions
│
├── public/                          # Static assets
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

---

## Pages

### Home Page (/)

Landing page with:

- System overview
- Quick start guide
- Feature highlights
- CTA to practice page

### Practice Page (/practice)

Essay submission interface:

- GRE prompt selector or custom prompt input
- Essay text editor with word count
- Student ID input
- Submit button with loading state
- Redirects to results page after grading

### Results Page (/results/[id])

Displays full grading results:

- Overall score with visual indicator
- Dimension scores radar chart
- Merged feedback section
- Individual dimension cards
- Priority improvements list
- Historical weak areas (if any)
- Improvement from last essay
- Collapsible individual grader results

### History Page (/history)

List of past essays:

- Essay prompt preview
- Submission date
- Overall score
- Link to full results
- Pagination

### Progress Page (/progress)

Progress tracking dashboard:

- Score trend chart over time
- Dimension average comparison
- Weak area analysis
- Improvement recommendations

---

## Components

### GradingResults.tsx

Main component for displaying grading results.

```typescript
interface GradingResultsProps {
    results: GradingResponse;
}

export default function GradingResults({ results }: GradingResultsProps) {
    const {
        consensus,
        grader_results,
        weak_areas,
        improvement_from_last,
        total_grading_time_ms,
        fact_checks_performed,
    } = results;

    return (
        <div className="space-y-8">
            {/* Overall Score Section */}
            <div className="bg-gradient-to-r from-primary-600 to-primary-800 ...">
                <div className="text-6xl font-bold">
                    {consensus.overall_score.toFixed(1)}
                </div>
                {/* Quick Stats: Time, Dimensions, Variance, Fact Checks */}
            </div>

            {/* Score Chart */}
            <ScoreChart scores={consensus.dimension_scores} />

            {/* Merged Feedback */}
            <div className="prose">
                {consensus.merged_feedback}
            </div>

            {/* Dimension Cards Grid */}
            <div className="grid md:grid-cols-2 gap-4">
                {consensus.dimension_scores.map((dim) => (
                    <DimensionCard key={dim.dimension} dimension={dim} />
                ))}
            </div>

            {/* Priority Improvements */}
            {/* Weak Areas from History */}
            {/* Improvement from Last Essay */}
            {/* Individual Grader Results (collapsed) */}
        </div>
    );
}
```

### DimensionCard Component

Displays score and feedback for a single dimension:

```typescript
function DimensionCard({ dimension }: { dimension: DimensionScore }) {
    return (
        <div className="bg-white border rounded-lg p-4">
            <div className="flex justify-between">
                <h4>{DIMENSION_LABELS[dimension.dimension]}</h4>
                <span className={getScoreColor(dimension.score)}>
                    {dimension.score.toFixed(1)}
                </span>
            </div>

            <p className="text-gray-600">{dimension.feedback}</p>

            {dimension.strengths.length > 0 && (
                <div className="text-green-600">
                    <p>✓ Strengths</p>
                    <ul>
                        {dimension.strengths.map((s, i) => <li key={i}>• {s}</li>)}
                    </ul>
                </div>
            )}

            {dimension.improvements.length > 0 && (
                <div className="text-orange-600">
                    <p>→ To Improve</p>
                    <ul>
                        {dimension.improvements.map((imp, i) => <li key={i}>• {imp}</li>)}
                    </ul>
                </div>
            )}
        </div>
    );
}
```

### ScoreChart.tsx

Radar chart showing all 8 dimension scores:

```typescript
interface ScoreChartProps {
  scores: DimensionScore[];
}

export default function ScoreChart({ scores }: ScoreChartProps) {
  // Uses Chart.js or similar for radar visualization
  // Displays all 8 dimensions on a 0-6 scale
  // Color-coded by score level
}
```

### EssayEditor.tsx

Essay input form with validation:

```typescript
interface EssayEditorProps {
    onSubmit: (data: GradingRequest) => Promise<void>;
    isLoading: boolean;
}

export default function EssayEditor({ onSubmit, isLoading }: EssayEditorProps) {
    const [prompt, setPrompt] = useState("");
    const [essay, setEssay] = useState("");
    const [studentId, setStudentId] = useState("");

    const wordCount = essay.split(/\s+/).filter(Boolean).length;

    return (
        <form onSubmit={handleSubmit}>
            {/* Prompt Input */}
            <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Enter GRE Issue prompt..."
            />

            {/* Essay Input */}
            <textarea
                value={essay}
                onChange={(e) => setEssay(e.target.value)}
                placeholder="Write your essay here..."
                minLength={50}
            />

            {/* Word Count */}
            <div className={wordCount < 50 ? "text-red-500" : "text-green-500"}>
                {wordCount} words
            </div>

            {/* Submit Button */}
            <button type="submit" disabled={isLoading || wordCount < 50}>
                {isLoading ? "Grading..." : "Submit for Grading"}
            </button>
        </form>
    );
}
```

### Navigation.tsx

Top navigation bar:

```typescript
export default function Navigation() {
    return (
        <nav className="bg-white shadow">
            <div className="flex justify-between items-center">
                <Link href="/">GRE Writing Tutor</Link>

                <div className="flex gap-4">
                    <Link href="/practice">Practice</Link>
                    <Link href="/history">History</Link>
                    <Link href="/progress">Progress</Link>
                </div>
            </div>
        </nav>
    );
}
```

---

## Types (types/index.ts)

```typescript
// Grading Dimensions
export type GradingDimension =
  | "thesis"
  | "reasoning"
  | "evidence"
  | "structure"
  | "analysis"
  | "language"
  | "grammar"
  | "coherence";

// Dimension Labels for Display
export const DIMENSION_LABELS: Record<GradingDimension, string> = {
  thesis: "Clarity of Position (Thesis)",
  reasoning: "Quality of Reasoning",
  evidence: "Use of Evidence & Examples",
  structure: "Organization & Structure",
  analysis: "Depth of Analysis",
  language: "Language Use & Style",
  grammar: "Grammar & Mechanics",
  coherence: "Overall Coherence & Persuasiveness",
};

// Score Labels
export const SCORE_LABELS: Record<number, string> = {
  6: "Outstanding",
  5: "Strong",
  4: "Adequate",
  3: "Limited",
  2: "Seriously Flawed",
  1: "Fundamentally Deficient",
  0: "Off Topic",
};

// Dimension Score
export interface DimensionScore {
  dimension: GradingDimension;
  score: number;
  feedback: string;
  strengths: string[];
  improvements: string[];
}

// Grader Result
export interface GraderResult {
  grader_id: number;
  dimension_scores: DimensionScore[];
  overall_score: number;
  overall_feedback: string;
  grading_time_ms: number;
  fact_checks_count: number;
}

// Consensus Result
export interface ConsensusResult {
  dimension_scores: DimensionScore[];
  overall_score: number;
  score_variance: Record<string, number>;
  high_variance_dimensions: GradingDimension[];
  merged_feedback: string;
  strengths: string[];
  priority_improvements: string[];
}

// Weak Area
export interface WeakArea {
  dimension: GradingDimension;
  average_score: number;
  trend: "improving" | "declining" | "stable";
  recommendation: string;
}

// API Request
export interface GradingRequest {
  student_id: string;
  essay_prompt: string;
  essay_text: string;
  session_id?: string;
}

// API Response
export interface GradingResponse {
  request_id: string;
  student_id: string;
  timestamp: string;
  grader_results: GraderResult[];
  consensus: ConsensusResult;
  weak_areas: WeakArea[];
  improvement_from_last: Record<string, number> | null;
  total_grading_time_ms: number;
  fact_checks_performed: number;
}

// Helper Functions
export function getScoreColor(score: number): string {
  if (score >= 5) return "text-green-600";
  if (score >= 4) return "text-blue-600";
  if (score >= 3) return "text-yellow-600";
  return "text-red-600";
}

export function getScoreBgColor(score: number): string {
  if (score >= 5) return "bg-green-600";
  if (score >= 4) return "bg-blue-600";
  if (score >= 3) return "bg-yellow-600";
  return "bg-red-600";
}
```

---

## API Client (lib/api.ts)

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function gradeEssay(
  request: GradingRequest,
): Promise<GradingResponse> {
  const response = await fetch(`${API_BASE}/api/v1/grading/grade`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Grading failed");
  }

  return response.json();
}

export async function getStudentHistory(studentId: string): Promise<Essay[]> {
  const response = await fetch(
    `${API_BASE}/api/v1/students/${studentId}/history`,
  );
  return response.json();
}

export async function getStudentProgress(studentId: string): Promise<Progress> {
  const response = await fetch(
    `${API_BASE}/api/v1/students/${studentId}/progress`,
  );
  return response.json();
}

export async function getGradingDimensions(): Promise<Dimension[]> {
  const response = await fetch(`${API_BASE}/api/v1/grading/dimensions`);
  const data = await response.json();
  return data.dimensions;
}
```

---

## Utilities (lib/utils.ts)

```typescript
// Format milliseconds to human-readable time
export function formatTime(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  const seconds = Math.floor(ms / 1000);
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}m ${remainingSeconds}s`;
}

// Format date
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Truncate text
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "...";
}

// Calculate word count
export function wordCount(text: string): number {
  return text.split(/\s+/).filter(Boolean).length;
}
```

---

## Styling

Uses Tailwind CSS with custom configuration:

```javascript
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0f9ff",
          100: "#e0f2fe",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
          800: "#075985",
          900: "#0c4a6e",
        },
      },
    },
  },
  plugins: [require("@tailwindcss/typography"), require("@tailwindcss/forms")],
};
```

---

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Running the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build
npm start
```

Access: http://localhost:3000

---

## User Flow

```
1. Home Page
   │
   ├── Click "Start Practicing"
   │
   ▼
2. Practice Page
   │
   ├── Enter/Select GRE prompt
   ├── Write essay (min 50 words)
   ├── Enter student ID
   ├── Click "Submit for Grading"
   │
   ├── [Loading: 30-60 seconds]
   │
   ▼
3. Results Page
   │
   ├── View overall score
   ├── See dimension breakdown
   ├── Read detailed feedback
   ├── Check priority improvements
   │
   ├── Click "Practice Again" → Back to Step 2
   ├── Click "View History" → Step 4
   │
   ▼
4. History Page
   │
   ├── See all past essays
   ├── Click any essay → Back to Step 3
   │
   ├── Click "View Progress" → Step 5
   │
   ▼
5. Progress Page
   │
   ├── View score trends
   ├── See weak area analysis
   ├── Get improvement recommendations
   │
   └── Click "Practice" → Back to Step 2
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Home    │ →  │ Practice │ →  │ Results  │ →  │ History  │  │
│  └──────────┘    └────┬─────┘    └────┬─────┘    └──────────┘  │
│                       │               │                          │
└───────────────────────┼───────────────┼──────────────────────────┘
                        │               │
                        ▼               ▼
              ┌─────────────────────────────────────┐
              │          API Client (api.ts)         │
              │                                      │
              │  gradeEssay()  getHistory()  etc.   │
              └─────────────────┬───────────────────┘
                                │
                                │ HTTP/JSON
                                ▼
              ┌─────────────────────────────────────┐
              │       Backend API (FastAPI)          │
              │                                      │
              │  POST /api/v1/grading/grade          │
              │  GET  /api/v1/students/:id/history   │
              └─────────────────────────────────────┘
```
