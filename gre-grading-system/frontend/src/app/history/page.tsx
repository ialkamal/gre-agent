"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { getStudentEssays, getStudentHistory } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { getScoreColor, SCORE_LABELS } from "@/types";
import type { Essay, StudentHistory } from "@/types";

const DEMO_STUDENT_ID = "demo-student-001";

export default function HistoryPage() {
  const [essays, setEssays] = useState<Essay[]>([]);
  const [history, setHistory] = useState<StudentHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [essaysData, historyData] = await Promise.all([
          getStudentEssays(DEMO_STUDENT_ID, 20),
          getStudentHistory(DEMO_STUDENT_ID),
        ]);
        setEssays(essaysData.essays);
        setHistory(historyData);
      } catch (err) {
        setError("Failed to load history. Make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading your history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800 font-medium">{error}</p>
          <p className="text-yellow-700 text-sm mt-2">
            Start by writing your first essay on the Practice page.
          </p>
          <Link
            href="/practice"
            className="inline-block mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg"
          >
            Go to Practice
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">
        Your Essay History
      </h1>
      <p className="text-gray-600 mb-8">
        Review your past essays and track your improvement over time.
      </p>

      {/* Summary Stats */}
      {history && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="text-3xl font-bold text-primary-600">
              {history.total_essays}
            </div>
            <div className="text-sm text-gray-600">Essays Written</div>
          </div>
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div
              className={`text-3xl font-bold ${getScoreColor(history.average_overall_score)}`}
            >
              {history.average_overall_score.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600">Average Score</div>
          </div>
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="text-3xl font-bold text-orange-600">
              {history.weak_areas.length}
            </div>
            <div className="text-sm text-gray-600">Weak Areas</div>
          </div>
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <div className="text-3xl font-bold text-green-600">
              {history.score_trend.length > 1
                ? history.score_trend[history.score_trend.length - 1] -
                    history.score_trend[0] >
                  0
                  ? "↑"
                  : "↓"
                : "-"}
            </div>
            <div className="text-sm text-gray-600">Trend</div>
          </div>
        </div>
      )}

      {/* Essays List */}
      {essays.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <p className="text-gray-600 mb-4">
            You haven't written any essays yet.
          </p>
          <Link
            href="/practice"
            className="inline-block px-6 py-2 bg-primary-600 text-white rounded-lg"
          >
            Write Your First Essay
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {essays.map((essay) => (
            <Link
              key={essay.id}
              href={`/results/${essay.id}`}
              className="block bg-white rounded-lg p-6 border border-gray-200 hover:border-primary-300 hover:shadow-sm transition"
            >
              <div className="flex justify-between items-start gap-4">
                <div className="flex-1">
                  <p className="text-gray-800 line-clamp-2">{essay.prompt}</p>
                  <div className="flex gap-4 mt-2 text-sm text-gray-500">
                    <span>{formatDate(essay.created_at)}</span>
                    <span>{essay.word_count} words</span>
                  </div>
                </div>
                <div className="text-right">
                  <div
                    className={`text-2xl font-bold ${getScoreColor(essay.overall_score)}`}
                  >
                    {essay.overall_score.toFixed(1)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {SCORE_LABELS[Math.round(essay.overall_score)]}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
