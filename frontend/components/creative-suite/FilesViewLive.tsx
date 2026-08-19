"use client";

import { ChevronRight, Database, Download, FileText, Upload } from "lucide-react";
import { ChangeEvent, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { AssetItem } from "@/lib/types";

type Toast = { kind: "success" | "info" | "error"; text: string } | null;

type LocalAsset = Record<string, unknown>;

export function FilesViewLive({ notify }: { notify: (toast: Toast) => void }) {
  const [assets, setAssets] = useState<AssetItem[]>([]);
  const [localAssets, setLocalAssets] = useState<LocalAsset[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [persistenceNote, setPersistenceNote] = useState("Reading the connected asset library.");

  async function load() {
    setLoading(true);
    const [remote, local] = await Promise.allSettled([api.library.assets(), api.localAssets()]);
    if (remote.status === "fulfilled") {
      setAssets(remote.value);
      setPersistenceNote("Connected library assets are available for review.");
    } else {
      setAssets([]);
      setPersistenceNote("Remote library persistence is not active for this deployment; local generated files remain available below.");
    }
    setLocalAssets(local.status === "fulfilled" ? local.value : []);
    setLoading(false);
  }

  useEffect(() => { void load(); }, []);

  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const stored = await api.uploadFile(file, undefined, file.type.startsWith("image/") ? "image" : file.type.startsWith("audio/") ? "audio" : file.type.startsWith("video/") ? "video" : "document");
      notify({ kind: "success", text: `${file.name} is available in the asset library.` });
      if (stored.download_url || stored.signed_url) notify({ kind: "info", text: "A direct access link was created for this asset." });
      await load();
    } catch (cause) {
      notify({ kind: "error", text: cause instanceof Error ? cause.message : "The file could not be uploaded." });
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  const rows = [
    ...assets.map((asset) => ({ id: asset.id, name: asset.filename, type: asset.kind || "asset", access: asset.signed_url || "", source: "Connected library" })),
    ...localAssets.map((asset) => ({ id: String(asset.id || asset.stored_as || asset.filename), name: String(asset.filename || asset.stored_as || "Local asset"), type: String(asset.kind || "local asset"), access: typeof asset.download_url === "string" ? api.websitePreviewUrl(asset.download_url) : "", source: "Local deployment storage" })),
  ];

  return <div><div className="page-header"><div><div className="micro-label">DAVID AI / WORK SYSTEMS</div><h1>Files & knowledge</h1><p>Upload source material once, then reopen the generated and indexed assets from one surface.</p></div><div className="header-actions"><span className="status-tag tag-blue"><span className="status-dot" /> {loading ? "Reading library" : `${rows.length} assets`}</span><label className="button button-primary"><Upload size={16} /> {uploading ? "Uploading…" : "Add knowledge"}<input type="file" hidden onChange={(event) => void upload(event)} disabled={uploading} /></label></div></div><div className="knowledge-banner panel-card"><div className="knowledge-icon"><Database size={24} /></div><div><div className="eyebrow-pill">ASSET ACCESS</div><h2>David keeps the result visible.</h2><p>{persistenceNote}</p></div><div className="knowledge-stat"><strong>{rows.length}</strong><span>available assets</span></div></div><div className="file-table panel-card"><div className="file-table-header"><span>Name</span><span>Type</span><span>Source</span><span>Access</span><span /></div>{loading ? <div className="padded-card"><span className="micro-label">LOADING ASSETS</span></div> : rows.length ? rows.map((file) => <div className="file-row" key={file.id}><span className="file-name"><span className="file-icon"><FileText size={16} /></span><strong>{file.name}</strong></span><span>{file.type}</span><span>{file.source}</span>{file.access ? <a href={file.access} target="_blank" rel="noreferrer" className="text-button"><Download size={14} /> Open</a> : <span className="text-muted">Stored</span>}<ChevronRight size={16} /></div>) : <div className="padded-card"><span className="micro-label">NO ASSETS YET</span><p>Use Add knowledge or generate an image, voice track, video, or website to create the first artifact.</p></div>}</div></div>;
}
