"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { GradingDimension } from "@/types";
import { DIMENSION_LABELS } from "@/types";

interface ProgressChartProps {
  data: Array<{
    essay_id: string;
    date: string;
    overall_score: number;
    [key: string]: any;
  }>;
  selectedDimensions?: GradingDimension[];
}

const DIMENSION_COLORS: Record<string, string> = {
  overall: "#0c4a6e",
  thesis: "#0284c7",
  reasoning: "#0891b2",
  evidence: "#059669",
  structure: "#65a30d",
  analysis: "#ca8a04",
  language: "#ea580c",
  grammar: "#dc2626",
  coherence: "#9333ea",
};

export default function ProgressChart({
  data,
  selectedDimensions = [],
}: ProgressChartProps) {
  // Format dates for display
  const formattedData = data.map((item, index) => ({
    ...item,
    label: `Essay ${index + 1}`,
    dateLabel: new Date(item.date).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
  }));

  const showDimensions: GradingDimension[] =
    selectedDimensions.length > 0 ? selectedDimensions : [];

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="dateLabel" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 6]} tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value: number, name: string) => [
              value.toFixed(1),
              name === "overall_score"
                ? "Overall"
                : DIMENSION_LABELS[name as GradingDimension] || name,
            ]}
          />
          <Legend />

          {/* Always show overall score */}
          <Line
            type="monotone"
            dataKey="overall_score"
            name="Overall"
            stroke={DIMENSION_COLORS.overall}
            strokeWidth={3}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />

          {/* Show selected dimensions */}
          {showDimensions.map((dim) => (
            <Line
              key={dim}
              type="monotone"
              dataKey={dim}
              name={DIMENSION_LABELS[dim]}
              stroke={DIMENSION_COLORS[dim] || "#666"}
              strokeWidth={2}
              dot={{ r: 3 }}
              strokeDasharray="5 5"
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
