"use client";

import { FormEvent, useState } from "react";
import { Send, ShieldAlert } from "lucide-react";
import { sendChat, type LlmRequest } from "@/lib/api";

type PromptConsoleProps = {
  onCreated: (request: LlmRequest) => void;
};

export function PromptConsole({ onCreated }: PromptConsoleProps) {
  const [prompt, setPrompt] = useState("");
  const [model, setModel] = useState("gpt-5-mini");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!prompt.trim()) return;

    setIsSubmitting(true);
    setError(null);
    try {
      const result = await sendChat({ prompt, model });
      onCreated(result);
      setPrompt("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="rounded-lg border border-[var(--border)] bg-[var(--panel)] p-4 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold">Prompt Console</h2>
          <p className="mt-1 text-sm text-[var(--muted)]">Send a live request and capture observability data.</p>
        </div>
        <ShieldAlert className="text-[var(--warning)]" size={20} aria-hidden="true" />
      </div>
      <form className="space-y-3" onSubmit={onSubmit}>
        <label className="block text-sm font-medium" htmlFor="model">
          Model
        </label>
        <input
          id="model"
          className="w-full rounded-md border border-[var(--border)] bg-white px-3 py-2 font-mono text-sm outline-none focus:border-[var(--accent)]"
          value={model}
          onChange={(event) => setModel(event.target.value)}
        />
        <label className="block text-sm font-medium" htmlFor="prompt">
          Prompt
        </label>
        <textarea
          id="prompt"
          className="min-h-32 w-full resize-y rounded-md border border-[var(--border)] bg-white px-3 py-2 text-sm outline-none focus:border-[var(--accent)]"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder="Ask the model a question..."
        />
        {error ? <p className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
        <button
          className="inline-flex items-center justify-center gap-2 rounded-md bg-[var(--accent)] px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
          disabled={isSubmitting || !prompt.trim()}
          type="submit"
        >
          <Send size={16} />
          {isSubmitting ? "Sending" : "Send Prompt"}
        </button>
      </form>
    </section>
  );
}
