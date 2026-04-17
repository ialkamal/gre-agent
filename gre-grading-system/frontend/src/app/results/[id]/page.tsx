"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getEssayDetails } from "@/lib/api";
import ScoreChart from "@/components/ScoreChart";
import { formatDate, formatTime } from "@/lib/utils";
import { DIMENSION_LABELS, getScoreColor, SCORE_LABELS } from "@/types";

interface ImprovementExample {
  area: string;
  tip: string;
  before: string;
  after: string;
}

// Parse the structured feedback to extract before/after examples
function parseImprovements(feedback: string | null): {
  mainFeedback: string;
  improvements: ImprovementExample[];
} {
  if (!feedback) {
    return { mainFeedback: "", improvements: [] };
  }
  
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

export default function ResultsPage() {
  const params = useParams();
  const essayId = params.id as string;
  const [essay, setEssay] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadEssay() {
      try {
        const data = await getEssayDetails(essayId);
        setEssay(data);
      } catch (err) {
        setError("Failed to load essay details.");
      } finally {
        setLoading(false);
      }
    }
    loadEssay();
  }, [essayId]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <div className="animate-spin h-8 w-8 border-4 border-primary-500 border-t-transparent rounded-full mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading essay...</p>
      </div>
    );
  }

  if (error || !essay) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-800 font-medium">
            {error || "Essay not found"}
          </p>
          <Link
            href="/history"
            className="inline-block mt-4 text-primary-600 underline"
          >
            Back to History
          </Link>
        </div>
      </div>
    );
  }

  // Parse merged feedback for before/after improvements
  const { mainFeedback, improvements } = parseImprovements(essay.merged_feedback);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <Link
            href="/history"
            className="text-primary-600 hover:underline text-sm mb-2 block"
          >
            ← Back to History
          </Link>
          <h1 className="text-2xl font-bold text-gray-900">Essay Results</h1>
          <p className="text-gray-500">{formatDate(essay.created_at)}</p>
        </div>
        <div className="text-right">
          <div
            className={`text-4xl font-bold ${getScoreColor(essay.overall_score)}`}
          >
            {essay.overall_score.toFixed(1)}
          </div>
          <div className="text-sm text-gray-500">
            {SCORE_LABELS[Math.round(essay.overall_score)]}
          </div>
        </div>
      </div>

      {/* Prompt */}
      <div className="bg-gray-50 rounded-xl p-6">
        <h2 className="text-sm font-semibold text-gray-500 mb-2">PROMPT</h2>
        <p className="text-gray-800">{essay.prompt}</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-2xl font-bold text-primary-600">
            {essay.grader_results?.length || 3}
          </div>
          <div className="text-sm text-gray-600">Graders</div>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-2xl font-bold text-blue-600">
            {essay.total_fact_checks || 0}
          </div>
          <div className="text-sm text-gray-600">Fact Checks</div>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="text-2xl font-bold text-gray-600">
            {essay.word_count}
          </div>
          <div className="text-sm text-gray-600">Words</div>
        </div>
      </div>

      {/* Score Chart */}
      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <h2 className="text-lg font-semibold mb-4">Dimension Scores</h2>
        <ScoreChart
          scores={essay.dimension_scores.map((ds: any) => ({
            dimension: ds.dimension,
            score: ds.score,
            feedback: ds.feedback,
            strengths: ds.strengths || [],
            improvements: ds.improvements || [],
          }))}
        />
      </div>

      {/* Merged Feedback */}
      {mainFeedback && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4">📝 Detailed Feedback</h2>
          <div className="prose max-w-none text-gray-700 whitespace-pre-wrap">
            {mainFeedback}
          </div>
        </div>
      )}

      {/* Before/After Improvement Examples */}
      {improvements.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">
            🎯 Priority Improvements with Examples
          </h2>
          <div className="space-y-4">
            {improvements.map((improvement, i) => (
              <BeforeAfterCard key={i} improvement={improvement} />
            ))}
          </div>
        </div>
      )}

      {/* Dimension Details */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Dimension Breakdown</h2>
        {essay.dimension_scores.map((ds: any) => (
          <div
            key={ds.dimension}
            className="bg-white rounded-lg p-4 border border-gray-200"
          >
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">
                {DIMENSION_LABELS[
                  ds.dimension as keyof typeof DIMENSION_LABELS
                ] || ds.dimension}
              </span>
              <span className={`text-xl font-bold ${getScoreColor(ds.score)}`}>
                {ds.score.toFixed(1)}
              </span>
            </div>
            <p className="text-gray-600 text-sm">{ds.feedback}</p>

            {ds.strengths && ds.strengths.length > 0 && (
              <div className="mt-2">
                <p className="text-xs font-semibold text-green-700">
                  ✓ Strengths
                </p>
                <ul className="text-xs text-green-600">
                  {ds.strengths.map((s: string, i: number) => (
                    <li key={i}>• {s}</li>
                  ))}
                </ul>
              </div>
            )}

            {ds.improvements && ds.improvements.length > 0 && (
              <div className="mt-2">
                <p className="text-xs font-semibold text-orange-700">
                  → To Improve
                </p>
                <ul className="text-xs text-orange-600">
                  {ds.improvements.map((imp: string, i: number) => (
                    <li key={i}>• {imp}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Grader Results */}
      {essay.grader_results && essay.grader_results.length > 0 && (
        <div className="bg-white rounded-xl p-6 border border-gray-200">
          <h2 className="text-lg font-semibold mb-4">Individual Grader Results</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {essay.grader_results.map((gr: any) => (
              <div key={gr.grader_id} className="bg-gray-50 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-gray-700">
                    Grader {gr.grader_id + 1}
                  </span>
                  <span className={`text-xl font-bold ${getScoreColor(gr.overall_score)}`}>
                    {gr.overall_score.toFixed(1)}
                  </span>
                </div>
                <div className="text-xs text-gray-500 space-y-1">
                  <div>Temp: {gr.temperature}</div>
                  <div>Fact checks: {gr.fact_checks_count || 0}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Model Essay */}
      {essay.model_essay && (
        <details className="bg-emerald-50 rounded-xl border border-emerald-200">
          <summary className="p-4 cursor-pointer font-semibold text-emerald-800 hover:text-emerald-900">
            ✨ View Model Essay (Score 6 Version)
          </summary>
          <div className="p-6 pt-2 space-y-4">
            <div className="bg-white rounded-lg p-4 border border-emerald-200 font-serif leading-relaxed whitespace-pre-wrap">
              {essay.model_essay}
            </div>
            
            {essay.model_essay_notes && (
              <div className="bg-emerald-100 rounded-lg p-4">
                <h4 className="font-semibold text-emerald-800 mb-2">
                  Key Improvements Made
                </h4>
                <div className="text-emerald-700 text-sm whitespace-pre-wrap">
                  {essay.model_essay_notes}
                </div>
              </div>
            )}
          </div>
        </details>
      )}

      {/* Essay Text */}
      <details className="bg-gray-50 rounded-xl border border-gray-200">
        <summary className="p-4 cursor-pointer font-semibold text-gray-700">
          📝 View Your Essay ({essay.word_count} words)
        </summary>
        <div className="p-4 pt-0">
          <div className="bg-white rounded-lg p-4 border border-gray-200 font-serif leading-relaxed whitespace-pre-wrap">
            {essay.text}
          </div>
        </div>
      </details>
    </div>
  );
}
