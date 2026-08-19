"use client";

import { AudioLines, Check, Download, FileImage, Headphones, Image as ImageIcon, RefreshCw, SlidersHorizontal, Upload, Wand2 } from "lucide-react";
import { ChangeEvent, useMemo, useState } from "react";
import { api, toAudioUrl } from "@/lib/api";

type MultimodalKind = "voice" | "image" | "music" | "enhance" | "edit" | "reshoot";
type Toast = { kind: "success" | "info" | "error"; text: string } | null;

type Props = { kind: MultimodalKind; notify: (toast: Toast) => void };

const config: Record<MultimodalKind, { label: string; eyebrow: string; description: string; placeholder: string; accent: string; icon: typeof ImageIcon; needsSource?: boolean }> = {
  voice: { label: "Voice studio", eyebrow: "SPEECH + VOICE", description: "Generate a reviewable David voice track and keep the saved audio available for replay.", placeholder: "My name is David AI. I am a calm, capable voice-first model ready to help.", accent: "blue", icon: Headphones },
  image: { label: "Image lab", eyebrow: "VISUAL GENERATION", description: "Generate a brand-aware image through the configured Gemini or OpenAI image path.", placeholder: "A premium editorial product image for David AI: dark navy interface, cyan orbital core, precise cinematic lighting.", accent: "purple", icon: ImageIcon },
  music: { label: "Music studio", eyebrow: "SOUND DESIGN", description: "Generate a short sound-design bed through the configured audio-effects path and download the result.", placeholder: "A restrained futuristic interface sound bed: soft cyan pulse, subtle orbital shimmer, no melody, clean digital space.", accent: "amber", icon: AudioLines },
  enhance: { label: "Enhance media", eyebrow: "MEDIA ENHANCEMENT", description: "Upload an image and ask David to improve clarity, lighting, composition, or finish while preserving the subject.", placeholder: "Improve the lighting, clarity, and premium cyan orbital glow while preserving the original interface layout.", accent: "green", icon: Wand2, needsSource: true },
  edit: { label: "Edit studio", eyebrow: "CONTROLLED IMAGE EDITING", description: "Upload an image and describe the exact visual change. The edited result is shown before you download it.", placeholder: "Replace the empty lower workspace with a refined status panel while preserving the original David AI visual language.", accent: "red", icon: SlidersHorizontal, needsSource: true },
  reshoot: { label: "Reshoot studio", eyebrow: "SCENE DIRECTION", description: "Upload a reference image and generate a controlled visual variation with the same core identity.", placeholder: "Reimagine this interface as a cinematic 16:9 hero view with the same cyan orbital core and restrained HUD geometry.", accent: "purple", icon: RefreshCw, needsSource: true },
};

function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => typeof reader.result === "string" ? resolve(reader.result) : reject(new Error("The selected file could not be read."));
    reader.onerror = () => reject(new Error("The selected file could not be read."));
    reader.readAsDataURL(file);
  });
}

function imageSource(response: Record<string, unknown>): string | null {
  const images = Array.isArray(response.images) ? response.images : [];
  const first = images[0] && typeof images[0] === "object" ? images[0] as Record<string, unknown> : null;
  if (!first) return null;
  const b64 = typeof first.b64_json === "string" ? first.b64_json : typeof first.data === "string" ? first.data : null;
  if (!b64) return null;
  const mime = typeof first.mime_type === "string" ? first.mime_type : "image/png";
  return b64.startsWith("data:") ? b64 : `data:${mime};base64,${b64}`;
}

function dataPart(dataUrl: string) {
  const match = dataUrl.match(/^data:([^;]+);base64,(.+)$/);
  return match ? { mimeType: match[1], base64: match[2] } : { mimeType: "image/png", base64: dataUrl };
}

export function LiveMultimodalStudio({ kind, notify }: Props) {
  const meta = config[kind];
  const Icon = meta.icon;
  const [brief, setBrief] = useState(meta.placeholder);
  const [source, setSource] = useState<File | null>(null);
  const [sourcePreview, setSourcePreview] = useState<string | null>(null);
  const [working, setWorking] = useState(false);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [resultText, setResultText] = useState("");
  const [error, setError] = useState("");
  const [stage, setStage] = useState<"ready" | "working" | "complete" | "error">("ready");
  const sourceLabel = useMemo(() => source ? `${source.name} · ${(source.size / 1024 / 1024).toFixed(2)} MB` : "No reference selected", [source]);

  async function selectSource(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] || null;
    setSource(file);
    setSourcePreview(file ? await readFileAsDataUrl(file) : null);
  }

  async function generate() {
    if (!brief.trim() || working) return;
    if (meta.needsSource && !sourcePreview) {
      setError("Select a reference image first so David can perform a grounded media pass.");
      setStage("error");
      return;
    }
    setWorking(true);
    setStage("working");
    setError("");
    setImageUrl(null);
    setAudioUrl(null);
    setDownloadUrl(null);
    setResultText("");
    try {
      if (kind === "voice") {
        const response = await api.synthesize(brief.trim(), "AUTO", { persist: true });
        const url = response.audio_url || (typeof response.audio_base64 === "string" ? toAudioUrl(response.audio_base64, response.audio_format || "mpeg") : null);
        if (!url) throw new Error(response.reason || "The voice service returned no playable audio.");
        setAudioUrl(url);
        setDownloadUrl(url);
        setResultText(`David voice output is ready${response.persisted ? " and persisted" : " for this session"}.`);
      } else if (kind === "music") {
        const response = await api.soundEffect(brief.trim(), { durationSeconds: 8 });
        const url = toAudioUrl(response.audio_base64, response.audio_format || "mpeg");
        setAudioUrl(url);
        setDownloadUrl(url);
        setResultText("Sound-design output is ready for review and download.");
      } else {
        const reference = sourcePreview ? dataPart(sourcePreview) : undefined;
        const response = await api.providers.image(brief.trim(), ["gemini", "openai"], reference ? { imageBase64: reference.base64, imageMimeType: reference.mimeType } : {});
        const url = imageSource(response as Record<string, unknown>);
        if (!url) throw new Error("The image provider completed without returning a previewable image.");
        setImageUrl(url);
        const imageBlob = await fetch(url).then((result) => result.blob());
        const stored = await api.uploadFile(new File([imageBlob], `david-${kind}-${Date.now()}.png`, { type: imageBlob.type || "image/png" }), undefined, "image");
        setDownloadUrl(typeof stored.download_url === "string" ? stored.download_url : typeof stored.signed_url === "string" ? stored.signed_url : url);
        setResultText(`David ${meta.label.toLowerCase()} output is ready${stored.backend ? ` · ${stored.backend}` : ""}.`);
      }
      setStage("complete");
      notify({ kind: "success", text: `${meta.label} output is ready.` });
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : `${meta.label} failed.`;
      setError(message);
      setStage("error");
      notify({ kind: "error", text: `${meta.label} did not return a verified output.` });
    } finally {
      setWorking(false);
    }
  }

  return <div className="multimodal-page"><div className="page-header"><div><div className="micro-label">DAVID AI / {meta.eyebrow}</div><h1>{meta.label}</h1><p>{meta.description}</p></div><div className="header-actions"><span className={`status-tag ${stage === "complete" ? "tag-green" : stage === "error" ? "tag-red" : stage === "working" ? "tag-amber" : "tag-blue"}`}><span className="status-dot" /> {stage === "working" ? "Generating" : stage === "complete" ? "Output ready" : stage === "error" ? "Review error" : "Ready"}</span><button className="button button-primary" onClick={() => void generate()} disabled={working || !brief.trim()}>{working ? "Generating…" : "Generate output"}</button></div></div>
    <div className="multimodal-hero panel-card"><div className={`multimodal-icon tone-${meta.accent}`}><Icon size={25} /></div><div><div className="eyebrow-pill">REAL OUTPUT PATH</div><h2>One brief in. A reviewable artifact out.</h2><p>{meta.description}</p></div><div className="multimodal-boundary"><Check size={15} /><span>Preview and download are enabled</span></div></div>
    <div className="multimodal-grid"><section className="panel-card multimodal-brief"><div className="section-header"><div><div className="micro-label">PRODUCTION BRIEF</div><h2>Tell David what to make</h2><p>The model receives the brief, and any selected reference stays part of this request only.</p></div></div><textarea value={brief} onChange={(event) => setBrief(event.target.value)} aria-label={`${meta.label} production brief`} />{meta.needsSource && <label className="upload-drop"><FileImage size={18} /><span><strong>{source ? source.name : "Choose a reference image"}</strong><small>{sourceLabel}</small></span><input type="file" accept="image/*" onChange={(event) => void selectSource(event)} /></label>}<div className="multimodal-actions"><button className="button button-primary" onClick={() => void generate()} disabled={working || !brief.trim()}>{working ? "Generating output" : "Generate now"}</button>{downloadUrl && <a className="button button-secondary" href={downloadUrl} download target="_blank" rel="noreferrer"><Download size={15} /> Download</a>}</div>{error && <div className="provider-result provider-result-error"><span className="micro-label">OUTPUT ERROR</span><p>{error}</p></div>}{resultText && <div className="provider-result"><span className="micro-label">VERIFIED RESULT</span><p>{resultText}</p></div>}</section><section className="panel-card multimodal-plan"><div className="section-header"><div><div className="micro-label">OUTPUT SURFACE</div><h2>{imageUrl ? "Image preview" : audioUrl ? "Audio preview" : "David output"}</h2><p>Nothing is marked complete until a real output is returned by the backend.</p></div></div>{sourcePreview && !imageUrl && <img src={sourcePreview} alt="Selected reference" className="media-result-image" />}{imageUrl && <img src={imageUrl} alt="Generated David AI output" className="media-result-image" />}{audioUrl && <audio className="media-result-audio" controls src={audioUrl} />}{!imageUrl && !audioUrl && <div className="multimodal-preview"><div className="preview-orbit" /><Icon size={24} /><span>{working ? "David is working through the configured model path…" : "Your verified output will appear here."}</span></div>}{downloadUrl && <div className="output-access-row"><Upload size={14} /> Output access is available in this session and through the saved asset link.</div>}</section></div></div>;
}
