"use client";

import { useState, useEffect } from "react";
import { getProgressData, getStudentHistory } from "@/lib/api";
import ProgressChart from "@/components/ProgressChart";
import { DIMENSION_LABELS, getScoreColor } from "@/types";
import type { GradingDimension, StudentHistory, WeakArea } from "@/types";

const DEMO_STUDENT_ID = "demo-student-001";

const ALL_DIMENSIONS: GradingDimension[] = [
  "thesis",
  "reasoning",
  "evidence",
  "structure",
  "analysis",
  "language",
  "grammar",
  "coherence",
];

export default function ProgressPage() {
  const [progressData, setProgressData] = useState<any[]>([]);
  const [history, setHistory] = useState<StudentHistory | null>(null);
  const [selectedDimensions, setSelectedDimensions] = useState<
    GradingDimension[]
  >([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [progress, hist] = await Promise.all([
          getProgressData(DEMO_STUDENT_ID),
          getStudentHistory(DEMO_STUDENT_ID),
        ]);
        setProgressData(progress.data);
        setHistory(hist);
      } catch (err) {
        setError(
          "Failed to load progress data. Make sure the backend is running.",
        );
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const toggleDimension = (dim: GradingDimension) => {
    setSelectedDimensions((prev) =>
      prev.includes(dim) ? prev.filter((d) => d !== dim) : [...prev, dim],
    );
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading progress...</p>
      </div>
    );
  }

  if (error || progressData.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800 font-medium">
            {error ||
              "No progress data yet. Write some essays to see your progress!"}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Progress</h1>
      <p className="text-gray-600 mb-8">
        Track how your scores have improved over time across all dimensions.
      </p>

      {/* Main Progress Chart */}
      <div className="bg-white rounded-xl p-6 border border-gray-200 mb-8">
        <h2 className="text-lg font-semibold mb-4">Score Progress Over Time</h2>
        <ProgressChart
          data={progressData}
          selectedDimensions={selectedDimensions}
        />

        {/* Dimension Toggles */}
        <div className="mt-4 pt-4 border-t border-gray-100">
          <p className="text-sm text-gray-500 mb-2">Show dimensions:</p>
          <div className="flex flex-wrap gap-2">
            {ALL_DIMENSIONS.map((dim) => (
              <button
                key={dim}
                onClick={() => toggleDimension(dim)}
                className={`px-3 py-1 text-sm rounded-full transition ${
                  selectedDimensions.includes(dim)
                    ? "bg-primary-100 text-primary-700 border border-primary-300"
                    : "bg-gray-100 text-gray-600 border border-gray-200"
                }`}
              >
                {DIMENSION_LABELS[dim]}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Dimension Averages */}
      {history && (
        <div className="bg-white rounded-xl p-6 border border-gray-200 mb-8">
          <h2 className="text-lg font-semibold mb-4">Dimension Averages</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(history.dimension_averages).map(([dim, avg]) => (
              <div key={dim} className="text-center">
                <div className={`text-2xl font-bold ${getScoreColor(avg)}`}>
                  {avg.toFixed(1)}
                </div>
                <div className="text-xs text-gray-600">
                  {DIMENSION_LABELS[dim as GradingDimension] || dim}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Weak Areas */}
      {history && history.weak_areas.length > 0 && (
        <div className="bg-orange-50 rounded-xl p-6 border border-orange-200">
          <h2 className="text-lg font-semibold text-orange-800 mb-4">
            🎯 Areas to Focus On
          </h2>
          <div className="space-y-4">
            {history.weak_areas.map((wa: WeakArea) => (
              <div
                key={wa.dimension}
                className="bg-white rounded-lg p-4 border border-orange-100"
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-gray-800">
                    {DIMENSION_LABELS[wa.dimension]}
                  </span>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 text-xs rounded ${
                        wa.trend === "improving"
                          ? "bg-green-100 text-green-700"
                          : wa.trend === "declining"
                            ? "bg-red-100 text-red-700"
                            : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {wa.trend === "improving"
                        ? "↑ Improving"
                        : wa.trend === "declining"
                          ? "↓ Declining"
                          : "→ Stable"}
                    </span>
                    <span
                      className={`font-bold ${getScoreColor(wa.average_score)}`}
                    >
                      {wa.average_score.toFixed(1)}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-600">{wa.recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
