// Types for the GRE Grading System

export type GradingDimension =
  | "thesis"
  | "reasoning"
  | "evidence"
  | "structure"
  | "analysis"
  | "language"
  | "grammar"
  | "coherence";

export interface DimensionScore {
  dimension: GradingDimension;
  score: number;
  feedback: string;
  strengths: string[];
  improvements: string[];
}

export interface GraderResult {
  grader_id: number;
  dimension_scores: DimensionScore[];
  overall_score: number;
  overall_feedback: string;
  grading_time_ms: number;
  fact_checks_count: number;
}

export interface ConsensusResult {
  dimension_scores: DimensionScore[];
  overall_score: number;
  score_variance: Record<string, number>;
  high_variance_dimensions: GradingDimension[];
  merged_feedback: string;
  strengths: string[];
  priority_improvements: string[];
}

export interface WeakArea {
  dimension: GradingDimension;
  average_score: number;
  trend: "improving" | "declining" | "stable";
  recommendation: string;
}

export interface ModelEssay {
  model_essay: string;
  improvement_notes: string;
  word_count: number;
}

export interface GradingRequest {
  student_id: string;
  essay_prompt: string;
  essay_text: string;
  session_id?: string;
}

export interface GradingResponse {
  request_id: string;
  student_id: string;
  timestamp: string;
  grader_results: GraderResult[];
  consensus: ConsensusResult;
  weak_areas: WeakArea[];
  improvement_from_last: Record<string, number> | null;
  model_essay: ModelEssay | null;
  total_grading_time_ms: number;
  fact_checks_performed: number;
}

export interface Student {
  id: string;
  email: string;
  name: string;
  target_score: number | null;
  created_at: string;
  total_essays: number;
  average_score: number | null;
}

export interface StudentHistory {
  student_id: string;
  total_essays: number;
  average_overall_score: number;
  dimension_averages: Record<string, number>;
  weak_areas: WeakArea[];
  score_trend: number[];
  last_grading: string | null;
}

export interface Essay {
  id: string;
  prompt: string;
  text?: string;
  word_count: number;
  overall_score: number;
  created_at: string;
}

export interface SamplePrompt {
  id: number;
  prompt: string;
  instructions: string;
}

export const DIMENSION_LABELS: Record<GradingDimension, string> = {
  thesis: "Clarity of Position",
  reasoning: "Quality of Reasoning",
  evidence: "Evidence & Examples",
  structure: "Organization",
  analysis: "Depth of Analysis",
  language: "Language & Style",
  grammar: "Grammar & Mechanics",
  coherence: "Coherence & Persuasiveness",
};

export const SCORE_LABELS: Record<number, string> = {
  6: "Outstanding",
  5: "Strong",
  4: "Adequate",
  3: "Limited",
  2: "Seriously Flawed",
  1: "Fundamentally Deficient",
  0: "Off-topic",
};

export function getScoreColor(score: number): string {
  if (score >= 5.5) return "text-gre-outstanding";
  if (score >= 4.5) return "text-gre-strong";
  if (score >= 3.5) return "text-gre-adequate";
  if (score >= 2.5) return "text-gre-limited";
  if (score >= 1.5) return "text-gre-flawed";
  return "text-gre-deficient";
}

export function getScoreBgColor(score: number): string {
  if (score >= 5.5) return "bg-gre-outstanding";
  if (score >= 4.5) return "bg-gre-strong";
  if (score >= 3.5) return "bg-gre-adequate";
  if (score >= 2.5) return "bg-gre-limited";
  if (score >= 1.5) return "bg-gre-flawed";
  return "bg-gre-deficient";
}
