"use client";

import { useState, useEffect } from "react";
import { countWords } from "@/lib/utils";
import type { SamplePrompt } from "@/types";

interface EssayEditorProps {
  onSubmit: (prompt: string, essay: string) => void;
  isLoading: boolean;
  samplePrompts?: SamplePrompt[];
}

export default function EssayEditor({
  onSubmit,
  isLoading,
  samplePrompts = [],
}: EssayEditorProps) {
  const [prompt, setPrompt] = useState("");
  const [essay, setEssay] = useState("");
  const [selectedPromptId, setSelectedPromptId] = useState<number | null>(null);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
  const [timerActive, setTimerActive] = useState(false);

  const wordCount = countWords(essay);
  const minWords = 300;
  const targetWords = 500;

  // Timer effect
  useEffect(() => {
    if (!timerActive || timeRemaining === null) return;

    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev === null || prev <= 0) {
          setTimerActive(false);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [timerActive, timeRemaining]);

  const handlePromptSelect = (promptId: number) => {
    const selected = samplePrompts.find((p) => p.id === promptId);
    if (selected) {
      setPrompt(`${selected.prompt}\n\n${selected.instructions}`);
      setSelectedPromptId(promptId);
    }
  };

  const startTimer = () => {
    setTimeRemaining(30 * 60); // 30 minutes
    setTimerActive(true);
  };

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleSubmit = () => {
    if (prompt.trim() && essay.trim()) {
      onSubmit(prompt, essay);
    }
  };

  return (
    <div className="space-y-6">
      {/* Timer Bar */}
      {timerActive && timeRemaining !== null && (
        <div
          className={`p-3 rounded-lg flex justify-between items-center ${
            timeRemaining < 300
              ? "bg-red-100 text-red-800"
              : "bg-blue-100 text-blue-800"
          }`}
        >
          <span className="font-medium">Time Remaining</span>
          <span className="text-2xl font-mono font-bold">
            {formatTimer(timeRemaining)}
          </span>
        </div>
      )}

      {/* Prompt Selection */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Select a GRE Issue Writing Prompt
        </label>
        <select
          value={selectedPromptId || ""}
          onChange={(e) => handlePromptSelect(Number(e.target.value))}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="">-- Choose a prompt or write your own --</option>
          {samplePrompts.map((p) => (
            <option key={p.id} value={p.id}>
              {p.prompt.substring(0, 80)}...
            </option>
          ))}
        </select>
      </div>

      {/* Prompt Text Area */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Essay Prompt
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter the GRE Issue Writing prompt..."
          className="w-full h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        />
      </div>

      {/* Timer Start Button */}
      {!timerActive && (
        <div className="flex gap-2">
          <button
            onClick={startTimer}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
          >
            🕐 Start 30-Minute Timer
          </button>
        </div>
      )}

      {/* Essay Text Area */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label className="block text-sm font-medium text-gray-700">
            Your Essay Response
          </label>
          <div className="text-sm">
            <span
              className={
                wordCount < minWords
                  ? "text-red-600"
                  : wordCount < targetWords
                    ? "text-yellow-600"
                    : "text-green-600"
              }
            >
              {wordCount} words
            </span>
            <span className="text-gray-400"> / {targetWords} target</span>
          </div>
        </div>
        <textarea
          value={essay}
          onChange={(e) => setEssay(e.target.value)}
          placeholder="Write your essay response here..."
          className="w-full h-96 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 font-serif text-lg leading-relaxed"
        />
      </div>

      {/* Word Count Progress */}
      <div className="space-y-1">
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              wordCount < minWords
                ? "bg-red-500"
                : wordCount < targetWords
                  ? "bg-yellow-500"
                  : "bg-green-500"
            }`}
            style={{
              width: `${Math.min((wordCount / targetWords) * 100, 100)}%`,
            }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500">
          <span>Minimum: {minWords}</span>
          <span>Target: {targetWords}</span>
        </div>
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={isLoading || !prompt.trim() || wordCount < 50}
        className={`w-full py-4 rounded-lg font-semibold text-white transition ${
          isLoading || !prompt.trim() || wordCount < 50
            ? "bg-gray-400 cursor-not-allowed"
            : "bg-primary-600 hover:bg-primary-700"
        }`}
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            Grading in Progress... (This may take 30-60 seconds)
          </span>
        ) : (
          "📝 Submit for Grading"
        )}
      </button>

      {wordCount < 50 && essay.length > 0 && (
        <p className="text-sm text-red-600">
          Please write at least 50 words to submit your essay.
        </p>
      )}
    </div>
  );
}
