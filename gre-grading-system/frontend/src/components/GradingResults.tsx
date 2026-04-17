"use client";

import type { GradingResponse, DimensionScore } from "@/types";
import {
  DIMENSION_LABELS,
  getScoreColor,
  getScoreBgColor,
  SCORE_LABELS,
} from "@/types";
import { formatTime } from "@/lib/utils";
import ScoreChart from "./ScoreChart";

interface GradingResultsProps {
  results: GradingResponse;
}

interface ImprovementExample {
  area: string;
  tip: string;
  before: string;
  after: string;
}

// Parse the structured feedback to extract before/after examples
function parseImprovements(feedback: string): {
  mainFeedback: string;
  improvements: ImprovementExample[];
} {
  const improvements: ImprovementExample[] = [];
  
  // Extract all [IMPROVEMENT]...[/IMPROVEMENT] blocks
  const improvementRegex = /\[IMPROVEMENT\]([\s\S]*?)\[\/IMPROVEMENT\]/g;
  let match;
  
  while ((match = improvementRegex.exec(feedback)) !== null) {
    const block = match[1];
    
    // Parse the block
    const areaMatch = block.match(/Area:\s*(.+?)(?:\n|$)/);
    const tipMatch = block.match(/Tip:\s*(.+?)(?:\n|$)/);
    const beforeMatch = block.match(/\[BEFORE\]([\s\S]*?)\[AFTER\]/);
    const afterMatch = block.match(/\[AFTER\]([\s\S]*?)$/);
    
    if (areaMatch && tipMatch && beforeMatch && afterMatch) {
      improvements.push({
        area: areaMatch[1].trim(),
        tip: tipMatch[1].trim(),
        before: beforeMatch[1].trim(),
        after: afterMatch[1].trim(),
      });
    }
  }
  
  // Remove improvement blocks from main feedback
  const mainFeedback = feedback
    .replace(improvementRegex, '')
    .replace(/Priority Areas for Improvement:\s*\n*/g, '')
    .trim();
  
  return { mainFeedback, improvements };
}

function BeforeAfterCard({ improvement }: { improvement: ImprovementExample }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="bg-gradient-to-r from-orange-500 to-orange-600 px-4 py-2">
        <h4 className="font-semibold text-white">{improvement.area}</h4>
        <p className="text-orange-100 text-sm">{improvement.tip}</p>
      </div>
      
      <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-gray-200">
        {/* Before */}
        <div className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="bg-red-100 text-red-700 text-xs font-semibold px-2 py-1 rounded">
              BEFORE
            </span>
          </div>
          <p className="text-gray-600 text-sm italic leading-relaxed">
            "{improvement.before}"
          </p>
        </div>
        
        {/* After */}
        <div className="p-4 bg-green-50">
          <div className="flex items-center gap-2 mb-2">
            <span className="bg-green-100 text-green-700 text-xs font-semibold px-2 py-1 rounded">
              AFTER
            </span>
            <span className="text-green-600 text-xs">✓ Improved</span>
          </div>
          <p className="text-gray-700 text-sm leading-relaxed">
            "{improvement.after}"
          </p>
        </div>
      </div>
    </div>
  );
}

function ScoreBadge({ score }: { score: number }) {
  const roundedScore = Math.round(score);
  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1 rounded-full ${getScoreBgColor(score)} text-white`}
    >
      <span className="font-bold">{score.toFixed(1)}</span>
      <span className="text-sm opacity-90">
        {SCORE_LABELS[roundedScore] || ""}
      </span>
    </div>
  );
}

function DimensionCard({ dimension }: { dimension: DimensionScore }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
      <div className="flex justify-between items-center">
        <h4 className="font-medium text-gray-800">
          {DIMENSION_LABELS[dimension.dimension]}
        </h4>
        <span
          className={`text-2xl font-bold ${getScoreColor(dimension.score)}`}
        >
          {dimension.score.toFixed(1)}
        </span>
      </div>

      <p className="text-sm text-gray-600">{dimension.feedback}</p>

      {dimension.strengths.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-green-700 mb-1">
            ✓ Strengths
          </p>
          <ul className="text-xs text-green-600 space-y-1">
            {dimension.strengths.map((s, i) => (
              <li key={i}>• {s}</li>
            ))}
          </ul>
        </div>
      )}

      {dimension.improvements.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-orange-700 mb-1">
            → To Improve
          </p>
          <ul className="text-xs text-orange-600 space-y-1">
            {dimension.improvements.map((imp, i) => (
              <li key={i}>• {imp}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default function GradingResults({ results }: GradingResultsProps) {
  const {
    consensus,
    grader_results,
    weak_areas,
    improvement_from_last,
    total_grading_time_ms,
  } = results;

  // Parse the merged feedback to extract structured improvements
  const { mainFeedback, improvements } = parseImprovements(consensus.merged_feedback);

  return (
    <div className="space-y-8">
      {/* Overall Score Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-xl p-8 text-white">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          <div>
            <h2 className="text-2xl font-bold mb-2">
              Your GRE Issue Writing Score
            </h2>
            <p className="text-primary-100">
              Based on consensus from {grader_results.length} independent
              graders
            </p>
          </div>
          <div className="text-center">
            <div className="text-6xl font-bold">
              {consensus.overall_score.toFixed(1)}
            </div>
            <div className="text-primary-200">out of 6.0</div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-primary-500">
          <div>
            <div className="text-primary-200 text-sm">Grading Time</div>
            <div className="font-semibold">
              {formatTime(total_grading_time_ms)}
            </div>
          </div>
          <div>
            <div className="text-primary-200 text-sm">Dimensions Evaluated</div>
            <div className="font-semibold">8</div>
          </div>
          <div>
            <div className="text-primary-200 text-sm">Score Variance</div>
            <div className="font-semibold">
              {consensus.high_variance_dimensions.length > 0
                ? `${consensus.high_variance_dimensions.length} high`
                : "Low"}
            </div>
          </div>
          <div>
            <div className="text-primary-200 text-sm">Fact Checks</div>
            <div className="font-semibold">{results.fact_checks_performed}</div>
          </div>
        </div>
      </div>

      {/* Score Chart */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Dimension Scores</h3>
        <ScoreChart scores={consensus.dimension_scores} />
      </div>

      {/* Merged Feedback */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">📝 Detailed Feedback</h3>
        <div className="prose max-w-none text-gray-700 whitespace-pre-wrap">
          {mainFeedback}
        </div>
      </div>

      {/* Before/After Improvement Examples */}
      {improvements.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">
            🎯 Priority Improvements with Examples
          </h3>
          <div className="space-y-4">
            {improvements.map((improvement, i) => (
              <BeforeAfterCard key={i} improvement={improvement} />
            ))}
          </div>
        </div>
      )}

      {/* Dimension Cards Grid */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Dimension Breakdown</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {consensus.dimension_scores.map((dim) => (
            <DimensionCard key={dim.dimension} dimension={dim} />
          ))}
        </div>
      </div>

      {/* Priority Improvements (fallback if no structured examples) */}
      {improvements.length === 0 && consensus.priority_improvements.length > 0 && (
        <div className="bg-orange-50 rounded-xl border border-orange-200 p-6">
          <h3 className="text-lg font-semibold text-orange-800 mb-4">
            🎯 Priority Areas for Improvement
          </h3>
          <ul className="space-y-2">
            {consensus.priority_improvements.map((imp, i) => (
              <li key={i} className="flex gap-2 text-orange-700">
                <span className="text-orange-400">→</span>
                {imp}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Weak Areas from History */}
      {weak_areas.length > 0 && (
        <div className="bg-yellow-50 rounded-xl border border-yellow-200 p-6">
          <h3 className="text-lg font-semibold text-yellow-800 mb-4">
            📊 Historical Weak Areas
          </h3>
          <div className="space-y-3">
            {weak_areas.map((wa) => (
              <div key={wa.dimension} className="flex items-start gap-3">
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    wa.trend === "improving"
                      ? "bg-green-100 text-green-700"
                      : wa.trend === "declining"
                        ? "bg-red-100 text-red-700"
                        : "bg-gray-100 text-gray-700"
                  }`}
                >
                  {wa.trend === "improving"
                    ? "↑"
                    : wa.trend === "declining"
                      ? "↓"
                      : "→"}{" "}
                  {wa.trend}
                </span>
                <div>
                  <div className="font-medium text-yellow-800">
                    {DIMENSION_LABELS[wa.dimension]} (avg:{" "}
                    {wa.average_score.toFixed(1)})
                  </div>
                  <div className="text-sm text-yellow-700">
                    {wa.recommendation}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Improvement from Last */}
      {improvement_from_last &&
        Object.keys(improvement_from_last).length > 0 && (
          <div className="bg-green-50 rounded-xl border border-green-200 p-6">
            <h3 className="text-lg font-semibold text-green-800 mb-4">
              📈 Change from Last Essay
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(improvement_from_last).map(([dim, change]) => (
                <div key={dim} className="text-center">
                  <div
                    className={`text-2xl font-bold ${
                      change > 0
                        ? "text-green-600"
                        : change < 0
                          ? "text-red-600"
                          : "text-gray-600"
                    }`}
                  >
                    {change > 0 ? "+" : ""}
                    {change.toFixed(1)}
                  </div>
                  <div className="text-xs text-gray-600">
                    {DIMENSION_LABELS[dim as keyof typeof DIMENSION_LABELS] ||
                      dim}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      {/* Model Essay - Rewritten Version Scoring 6 */}
      {results.model_essay && (
        <details className="bg-emerald-50 rounded-xl border border-emerald-200">
          <summary className="p-4 cursor-pointer font-semibold text-emerald-800 hover:text-emerald-900">
            ✨ View Model Essay (Score 6 Version)
          </summary>
          <div className="p-6 pt-2 space-y-4">
            <p className="text-sm text-emerald-700 mb-4">
              This is a rewritten version of your essay that demonstrates how to score 6 across all dimensions.
              Compare it with your original to see the improvements.
            </p>
            
            <div className="bg-white rounded-lg p-4 border border-emerald-200">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-semibold text-emerald-800">Model Essay</h4>
                <span className="text-sm text-emerald-600">
                  {results.model_essay.word_count} words
                </span>
              </div>
              <div className="prose max-w-none text-gray-700 whitespace-pre-wrap leading-relaxed">
                {results.model_essay.model_essay}
              </div>
            </div>
            
            {results.model_essay.improvement_notes && (
              <div className="bg-emerald-100 rounded-lg p-4">
                <h4 className="font-semibold text-emerald-800 mb-2">
                  Key Improvements Made
                </h4>
                <div className="text-sm text-emerald-700 whitespace-pre-wrap">
                  {results.model_essay.improvement_notes}
                </div>
              </div>
            )}
          </div>
        </details>
      )}

      {/* Individual Grader Results (Collapsed by default) */}
      <details className="bg-gray-50 rounded-xl border border-gray-200">
        <summary className="p-4 cursor-pointer font-semibold text-gray-700 hover:text-gray-900">
          🔍 View Individual Grader Results
        </summary>
        <div className="p-4 pt-0 space-y-4">
          {grader_results.map((gr) => (
            <div
              key={gr.grader_id}
              className="bg-white rounded-lg p-4 border border-gray-200"
            >
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium">Grader {gr.grader_id + 1}</span>
                <ScoreBadge score={gr.overall_score} />
              </div>
              <p className="text-sm text-gray-600 whitespace-pre-wrap">
                {gr.overall_feedback}
              </p>
              <div className="text-xs text-gray-400 mt-2 flex justify-between">
                <span>Grading time: {formatTime(gr.grading_time_ms)}</span>
                <span>Fact checks: {gr.fact_checks_count || 0}</span>
              </div>
            </div>
          ))}
        </div>
      </details>
    </div>
  );
}
