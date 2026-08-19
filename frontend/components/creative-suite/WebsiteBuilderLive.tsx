"use client";

import { Check, Download, Globe2, Rocket, WandSparkles } from "lucide-react";
import { useState } from "react";
import { api } from "@/lib/api";

type Toast = { kind: "success" | "info" | "error"; text: string } | null;

export function WebsiteBuilderLive({ notify }: { notify: (toast: Toast) => void }) {
  const [brief, setBrief] = useState("A conversion-focused launch page for David AI, a calm operating system for independent business owners.");
  const [working, setWorking] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");

  async function buildWebsite() {
    if (!brief.trim() || working) return;
    setWorking(true);
    setError("");
    setResult(null);
    try {
      const response = await api.websiteGenerate(brief.trim());
      setResult(response);
      notify({ kind: "success", text: "David returned a previewable website artifact." });
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "Website generation failed.";
      setError(message);
      notify({ kind: "error", text: "David did not mark the website complete because no artifact was returned." });
    } finally {
      setWorking(false);
    }
  }

  const html = typeof result?.html === "string" ? result.html : "";
  const previewPath = typeof result?.preview_url === "string" ? result.preview_url : "";
  const previewUrl = previewPath ? api.websitePreviewUrl(previewPath) : "";
  const persisted = result?.persistence_status === "persisted";

  return <div><div className="page-header"><div><div className="micro-label">DAVID AI / CREATIVE STUDIO</div><h1>Website builder</h1><p>Describe the system. David returns a real responsive preview and a link you can reopen.</p></div><div className="header-actions"><span className={`status-tag ${html ? "tag-green" : working ? "tag-amber" : "tag-blue"}`}><span className="status-dot" /> {working ? "Generating" : html ? "Preview ready" : "Ready"}</span><button className="button button-primary" onClick={() => void buildWebsite()} disabled={working || !brief.trim()}><Rocket size={16} /> {working ? "Building…" : "Build website"}</button></div></div><div className="builder-layout"><section className="panel-card builder-prompt"><div className="section-header"><div><div className="micro-label">BUILD BRIEF</div><h2>Tell David what to build</h2><p>The model creates a structured page and David turns it into a previewable artifact.</p></div></div><textarea value={brief} onChange={(event) => setBrief(event.target.value)} /><div className="builder-options"><span className="option-chip active"><Check size={14} /> Responsive</span><span className="option-chip active"><Check size={14} /> Brand-aware</span><span className="option-chip active"><Check size={14} /> Review before publish</span></div><div className="builder-action-row"><span>Publishing remains an approval-gated action.</span><button className="button button-primary" onClick={() => void buildWebsite()} disabled={working || !brief.trim()}><WandSparkles size={15} /> Generate preview</button></div>{error && <div className="provider-result provider-result-error"><span className="micro-label">WEBSITE ERROR</span><p>{error}</p></div>}{html && <div className="provider-result"><span className="micro-label">VERIFIED WEBSITE ARTIFACT</span><p>{persisted ? "Saved to the connected persistence layer." : "Available through David’s local artifact store for this deployment."}</p><div className="media-result-actions">{previewUrl && <a className="button button-secondary" href={previewUrl} target="_blank" rel="noreferrer"><Globe2 size={15} /> Open preview</a>}<a className="button button-secondary" href={`data:text/html;charset=utf-8,${encodeURIComponent(html)}`} download="david-ai-website.html"><Download size={15} /> Download HTML</a></div></div>}</section><section className="panel-card browser-preview"><div className="browser-top"><div className="browser-dots"><span /><span /><span /></div><span>{previewUrl ? "david-ai / generated-preview" : "david-ai / live-preview"}</span></div>{html ? <iframe title="Generated David AI website preview" srcDoc={html} sandbox="allow-scripts" className="generated-site-frame" /> : <div className="preview-content"><div className="preview-hero"><span className="eyebrow-pill">DAVID AI / PREVIEW</span><h2>Your generated website appears here.</h2><p>Write a brief and generate a real artifact. The preview will not claim completion before HTML exists.</p></div></div>}</section></div></div>;
}
