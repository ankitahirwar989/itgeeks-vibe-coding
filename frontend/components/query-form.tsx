"use client";

import { useState } from "react";
import { BookOpen, Loader2, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ResultPanel } from "@/components/result-panel";
import { askQuestion } from "@/lib/api";
import type { QueryResponse } from "@/types/api";

const EXAMPLES: { label: string; question: string }[] = [
  {
    label: "Answerable",
    question: "What attendance percentage is required to sit for the semester examination?",
  },
  {
    label: "Unknown",
    question: "What happens if I miss the semester examination because I am attending my cousin's wedding?",
  },
  {
    label: "Contradiction",
    question:
      "What is the minimum attendance percentage required to sit for the semester examination if a student has an approved medical certificate?",
  },
];

export function QueryForm() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<QueryResponse | null>(null);

  async function submit(q: string) {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await askQuestion(q);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
        <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-muted-foreground">
          <BookOpen className="h-4 w-4" />
          Ask about the rulebook
        </div>
        <Textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. What attendance percentage is required to sit for the semester examination?"
        />
        <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex.label}
                onClick={() => {
                  setQuestion(ex.question);
                  submit(ex.question);
                }}
                className="rounded-full border border-border px-3 py-1 text-xs text-muted-foreground hover:bg-muted"
              >
                Try: {ex.label}
              </button>
            ))}
          </div>
          <Button onClick={() => submit(question)} disabled={loading || !question.trim()}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            Ask
          </Button>
        </div>
      </div>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 p-4 text-sm text-red-800 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">
          {error}
        </div>
      )}

      {result && <ResultPanel result={result} />}
    </div>
  );
}
