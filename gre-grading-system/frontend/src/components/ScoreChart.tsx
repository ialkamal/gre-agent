"use client";

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";
import type { DimensionScore } from "@/types";
import { DIMENSION_LABELS } from "@/types";

interface ScoreChartProps {
  scores: DimensionScore[];
  showBar?: boolean;
}

const COLORS = {
  6: "#22c55e",
  5: "#84cc16",
  4: "#eab308",
  3: "#f97316",
  2: "#ef4444",
  1: "#dc2626",
  0: "#991b1b",
};

function getColor(score: number): string {
  if (score >= 5.5) return COLORS[6];
  if (score >= 4.5) return COLORS[5];
  if (score >= 3.5) return COLORS[4];
  if (score >= 2.5) return COLORS[3];
  if (score >= 1.5) return COLORS[2];
  return COLORS[1];
}

export default function ScoreChart({
  scores,
  showBar = true,
}: ScoreChartProps) {
  const chartData = scores.map((s) => ({
    dimension: DIMENSION_LABELS[s.dimension].split(" ")[0], // Short label
    fullName: DIMENSION_LABELS[s.dimension],
    score: s.score,
    fullMark: 6,
  }));

  return (
    <div className="grid md:grid-cols-2 gap-6">
      {/* Radar Chart */}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={chartData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 12 }} />
            <PolarRadiusAxis
              angle={30}
              domain={[0, 6]}
              tick={{ fontSize: 10 }}
            />
            <Radar
              name="Score"
              dataKey="score"
              stroke="#0284c7"
              fill="#0ea5e9"
              fillOpacity={0.5}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Bar Chart */}
      {showBar && (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical">
              <XAxis type="number" domain={[0, 6]} />
              <YAxis
                dataKey="dimension"
                type="category"
                width={80}
                tick={{ fontSize: 11 }}
              />
              <Tooltip
                formatter={(value: number) => [value.toFixed(1), "Score"]}
                labelFormatter={(label) =>
                  chartData.find((d) => d.dimension === label)?.fullName ||
                  label
                }
              />
              <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getColor(entry.score)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
