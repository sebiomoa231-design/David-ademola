"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { IntegrationOrb } from "./IntegrationOrb";
import { WebsiteGenerationPanel } from "./WebsiteGenerationPanel";

type Source = {
  id: string;
  name: string;
  repository: string;
  family: string;
  adapted_capabilities: string[];
  integration_boundary: string;
  source_files: string[];
};

export function SourceIntegrationsPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.integrations
      .sources()
      .then((response) => setSources(response.sources))
      .catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Could not load source integrations"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 px-5 py-8 text-slate-100 md:px-10">
      <div className="mx-auto max-w-7xl space-y-7">
        <header className="flex flex-col justify-between gap-5 border-b border-white/10 pb-6 md:flex-row md:items-end">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.34em] text-cyan-300">David AI / source integrations</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">A preserved primary, with compatible capability packs.</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">Each source repository is represented separately. Adapted code is isolated behind additive contracts so the primary David AI control plane remains intact.</p>
          </div>
          <a href="/" className="rounded-xl border border-white/15 px-4 py-2 text-sm text-slate-300 transition hover:border-cyan-300/60 hover:text-white">Back to David AI</a>
        </header>

        <section className="grid gap-6 rounded-2xl border border-white/10 bg-gradient-to-br from-cyan-950/40 via-slate-950 to-violet-950/30 p-6 md:grid-cols-[220px_1fr] md:items-center">
          <div className="flex justify-center"><IntegrationOrb state={loading ? "PROCESSING" : error ? "ERROR" : "RESPONDING"} /></div>
          <div>
            <p className="text-[10px] uppercase tracking-[0.26em] text-slate-500">Integration posture</p>
            <h2 className="mt-2 text-xl font-semibold text-white">Non-destructive by design</h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">The adapted source patterns are exposed as capability metadata and focused workflows. Existing routes, providers, secrets, and deployment contracts remain authoritative in the primary repository.</p>
            <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-300">
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">6 source repositories</span>
              <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">1 primary control plane</span>
              <span className="rounded-full border border-emerald-400/25 bg-emerald-950/20 px-3 py-1 text-emerald-300">Secrets excluded</span>
            </div>
          </div>
        </section>

        <WebsiteGenerationPanel />

        <section>
          <div className="mb-4 flex items-end justify-between gap-4">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.28em] text-cyan-300/80">Source registry</p>
              <h2 className="mt-1 text-xl font-semibold text-white">Adapted capability packs</h2>
            </div>
            {loading ? <span className="text-xs text-slate-500">Loading…</span> : <span className="text-xs text-slate-500">{sources.length} registered</span>}
          </div>
          {error ? <div className="rounded-xl border border-rose-400/30 bg-rose-950/20 p-4 text-sm text-rose-200">{error}</div> : null}
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {sources.map((source) => (
              <article key={source.id} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 transition hover:border-cyan-300/30 hover:bg-white/[0.05]">
                <div className="flex items-start justify-between gap-3">
                  <div><h3 className="font-semibold text-white">{source.name}</h3><p className="mt-1 text-xs text-slate-500">{source.family}</p></div>
                  <span className="rounded-full border border-cyan-300/20 px-2 py-1 text-[9px] uppercase tracking-[0.16em] text-cyan-300">Adapted</span>
                </div>
                <div className="mt-4 space-y-2">{source.adapted_capabilities.map((capability) => <div key={capability} className="rounded-lg bg-black/20 px-3 py-2 text-xs text-slate-300">{capability}</div>)}</div>
                <p className="mt-4 text-xs leading-5 text-slate-500">{source.integration_boundary}</p>
                <a href={source.repository} target="_blank" rel="noreferrer" className="mt-4 inline-block text-xs text-cyan-300 underline underline-offset-4">View source repository</a>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
