"use client";

import { FormEvent, useState } from "react";
import { api } from "@/lib/api";

export function WebsiteGenerationPanel() {
  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = prompt.trim();
    if (!value || pending) return;

    setPending(true);
    setError(null);
    setResult(null);
    try {
      setResult(await api.websiteGenerate(value));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Website generation failed");
    } finally {
      setPending(false);
    }
  }

  const html = typeof result?.html === "string" ? result.html : null;
  const url = typeof result?.url === "string" ? result.url : null;
  const message = typeof result?.message === "string" ? result.message : null;

  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/55 p-5 shadow-2xl shadow-cyan-950/20">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-cyan-300/80">Adapted OS capability</p>
          <h2 className="mt-1 text-lg font-semibold text-white">Prompt-to-website workspace</h2>
          <p className="mt-1 max-w-xl text-sm text-slate-400">A focused generation flow adapted from the source AI OS and connected to the primary David backend.</p>
        </div>
        <span className="rounded-full border border-emerald-400/30 px-2.5 py-1 text-[10px] uppercase tracking-[0.18em] text-emerald-300">Primary API</span>
      </div>

      <form onSubmit={submit} className="space-y-3">
        <textarea
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          rows={4}
          placeholder="Describe the website David should build…"
          className="w-full resize-y rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300/60"
        />
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs text-slate-500">Publishing remains a separate, approval-gated action.</p>
          <button type="submit" disabled={pending || !prompt.trim()} className="rounded-xl bg-cyan-300 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-40">
            {pending ? "Generating…" : "Generate website"}
          </button>
        </div>
      </form>

      {error ? <div className="mt-4 rounded-xl border border-rose-400/30 bg-rose-950/20 p-3 text-sm text-rose-200">{error}</div> : null}
      {result ? (
        <div className="mt-4 rounded-xl border border-white/10 bg-black/20 p-3">
          {url ? <a href={url} target="_blank" rel="noreferrer" className="break-all text-sm text-cyan-300 underline">{url}</a> : null}
          {message ? <p className="mt-2 text-sm text-slate-300">{message}</p> : null}
          {html ? <iframe title="Generated website preview" srcDoc={html} sandbox="" className="mt-3 h-[420px] w-full rounded-lg border border-white/10 bg-white" /> : <pre className="mt-3 max-h-64 overflow-auto rounded-lg bg-black/30 p-3 text-xs text-slate-300">{JSON.stringify(result, null, 2)}</pre>}
        </div>
      ) : null}
    </section>
  );
}
