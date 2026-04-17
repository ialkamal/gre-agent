"use client";

import { useState, useEffect } from "react";
import EssayEditor from "@/components/EssayEditor";
import GradingResults from "@/components/GradingResults";
import { gradeEssay, getSamplePrompts } from "@/lib/api";
import type { GradingResponse, SamplePrompt } from "@/types";

// Demo student ID (in production, this would come from auth)
const DEMO_STUDENT_ID = "demo-student-001";

export default function PracticePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<GradingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [prompts, setPrompts] = useState<SamplePrompt[]>([]);

  useEffect(() => {
    // Load sample prompts
    getSamplePrompts()
      .then((data) => setPrompts(data.prompts))
      .catch((err) => console.error("Failed to load prompts:", err));
  }, []);

  const handleSubmit = async (prompt: string, essay: string) => {
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await gradeEssay({
        student_id: DEMO_STUDENT_ID,
        essay_prompt: prompt,
        essay_text: essay,
      });
      setResults(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Grading failed. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Practice GRE Issue Writing
        </h1>
        <p className="text-gray-600">
          Select a prompt, write your essay, and get detailed feedback from our
          AI grading system.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          <p className="font-medium">Error</p>
          <p>{error}</p>
        </div>
      )}

      {!results ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <EssayEditor
            onSubmit={handleSubmit}
            isLoading={isLoading}
            samplePrompts={prompts}
          />
        </div>
      ) : (
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Your Results</h2>
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
            >
              ✏️ Write Another Essay
            </button>
          </div>
          <GradingResults results={results} />
        </div>
      )}

      {/* Tips Section */}
      {!results && !isLoading && (
        <div className="mt-8 bg-blue-50 rounded-xl p-6 border border-blue-100">
          <h3 className="font-semibold text-blue-800 mb-3">
            💡 Tips for a High Score
          </h3>
          <ul className="space-y-2 text-blue-700 text-sm">
            <li>
              • <strong>Take a clear position</strong> in your opening paragraph
            </li>
            <li>
              • <strong>Use specific examples</strong> from history, current
              events, or personal experience
            </li>
            <li>
              • <strong>Address counterarguments</strong> to show depth of
              analysis
            </li>
            <li>
              • <strong>Organize your essay</strong> with clear paragraphs and
              transitions
            </li>
            <li>
              • <strong>Aim for 400-600 words</strong> to fully develop your
              ideas
            </li>
            <li>
              • <strong>Leave time to proofread</strong> for grammar and clarity
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}
