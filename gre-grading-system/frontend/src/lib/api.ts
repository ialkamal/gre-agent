// API client for the GRE Grading System

import type {
  GradingRequest,
  GradingResponse,
  Student,
  StudentHistory,
  Essay,
  SamplePrompt,
  WeakArea,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// Grading endpoints
export async function gradeEssay(
  request: GradingRequest,
): Promise<GradingResponse> {
  return fetchAPI<GradingResponse>("/api/v1/grading/grade", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function quickGradeEssay(
  request: GradingRequest,
): Promise<{ grader_result: any; total_grading_time_ms: number }> {
  return fetchAPI("/api/v1/grading/grade/quick", {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getGradingDimensions(): Promise<{
  dimensions: Array<{
    id: string;
    name: string;
    description: string;
    weight: number;
  }>;
}> {
  return fetchAPI("/api/v1/grading/dimensions");
}

// Student endpoints
export async function createStudent(data: {
  email: string;
  name: string;
  target_score?: number;
}): Promise<Student> {
  return fetchAPI<Student>("/api/v1/students/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getStudent(studentId: string): Promise<Student> {
  return fetchAPI<Student>(`/api/v1/students/${studentId}`);
}

export async function getStudentHistory(
  studentId: string,
): Promise<StudentHistory> {
  return fetchAPI<StudentHistory>(`/api/v1/students/${studentId}/history`);
}

export async function getWeakAreas(studentId: string): Promise<{
  student_id: string;
  weak_areas: WeakArea[];
}> {
  return fetchAPI(`/api/v1/students/${studentId}/weak-areas`);
}

// History endpoints
export async function getStudentEssays(
  studentId: string,
  limit = 10,
  offset = 0,
): Promise<{
  student_id: string;
  essays: Essay[];
  total: number;
}> {
  return fetchAPI(
    `/api/v1/history/essays/${studentId}?limit=${limit}&offset=${offset}`,
  );
}

export async function getEssayDetails(essayId: string): Promise<any> {
  return fetchAPI(`/api/v1/history/essay/${essayId}`);
}

export async function getProgressData(
  studentId: string,
  dimension?: string,
): Promise<{
  student_id: string;
  total_essays: number;
  data: Array<{
    essay_id: string;
    date: string;
    overall_score: number;
    [key: string]: any;
  }>;
}> {
  const url = dimension
    ? `/api/v1/history/progress/${studentId}?dimension=${dimension}`
    : `/api/v1/history/progress/${studentId}`;
  return fetchAPI(url);
}

// Sample prompts
export async function getSamplePrompts(): Promise<{
  prompts: SamplePrompt[];
}> {
  return fetchAPI("/api/v1/sample-prompts");
}

// Health check
export async function checkHealth(): Promise<{
  status: string;
  langsmith_enabled: boolean;
  database_configured: boolean;
}> {
  return fetchAPI("/health");
}
