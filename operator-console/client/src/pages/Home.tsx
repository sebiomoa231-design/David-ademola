import { AIChatBox, type Message } from "@/components/AIChatBox";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/_core/hooks/useAuth";
import { startLogin } from "@/const";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { trpc } from "@/lib/trpc";
import { runOperatorStream } from "@/lib/operatorStreamController";
import { useOperatorVoice } from "@/hooks/useOperatorVoice";
import { CurrentTaskAccess, MemoryRemoveControl, OperatorActivityAccess, TranscriptClearControl } from "@/components/OperatorAccessControls";
import { PlanEvidenceList } from "@/components/PlanEvidenceList";
import { ConversationPlanSurface, ExecutionPlanSurface, RunPlanSurface } from "@/components/PlanViewSurfaces";
import { DemoModeIndicator } from "@/components/DemoModeIndicator";
import { OperatorShellStatus } from "@/components/OperatorShellStatus";
import { HomeShellStatus } from "@/components/HomeShellStatus";
import type { DavidResources, RemoteResult } from "@/lib/davidTypes";
import { COOKIE_NAME } from "@shared/const";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  AudioLines,
  Bot,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  CircleDot,
  Clapperboard,
  Clock3,
  Command,
  Compass,
  Database,
  FileText,
  FolderKanban,
  Gauge,
  Globe2,
  Image as ImageIcon,
  Layers3,
  LayoutDashboard,
  Library,
  Menu,
  MessageSquare,
  Mic,
  MonitorCog,
  MoreHorizontal,
  Palette,
  PanelLeftClose,
  PanelLeftOpen,
  Pause,
  Play,
  Plus,
  Rocket,
  Search,
  Send,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Square,
  Target,
  Video,
  Volume2,
  Wand2,
  X,
  Zap,
} from "lucide-react";
import type { CSSProperties } from "react";
import { useEffect, useMemo, useState } from "react";
import { useLocation } from "wouter";

type NavKey =
  | "overview" | "conversation" | "runs" | "projects" | "tasks" | "memory" | "files"
  | "creative" | "website" | "video" | "image" | "music" | "voice" | "enhance" | "edit"
  | "providers" | "activity" | "devices" | "settings" | "owner";

type NavItem = { key: NavKey; label: string; icon: typeof LayoutDashboard; path: string };
type OperatorCoreState = "idle" | "listening" | "thinking" | "planning" | "executing" | "verifying" | "speaking" | "complete" | "degraded";
type OperatorRuntimeStatus = { runtime: string; model: string; streaming: boolean; personality: string };
type PersistedPlan = { isMultiStep: boolean; steps: string[] };
type OperatorPreferences = { reducedMotion: boolean; highContrast: boolean; quietMode: boolean; compactLayout: boolean; demoMode: boolean; accent: "cyan" | "blue" | "mint" };

function parsePersistedPlan(value: unknown): PersistedPlan | null {
  if (typeof value !== "string") return null;
  try {
    const parsed = JSON.parse(value) as Record<string, unknown>;
    const steps = Array.isArray(parsed.steps) ? parsed.steps.filter((step): step is string => typeof step === "string" && Boolean(step.trim())).map((step) => step.trim()) : [];
    return steps.length ? { isMultiStep: parsed.isMultiStep === true, steps } : null;
  } catch {
    return null;
  }
}

const navGroups: { label: string; items: NavItem[] }[] = [
  {
    label: "COMMAND CENTER",
    items: [
      { key: "overview", label: "Overview", icon: LayoutDashboard, path: "/" },
      { key: "conversation", label: "Conversation", icon: MessageSquare, path: "/conversation" },
      { key: "runs", label: "Operator runs", icon: Bot, path: "/runs" },
    ],
  },
  {
    label: "WORK SYSTEMS",
    items: [
      { key: "projects", label: "Projects", icon: FolderKanban, path: "/projects" },
      { key: "tasks", label: "Tasks", icon: Target, path: "/tasks" },
      { key: "memory", label: "Memory", icon: BrainCircuit, path: "/memory" },
      { key: "files", label: "Files & knowledge", icon: Library, path: "/files" },
    ],
  },
  {
    label: "CREATIVE STUDIO",
    items: [
      { key: "creative", label: "Creative suite", icon: Palette, path: "/creative" },
      { key: "website", label: "Website builder", icon: Globe2, path: "/website" },
      { key: "video", label: "Video studio", icon: Video, path: "/video" },
      { key: "image", label: "Image studio", icon: ImageIcon, path: "/image" },
      { key: "music", label: "Music studio", icon: AudioLines, path: "/music" },
      { key: "voice", label: "Voice studio", icon: Volume2, path: "/voice" },
      { key: "enhance", label: "Enhance media", icon: Wand2, path: "/enhance" },
      { key: "edit", label: "Edit studio", icon: SlidersHorizontal, path: "/edit" },
    ],
  },
  {
    label: "SYSTEM",
    items: [
      { key: "providers", label: "Providers", icon: Zap, path: "/providers" },
      { key: "activity", label: "Activity log", icon: Activity, path: "/activity" },
      { key: "devices", label: "Devices", icon: MonitorCog, path: "/devices" },
      { key: "settings", label: "Settings", icon: Settings, path: "/settings" },
      { key: "owner", label: "Owner console", icon: ShieldCheck, path: "/owner" },
    ],
  },
];

const pageMeta: Record<NavKey, { eyebrow: string; title: string; description: string }> = {
  overview: { eyebrow: "DAVID AI OPERATOR / OS COMMAND CENTER", title: "A calmer way to run your environment.", description: "Give David an outcome. Inspect the operating plan, approvals, voice state, and evidence in one focused control surface." },
  conversation: { eyebrow: "DAVID AI OPERATOR / VOICE & TEXT", title: "Start with the outcome.", description: "Speak or type an operating-system request. David responds only through connected services and evidenced system states." },
  runs: { eyebrow: "DAVID AI OPERATOR / RUNS", title: "Execution, without the black box.", description: "Operator runs appear only after the connected runtime provides real status, plans, lifecycle events, and evidence." },
  projects: { eyebrow: "DAVID AI OPERATOR / WORK SYSTEMS", title: "Projects with a shared memory.", description: "Connect goals, files, decisions, and active operator work in a single project context." },
  tasks: { eyebrow: "DAVID AI OPERATOR / WORK SYSTEMS", title: "The execution queue.", description: "Track what is ready, blocked, in review, and awaiting an approval boundary." },
  memory: { eyebrow: "DAVID AI OPERATOR / WORK SYSTEMS", title: "Memory with provenance.", description: "Facts, preferences, decisions, and learning should always stay attributable and user-controlled." },
  files: { eyebrow: "DAVID AI OPERATOR / WORK SYSTEMS", title: "Knowledge, ready when it matters.", description: "Bring sources into the workspace once; connect them to projects, reasoning, and reviewable outputs." },
  creative: { eyebrow: "DAVID AI OPERATOR / CREATIVE STUDIO", title: "One brief. Multiple finished surfaces.", description: "Turn an idea into a coordinated website, script, visual system, voice plan, and deliverable review." },
  website: { eyebrow: "DAVID AI OPERATOR / CREATIVE STUDIO", title: "Build the system behind the page.", description: "Define the audience, outcome, hierarchy, and implementation plan before a live site is generated." },
  video: { eyebrow: "DAVID AI OPERATOR / CREATIVE STUDIO", title: "Shape the story before the render.", description: "Create a reviewable script, shot sequence, captions, and delivery plan from a single creative brief." },
  image: { eyebrow: "DAVID AI OPERATOR / CREATIVE STUDIO", title: "Create a visual language, not one-off assets.", description: "Capture reference, composition, palette, subject, and revision rules before an image task runs." },
  music: { eyebrow: "DAVID AI OPERATOR / CREATIVE STUDIO", title: "Plan the sound of the idea.", description: "Describe mood, pacing, instrumentation, rights requirements, and final duration in a structured cue sheet." },
  voice: { eyebrow: "DAVID AI OPERATOR / CREATIVE STUDIO", title: "Voice output with a clear control boundary.", description: "David can surface configured text-to-speech status without placing a microphone control in the workspace." },
  enhance: { eyebrow: "DAVID AI OPERATOR / CREATIVE STUDIO", title: "Improve the source, preserve the proof.", description: "Prepare a scoped enhancement request with originals, output settings, and an approval-ready comparison." },
  edit: { eyebrow: "DAVID AI OPERATOR / CREATIVE STUDIO", title: "Edit with intent.", description: "Translate a creative direction into a reviewable edit plan before any source is changed." },
  providers: { eyebrow: "DAVID AI OPERATOR / SYSTEM", title: "Capability health at a glance.", description: "Only providers returned by the connected service are marked available. Missing routes remain plainly unavailable." },
  activity: { eyebrow: "DAVID AI OPERATOR / SYSTEM", title: "Everything David does, inspectable.", description: "Review health checks, approvals, runs, tool calls, and verification events with sources and timestamps." },
  devices: { eyebrow: "DAVID AI OPERATOR / SYSTEM", title: "Trusted surfaces, explicit scope.", description: "Manage the devices and clients that may receive notifications or controlled operator output." },
  settings: { eyebrow: "DAVID AI OPERATOR / SYSTEM", title: "Tune the operating model.", description: "Control local presentation preferences and review backend-dependent operating controls as the connected runtime expands." },
  owner: { eyebrow: "DAVID AI OPERATOR / OWNER CONSOLE", title: "The governance plane.", description: "Provider health, execution policy, audit posture, and platform ownership belong in the open." },
};

const starters = [
  "Prepare a decision-ready weekly operating brief",
  "Turn this idea into a launch page plan",
  "Map a content workflow from research to publish review",
  "Audit a project and identify the next approval",
];

function normalizePath(path: string): NavKey {
  const segment = path.replace(/^\//, "").split("/")[0] || "overview";
  const found = navGroups.flatMap((group) => group.items).find((item) => item.key === segment || item.path === `/${segment}`);
  return found?.key ?? "overview";
}

function Signal({ state, label }: { state: "online" | "degraded" | "offline" | "pending"; label: string }) {
  return <span className={cn("signal", `signal-${state}`)}><i />{label}</span>;
}

function RemoteStateCard({ label, result, icon: Icon }: { label: string; result?: RemoteResult<unknown>; icon: typeof Activity }) {
  const state = result?.state ?? "unavailable";
  const stateLabel = state === "ready" ? "Connected" : state === "degraded" ? "Degraded" : "Unavailable";
  return (
    <div className="surface-card resource-card">
      <div className="resource-icon"><Icon size={16} /></div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2"><p className="resource-label">{label}</p><Badge className={cn("state-badge", `state-${state}`)}>{stateLabel}</Badge></div>
        <p className="resource-detail">{result?.message ?? "Checking connected service…"}</p>
      </div>
    </div>
  );
}

function workspaceResult(data: unknown[] | undefined, error: unknown, noun: string): RemoteResult<unknown[]> {
  if (data) return { state: "ready", status: 200, data, message: `${data.length} ${noun}${data.length === 1 ? "" : "s"} saved in this workspace.` };
  if (error) return { state: "degraded", status: null, data: null, message: `David could not load ${noun} records.` };
  return { state: "unavailable", status: null, data: null, message: `Checking ${noun} records…` };
}

function DavidCore({ state, amplitude = 0, detail }: { state: OperatorCoreState; amplitude?: number; detail: string }) {
  const label = state === "idle" ? "STANDBY" : state.toUpperCase();
  return (
    <div className={cn("core-stage", `core-${state}`)} style={{ "--voice-amplitude": String(amplitude) } as CSSProperties} aria-label={`David AI Operator core state: ${label}`}>
      <div className="core-grid" />
      <div className="core-ring core-ring-a" /><div className="core-ring core-ring-b" /><div className="core-ring core-ring-c" />
      <div className="core-orb"><span className="core-orb-inner" /><span className="core-orb-glint" /></div>
      <div className="core-readout top">DAVID AI OPERATOR // {label}</div>
      <div className="core-waveform" aria-hidden="true">{Array.from({ length: 21 }, (_, index) => <i key={index} style={{ "--wave-index": String(index), "--voice-amplitude": String(amplitude) } as CSSProperties} />)}</div>
      <div className="core-readout bottom" role="status" aria-live="polite">{detail}</div>
      <div className="core-coordinate left">VOICE / {state === "listening" ? "INPUT LIVE" : state === "speaking" ? "OUTPUT LIVE" : "STANDING BY"}</div><div className="core-coordinate right">OS CORE / GOVERNED</div>
    </div>
  );
}

function OrchestrationDiagnostics({ state, summary, plan }: { state: OperatorCoreState; summary: string; plan: PersistedPlan | null }) {
  const active = ["thinking", "planning", "executing", "verifying", "speaking"].includes(state);
  if (!active) return null;
  const stageLabel = state === "thinking" ? "ANALYSING REQUEST" : state === "planning" ? "ASSEMBLING PLAN" : state === "executing" ? "COMPOSING RESPONSE" : state === "verifying" ? "VERIFYING DELIVERY" : "VOICE RESPONSE";
  return <div className="orchestration-diagnostics" aria-live="polite" aria-label="Live David AI Operator orchestration diagnostics"><section className="core-diagnostic-panel core-diagnostic-left"><p>ORCHESTRATION</p><strong>{stageLabel}</strong><span>{summary}</span><div className="diagnostic-scan" /></section><section className="core-diagnostic-panel core-diagnostic-right"><p>RUN EVIDENCE</p>{plan ? <ol>{plan.steps.slice(0, 3).map((step, index) => <li key={`${index}-${step}`}><i />{step}</li>)}</ol> : <span>Awaiting persisted plan evidence.</span>}</section></div>;
}

function Dashboard({ onNavigate, onObjective, status, resources, isLoading, coreState, lifecycleSummary, voiceAmplitude, activePlan }: {
  onNavigate: (path: string) => void;
  onObjective: (objective: string) => void;
  status?: OperatorRuntimeStatus;
  resources?: DavidResources;
  isLoading: boolean;
  coreState: OperatorCoreState;
  lifecycleSummary: string;
  voiceAmplitude: number;
  activePlan: PersistedPlan | null;
}) {
  const online = status?.runtime === "ready";
  const tts = false;
  const resourceCards = [
    { label: "Operator runs", result: resources?.runs, icon: Bot },
    { label: "Projects", result: resources?.projects, icon: FolderKanban },
    { label: "Memory", result: resources?.memories, icon: BrainCircuit },
    { label: "Provider directory", result: resources?.providers, icon: Zap },
  ];

  return <>
    <section className="dashboard-grid">
      <div className="hero-panel surface-card">
        <div className="panel-kicker"><span>OPERATIONAL CORE</span><span className="line" /><span>01 / 09</span></div>
        <DavidCore state={coreState} amplitude={voiceAmplitude} detail={lifecycleSummary} />
        <OrchestrationDiagnostics state={coreState} summary={lifecycleSummary} plan={activePlan} />
        <div className="hero-bottom">
          <div><p className="eyebrow-small">SYSTEM STATE</p><div className="flex items-center gap-2 mt-1"><Signal state={online ? "online" : isLoading ? "pending" : "degraded"} label={online ? "ONLINE" : isLoading ? "CHECKING" : "DEGRADED"} /><span className="technical-copy">{lifecycleSummary}</span></div></div>
          <button className="text-action" onClick={() => onNavigate("/activity")}>Inspect activity <ArrowUpRight size={14} /></button>
        </div>
      </div>
      <aside className="status-rail">
        <div className="surface-card status-card">
          <div className="section-heading"><div><p className="eyebrow-small">SYSTEM SIGNAL</p><h3>Live surface</h3></div><Gauge size={18} /></div>
          <Separator className="my-4 bg-white/10" />
          {isLoading ? <><Skeleton className="h-10 bg-white/10" /><Skeleton className="h-10 mt-3 bg-white/10" /></> : <div className="space-y-4">
            <div className="signal-row"><span>David runtime</span><Signal state={online ? "online" : "degraded"} label={online ? "READY" : "LIMITED"} /></div>
            <div className="signal-row"><span>Reasoning model</span><span className="technical-copy">{status?.model ?? "CHECKING"}</span></div>
            <div className="signal-row"><span>Response stream</span><Signal state={status?.streaming ? "online" : "offline"} label={status?.streaming ? "ENABLED" : "CHECKING"} /></div>
          </div>}
        </div>
        <div className="surface-card mission-card">
          <div className="section-heading"><div><p className="eyebrow-small">MISSION CONTROL</p><h3>Give David an outcome.</h3></div><Target size={18} /></div>
          <p>David translates a clear objective into a plan, visible work, and an approval-aware result.</p>
          <Button onClick={() => onNavigate("/conversation")} className="primary-action w-full">Open conversation <ChevronRight size={16} /></Button>
        </div>
      </aside>
    </section>
    <section className="dashboard-lower">
      <div className="surface-card quick-panel">
        <div className="section-heading"><div><p className="eyebrow-small">START HERE</p><h3>What should move forward?</h3></div><Command size={18} /></div>
        <div className="quick-grid">
          {starters.map((prompt) => <button key={prompt} className="quick-action" onClick={() => onObjective(prompt)}><span>{prompt}</span><ArrowUpRight size={15} /></button>)}
        </div>
      </div>
      <div className="surface-card resources-panel">
        <div className="section-heading"><div><p className="eyebrow-small">CONNECTED CONTRACTS</p><h3>Availability is explicit.</h3></div><ShieldCheck size={18} /></div>
        <div className="resource-grid">{resourceCards.map((card) => <RemoteStateCard key={card.label} {...card} />)}</div>
      </div>
    </section>
    <section className="surface-card hub-reference-panel">
      <div className="section-heading"><div><p className="eyebrow-small">DAVID AI / REACTIVE HUB STATE SYSTEM</p><h3>The command-center visual language.</h3></div><Sparkles size={18} /></div>
      <img src="/manus-storage/david_ai_hub_state_sequence_c05de795.png" alt="David AI Reactive Hub State System: standby, listening, thinking, planning, executing, verifying, complete and degraded" />
      <p>The central hub follows these states while David waits, interprets an objective, plans, responds, verifies the outcome, or reports a limitation.</p>
    </section>
  </>;
}

function Conversation({ messages, onSend, pending, status, conversations, activeConversationId, onSelectConversation, memories, selectedMemoryIds, onToggleMemory, activePlan, voice, voiceOutputEnabled, onToggleVoiceOutput }: { messages: Message[]; onSend: (message: string) => void; pending: boolean; status?: OperatorRuntimeStatus; conversations: Array<{ id: string; title: string }>; activeConversationId?: string; onSelectConversation: (id: string) => void; memories: Array<{ id: string; content: string; kind: string }>; selectedMemoryIds: string[]; onToggleMemory: (id: string) => void; activePlan: PersistedPlan | null; voice: ReturnType<typeof useOperatorVoice>; voiceOutputEnabled: boolean; onToggleVoiceOutput: () => void }) {
  const chatReady = status?.runtime === "ready";
  return <div className="conversation-layout">
    <section className="surface-card conversation-card">
      <div className="conversation-head"><div><p className="eyebrow-small">TEXT INTERFACE</p><h2>Conversation with David</h2></div><Signal state={chatReady ? "online" : "degraded"} label={chatReady ? "UPSTREAM CHECKED" : "UPSTREAM LIMITED"} /></div>
      <AIChatBox messages={messages} onSendMessage={onSend} isLoading={pending} height="calc(100vh - 274px)" className="david-chat" placeholder="Describe an outcome, question, or creative direction…" suggestedPrompts={starters} />
    </section>
    <aside className="conversation-aside space-y-4">
      <div className="surface-card detail-card"><p className="eyebrow-small">INTERACTION MODEL</p><h3>Text first, governed by design.</h3><p>Conversation, plans, approvals, tool activity, and results should share one traceable run contract.</p></div>
      <div className="surface-card detail-card"><p className="eyebrow-small">CONNECTION NOTE</p><p className="technical-copy">{chatReady ? `David is ready with ${status?.model}.` : "Checking David AI runtime…"}</p></div>
      <div className="surface-card detail-card"><p className="eyebrow-small">SAVED CONVERSATIONS</p>{conversations.length ? <div className="conversation-history">{conversations.slice(0, 7).map((conversation) => <button key={conversation.id} className={cn("conversation-history-item", conversation.id === activeConversationId && "conversation-history-active")} onClick={() => onSelectConversation(conversation.id)}>{conversation.title}</button>)}</div> : <p className="technical-copy">No saved conversations yet.</p>}</div>
      <div className="surface-card detail-card"><p className="eyebrow-small">MEMORY SCOPE</p><p className="technical-copy">Only selected memories are included in the next request.</p>{memories.length ? <div className="memory-scope-list">{memories.slice(0, 8).map((memory) => <button key={memory.id} className={cn("memory-scope-item", selectedMemoryIds.includes(memory.id) && "memory-scope-selected")} role="checkbox" aria-checked={selectedMemoryIds.includes(memory.id)} onClick={() => onToggleMemory(memory.id)}><span>{selectedMemoryIds.includes(memory.id) ? "✓" : "+"}</span>{memory.content}</button>)}</div> : <p className="technical-copy">Save a memory to make it available for explicit use.</p>}</div>
      <ConversationPlanSurface plan={activePlan} />
      <div className="surface-card detail-card voice-operator-card"><p className="eyebrow-small">VOICE OPERATOR</p><div className="voice-status-row"><Signal state={voice.state === "degraded" ? "degraded" : voice.state === "idle" || voice.state === "cancelled" ? "offline" : "online"} label={voice.state.toUpperCase()} /><span className="voice-amplitude" style={{ "--voice-amplitude": String(voice.amplitude) } as CSSProperties} aria-label={`Voice amplitude ${Math.round(voice.amplitude * 100)} percent`} /></div><p aria-live="polite">{voice.error ?? (voice.state === "listening" ? "Listening through your microphone. Tap stop when you finish speaking." : voice.state === "transcribing" ? "Sending your recording to the configured speech service." : voice.state === "reasoning" ? "David AI Operator is analysing the request and preparing a verified response." : voice.state === "speaking" ? "Kenny voice output is active. You can stop or pause it at any time." : voice.state === "paused" ? "Kenny voice output is paused. Resume or stop it when ready." : voice.state === "cancelled" ? "Voice output was cancelled. David AI Operator has returned to standby." : "Use the microphone to speak an operating-system request.")}</p>{voice.transcript && <div className="voice-transcript"><span>LAST TRANSCRIPT</span><p>{voice.transcript}</p><TranscriptClearControl onClear={voice.clearTranscript} /></div>}<div className="voice-actions"><Button className="primary-action" disabled={!voice.isSupported || pending || voice.state === "transcribing"} onClick={voice.state === "listening" ? voice.stopListening : voice.startListening}>{voice.state === "listening" ? <Square size={15} /> : <Mic size={15} />}{voice.state === "listening" ? "Stop listening" : "Speak to David"}</Button>{voice.state === "speaking" && <><button className="subtle-button" onClick={voice.pauseSpeaking}><Pause size={14} /> Pause</button><button className="subtle-button" onClick={voice.interruptSpeaking}><Square size={14} /> Stop voice</button></>}{voice.state === "paused" && <><button className="subtle-button" onClick={() => void voice.resumeSpeaking()}><Play size={14} /> Resume</button><button className="subtle-button" onClick={voice.interruptSpeaking}><Square size={14} /> Stop voice</button></>}</div><label className="voice-toggle"><input type="checkbox" checked={voiceOutputEnabled} onChange={onToggleVoiceOutput} /> Speak David’s responses</label></div>
    </aside>
  </div>;
}

function PersistentWorkspace({ page, onNavigate }: { page: "memory" | "projects" | "tasks" | "runs"; onNavigate: (path: string) => void }) {
  const [draft, setDraft] = useState("");
  const [selectedRunId, setSelectedRunId] = useState<string | undefined>();
  const utils = trpc.useUtils();
  const memories = trpc.david.memory.list.useQuery(undefined, { enabled: page === "memory" });
  const projects = trpc.david.projects.list.useQuery(undefined, { enabled: page === "projects" || page === "tasks" });
  const tasks = trpc.david.tasks.list.useQuery(undefined, { enabled: page === "tasks" });
  const runs = trpc.david.runs.list.useQuery(undefined, { enabled: page === "runs" });
  const resolvedRunId = selectedRunId ?? runs.data?.[0]?.id;
  const selectedRunPlan = parsePersistedPlan(runs.data?.find((run) => run.id === resolvedRunId)?.planData);
  const runEvents = trpc.david.runs.events.useQuery({ runId: resolvedRunId ?? "" }, { enabled: page === "runs" && Boolean(resolvedRunId), retry: false });
  const addMemory = trpc.david.memory.create.useMutation({ onSuccess: () => { setDraft(""); void utils.david.memory.list.invalidate(); } });
  const addProject = trpc.david.projects.create.useMutation({ onSuccess: () => { setDraft(""); void utils.david.projects.list.invalidate(); } });
  const addTask = trpc.david.tasks.create.useMutation({ onSuccess: () => { setDraft(""); void utils.david.tasks.list.invalidate(); } });
  const updateTask = trpc.david.tasks.update.useMutation({ onSuccess: () => void utils.david.tasks.list.invalidate() });
  const deleteMemory = trpc.david.memory.delete.useMutation({ onSuccess: () => void utils.david.memory.list.invalidate() });
  const isBusy = addMemory.isPending || addProject.isPending || addTask.isPending;
  const rows = page === "memory" ? memories.data ?? [] : page === "projects" ? projects.data ?? [] : page === "tasks" ? tasks.data ?? [] : runs.data ?? [];
  const title = page === "memory" ? "Add a memory" : page === "projects" ? "Create a project" : page === "tasks" ? "Create a task" : "Operator execution history";
  const placeholder = page === "memory" ? "For example: I prefer concise weekly summaries" : page === "projects" ? "Project name" : "Task title";
  const submit = () => {
    const value = draft.trim();
    if (!value) return;
    if (page === "memory") addMemory.mutate({ content: value, kind: "note" });
    if (page === "projects") addProject.mutate({ name: value });
    if (page === "tasks") addTask.mutate({ title: value });
  };
  return <div className="workspace-layout">
    <section className="surface-card workspace-primary">
      <div className="workspace-toolbar"><div><p className="eyebrow-small">DAVID AI OPERATOR / PERSISTENT WORKSPACE</p><h2>{title}</h2><p>These records are saved to your secure David AI Operator workspace and remain attributable to your account.</p></div><button className="subtle-button" onClick={() => onNavigate("/conversation")}><MessageSquare size={15} /> Ask David</button></div>
      <div className="workspace-canvas workspace-live">
        {page !== "runs" && <div className="record-composer"><Input value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") submit(); }} placeholder={placeholder} /><Button className="primary-action" disabled={!draft.trim() || isBusy} onClick={submit}><Plus size={15} /> Save</Button></div>}
        <div className="record-stack">{rows.length === 0 ? <div className="empty-workspace"><div className="empty-orbit"><Database size={22} /></div><p className="eyebrow-small">NO SAVED RECORDS</p><h3>{page === "runs" ? "David AI Operator has not completed a run yet." : "This workspace is ready."}</h3><p>{page === "runs" ? "Start a conversation or voice request to create a real LLM-backed operator run." : "Add the first item above or ask David to help structure it."}</p></div> : rows.map((row) => {
          const item = row as Record<string, unknown>;
          const main = String(item.content ?? item.name ?? item.title ?? item.objective ?? "David AI record");
          const sub = String(item.description ?? item.plan ?? item.kind ?? item.status ?? "Saved workspace record");
          const plan = page === "runs" ? parsePersistedPlan(item.planData) : null;
          return <div className={cn("record-row", page === "runs" && String(item.id) === resolvedRunId && "record-row-selected")} key={String(item.id)} onClick={() => page === "runs" && setSelectedRunId(String(item.id))} role={page === "runs" ? "button" : undefined} tabIndex={page === "runs" ? 0 : undefined}><div className="record-row-icon">{page === "memory" ? <BrainCircuit size={16} /> : page === "projects" ? <FolderKanban size={16} /> : page === "tasks" ? <Target size={16} /> : <Bot size={16} />}</div><div className="flex-1 min-w-0"><h3>{main}</h3><p>{sub}</p><RunPlanSurface plan={plan} /></div>{page === "memory" && <MemoryRemoveControl onRemove={() => deleteMemory.mutate({ id: String(item.id) })} />}{page === "tasks" && item.status !== "done" && <button className="row-action" onClick={() => updateTask.mutate({ id: String(item.id), status: "done" })}>Mark done</button>}<Badge className="state-badge state-ready">{String(item.status ?? item.kind ?? "saved").replace("_", " ")}</Badge></div>;
        })}</div>
        {page === "runs" && resolvedRunId && <section className="execution-theater" aria-label="David AI Operator Execution Theater"><div className="section-heading"><div><p className="eyebrow-small">OPERATOR EXECUTION THEATER</p><h3>Persisted lifecycle</h3></div><Signal state={runEvents.isLoading ? "pending" : runEvents.isError ? "degraded" : "online"} label={runEvents.isLoading ? "LOADING" : runEvents.isError ? "UNAVAILABLE" : "PERSISTED"} /></div><ExecutionPlanSurface plan={selectedRunPlan} />{runEvents.data?.length ? <ol className="event-rail">{runEvents.data.map((event) => <li key={event.id} className={cn("event-item", `event-${event.state}`)}><span className="event-dot" /><div><p>{event.summary}</p><small>{event.type.replaceAll("_", " ")} · {event.actor}{event.provider ? ` · ${event.provider}` : ""}</small></div><time>{new Date(event.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</time></li>)}</ol> : <p className="technical-copy theater-empty">No persisted events are available for this run yet.</p>}</section>}
      </div>
    </section>
    <aside className="workspace-aside"><div className="surface-card detail-card"><p className="eyebrow-small">STATE BOUNDARY</p><h3>Persistent and visible.</h3><p>David can retrieve stored context while keeping it editable, attributable, and separate from generated responses.</p></div><div className="surface-card detail-card"><p className="eyebrow-small">NEXT STEP</p><p>Use Conversation to give David an outcome, then inspect the resulting operator run here.</p><button className="text-action" onClick={() => onNavigate("/conversation")}>Open conversation <ArrowUpRight size={14} /></button></div></aside>
  </div>;
}

function ActivityWorkspace({ onNavigate }: { onNavigate: (path: string) => void }) {
  const runs = trpc.david.runs.list.useQuery();
  const latestRun = runs.data?.[0];
  const events = trpc.david.runs.events.useQuery({ runId: latestRun?.id ?? "" }, { enabled: Boolean(latestRun?.id), retry: false });
  const external = trpc.davidApi.status.useQuery(undefined, { retry: false });
  const health = external.data?.health as RemoteResult<unknown> | undefined;
  return <div className="workspace-layout">
    <section className="surface-card workspace-primary">
      <div className="workspace-toolbar"><div><p className="eyebrow-small">DAVID AI OPERATOR / ACTIVITY & HEALTH</p><h2>Evidence, not theatre.</h2><p>Recent lifecycle events are stored against each operator run. External provider health is shown separately from David’s built-in LLM runtime.</p></div><button className="subtle-button" onClick={() => onNavigate("/conversation")}><MessageSquare size={15} /> Start a run</button></div>
      <div className="workspace-canvas workspace-live"><div className="activity-grid"><div className="activity-health"><p className="eyebrow-small">LOCAL OPERATOR ACTIVITY</p><p>Persistent run events are available here as a local activity ledger. No external push-notification feed is represented as configured.</p><p className="eyebrow-small">EXTERNAL DAVID SERVICE</p><Signal state={health?.state === "ready" ? "online" : health?.state === "degraded" ? "degraded" : "offline"} label={health ? health.state.toUpperCase() : "CHECKING"} /><p>{health?.message ?? "Checking the optional external David service."}</p><p className="eyebrow-small">APPROVAL BOUNDARY</p><p>David can create only internal workspace records from direct requests. No external or irreversible action is declared complete without a connected capability and evidence.</p></div>{latestRun ? <div><p className="eyebrow-small">LATEST RUN</p><h3 className="activity-run-title">{latestRun.objective}</h3>{events.data?.length ? <ol className="event-rail activity-event-rail">{events.data.map((event) => <li key={event.id} className={cn("event-item", `event-${event.state}`)}><span className="event-dot" /><div><p>{event.summary}</p><small>{event.type.replaceAll("_", " ")} · {event.actor}</small></div><time>{new Date(event.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</time></li>)}</ol> : <p className="technical-copy">Lifecycle events will appear as David processes the run.</p>}</div> : <div className="empty-workspace"><div className="empty-orbit"><Activity size={22} /></div><p className="eyebrow-small">NO RECENT EVIDENCE</p><h3>No operator runs have been recorded.</h3><p>Start a conversation to create an attributable David AI Operator run.</p></div>}</div></div>
    </section>
    <aside className="workspace-aside"><div className="surface-card detail-card"><p className="eyebrow-small">SYSTEM HEALTH</p><h3>Local operator runtime</h3><p>David’s local server-side language model is checked independently from the optional external service.</p></div><div className="surface-card detail-card"><p className="eyebrow-small">AUDIT MODEL</p><p>Conversation history, workspace records, response plans, and lifecycle events persist by signed-in user.</p></div></aside>
  </div>;
}

const creativeBriefKinds = {
  creative: { label: "Creative direction", route: "/creative", icon: Palette },
  website: { label: "Website brief", route: "/website", icon: Globe2 },
  video: { label: "Video brief", route: "/video", icon: Video },
  image: { label: "Image brief", route: "/image", icon: ImageIcon },
  music: { label: "Music brief", route: "/music", icon: Volume2 },
} as const;

function CreativeBriefWorkspace({ page, onNavigate }: { page: keyof typeof creativeBriefKinds; onNavigate: (path: string) => void }) {
  const [draft, setDraft] = useState("");
  const utils = trpc.useUtils();
  const memories = trpc.david.memory.list.useQuery();
  const addBrief = trpc.david.memory.create.useMutation({ onSuccess: () => { setDraft(""); void utils.david.memory.list.invalidate(); } });
  const removeBrief = trpc.david.memory.delete.useMutation({ onSuccess: () => void utils.david.memory.list.invalidate() });
  const current = creativeBriefKinds[page];
  const Icon = current.icon;
  const prefix = `[${current.label}]`;
  const briefs = (memories.data ?? []).filter((memory) => memory.content.startsWith(prefix));
  const saveBrief = () => {
    const value = draft.trim();
    if (!value) return;
    addBrief.mutate({ kind: "note", content: `${prefix}\n${value}` });
  };
  return <div className="workspace-layout">
    <section className="surface-card workspace-primary">
      <div className="workspace-toolbar"><div><p className="eyebrow-small">DAVID AI OPERATOR / CREATIVE BRIEF</p><h2>{current.label} workspace</h2><p>Capture the intended audience, outcome, tone, references, and constraints. David AI Operator stores the brief locally; generation remains unavailable until a connected capability provides evidence.</p></div><button className="subtle-button" onClick={() => onNavigate("/conversation")}><MessageSquare size={15} /> Ask David to plan it</button></div>
      <div className="workspace-canvas workspace-live creative-brief-canvas"><div className="creative-brief-tabs" role="tablist" aria-label="Creative brief type">{Object.entries(creativeBriefKinds).map(([key, item]) => <button key={key} role="tab" aria-selected={key === page} className={cn("creative-brief-tab", key === page && "creative-brief-tab-active")} onClick={() => onNavigate(item.route)}>{item.label}</button>)}</div><div className="creative-brief-composer"><textarea value={draft} onChange={(event) => setDraft(event.target.value)} placeholder={`Describe the ${current.label.toLowerCase()}: audience, objective, visual or sonic direction, deliverables, and constraints.`} /><Button className="primary-action" disabled={!draft.trim() || addBrief.isPending} onClick={saveBrief}><Plus size={15} /> Save brief</Button></div><div className="record-stack">{briefs.length ? briefs.map((brief) => <div className="record-row" key={brief.id}><div className="record-row-icon"><Icon size={16} /></div><div className="flex-1 min-w-0"><h3>{current.label}</h3><p className="creative-brief-content">{brief.content.slice(prefix.length).trim()}</p></div><MemoryRemoveControl onRemove={() => removeBrief.mutate({ id: brief.id })} /></div>) : <div className="empty-workspace"><div className="empty-orbit"><Icon size={22} /></div><p className="eyebrow-small">NO SAVED BRIEF</p><h3>Start with a clear creative direction.</h3><p>Your saved brief will stay available in this local operator workspace. A generation result will only appear after a supported backend capability is connected.</p></div>}</div></div>
    </section>
    <aside className="workspace-aside"><div className="surface-card detail-card"><p className="eyebrow-small">AVAILABLE NOW</p><h3>Creative planning</h3><p>Brief capture, David’s conversational planning, persistent context, and reviewable direction are available locally.</p></div><div className="surface-card detail-card"><p className="eyebrow-small">BACKEND BOUNDARY</p><p>Website, video, image, and music generation are not shown as active until the authoritative backend exposes a verified capability and output contract.</p></div></aside>
  </div>;
}

function DemoModeBoundary({ enabled, onChange }: { enabled: boolean; onChange: () => void }) {
  return <div className={cn("demo-mode-boundary", enabled && "demo-mode-enabled")} role="note"><div><p className="eyebrow-small">DEMONSTRATION MODE</p><h3>{enabled ? "Presentation mode is on." : "Presentation mode is off."}</h3><p>Enabling this changes only the David AI Operator presentation label. It does not simulate, unlock, or report any external provider, device, action, or backend record as available.</p></div><label className="setting-toggle"><input type="checkbox" checked={enabled} onChange={onChange} /><span><strong>Label this session as a demonstration</strong><small>Keep all capability status based on live evidence.</small></span></label></div>;
}

function Workspace({ page, resources, status, onNavigate, preferences, onPreferencesChange }: { page: NavKey; resources?: DavidResources; status?: OperatorRuntimeStatus; onNavigate: (path: string) => void; preferences: OperatorPreferences; onPreferencesChange: (next: Partial<OperatorPreferences>) => void }) {
  if (page === "memory" || page === "projects" || page === "tasks" || page === "runs") return <PersistentWorkspace page={page} onNavigate={onNavigate} />;
  if (page === "activity") return <ActivityWorkspace onNavigate={onNavigate} />;
  if (page === "creative" || page === "website" || page === "video" || page === "image" || page === "music") return <CreativeBriefWorkspace page={page} onNavigate={onNavigate} />;
  const meta = pageMeta[page];
  const resource = page === "providers" ? resources?.providers : undefined;
  const isVoice = page === "voice";
  const isSettings = page === "settings";
  const voiceStatus = trpc.davidApi.voice.status.useQuery(undefined, { enabled: isVoice, retry: false });
  const voiceResult = voiceStatus.data as RemoteResult<Record<string, unknown>> | undefined;
  const generatedRows = resource?.state === "ready" && Array.isArray(resource.data) ? resource.data : [];
  const cards = isVoice ? [
    { label: "Text-to-speech", value: voiceResult?.data?.tts_configured === true ? "Configured" : voiceStatus.isLoading ? "Checking" : "Unavailable", detail: voiceResult?.data?.tts_configured === true ? `Render voice provider: ${String(voiceResult.data.tts_provider ?? "configured")}.` : voiceResult?.message ?? "Checking the secure Render voice service." },
    { label: "Speech-to-text", value: voiceResult?.data?.stt_configured === true ? "Configured" : voiceStatus.isLoading ? "Checking" : "Unavailable", detail: voiceResult?.data?.stt_configured === true ? `Transcription provider: ${String(voiceResult.data.stt_provider ?? "configured")}.` : voiceResult?.message ?? "Microphone capture is available from the Voice Operator controls." },
  ] : [
    { label: "Backend contract", value: resource?.state === "ready" ? "Available" : "Unavailable", detail: resource?.message ?? "This workspace awaits a connected backend route." },
    { label: "Execution truth", value: "Preserved", detail: "No completed state is shown without upstream evidence." },
  ];

  return <div className="workspace-layout">
    <section className="surface-card workspace-primary">
      <div className="workspace-toolbar"><div><p className="eyebrow-small">{meta.eyebrow}</p><h2>{meta.title}</h2><p>{meta.description}</p></div><button className="subtle-button" onClick={() => onNavigate("/conversation")}>{isVoice ? <><Mic size={15} /> Open voice operator</> : <><MessageSquare size={15} /> Start with text</>}</button></div>
      <div className="workspace-canvas">
        {isSettings ? <div className="operator-settings" aria-label="David AI Operator interface controls"><div className="settings-copy"><p className="eyebrow-small">INTERFACE PREFERENCES</p><h3>Visual control remains local to this browser.</h3><p>These settings change only the David AI Operator presentation layer. They do not claim to alter external runtime or voice-provider configuration.</p></div><div className="setting-toggle-grid"><label className="setting-toggle"><input type="checkbox" checked={preferences.reducedMotion} onChange={() => onPreferencesChange({ reducedMotion: !preferences.reducedMotion })} /><span><strong>Reduced motion</strong><small>Replace continuous HUD movement with calm static indicators.</small></span></label><label className="setting-toggle"><input type="checkbox" checked={preferences.highContrast} onChange={() => onPreferencesChange({ highContrast: !preferences.highContrast })} /><span><strong>High contrast</strong><small>Increase text and boundary contrast for easier reading.</small></span></label><label className="setting-toggle"><input type="checkbox" checked={preferences.quietMode} onChange={() => onPreferencesChange({ quietMode: !preferences.quietMode })} /><span><strong>Quiet mode</strong><small>Keep responses on screen without automatically starting Kenny voice output.</small></span></label><label className="setting-toggle"><input type="checkbox" checked={preferences.compactLayout} onChange={() => onPreferencesChange({ compactLayout: !preferences.compactLayout })} /><span><strong>Compact layout</strong><small>Reduce decorative panel height while retaining all controls.</small></span></label></div><div className="accent-picker"><div><p className="eyebrow-small">ACCENT SIGNAL</p><p>Choose the presentation accent for this session.</p></div><div role="group" aria-label="Interface accent color" className="accent-options">{(["cyan", "blue", "mint"] as const).map((accent) => <button key={accent} type="button" className={cn("accent-option", preferences.accent === accent && "accent-option-active")} aria-pressed={preferences.accent === accent} onClick={() => onPreferencesChange({ accent })}><i /><span>{accent}</span></button>)}</div></div></div> : isVoice ? <div className="empty-workspace"><div className="empty-orbit"><AudioLines size={22} /></div><p className="eyebrow-small">VOICE RUNTIME</p><h3>{voiceResult?.data?.tts_configured === true && voiceResult?.data?.stt_configured === true ? "Voice services are ready at the configured Render backend." : "Voice services need attention."}</h3><p>{voiceResult?.data?.voice_style ? `Configured output profile: ${String(voiceResult.data.voice_style)}.` : voiceResult?.message ?? "Open Voice Operator to request microphone access and start a spoken operating-system request."}</p><Button className="primary-action" onClick={() => onNavigate("/conversation")}><Mic size={16} /> Speak to David</Button></div> : generatedRows.length > 0 ? <div className="data-list">{generatedRows.map((item, index) => <div className="data-row" key={index}><CircleDot size={16} /><pre>{JSON.stringify(item, null, 2)}</pre></div>)}</div> : <div className="empty-workspace"><div className="empty-orbit"><Sparkles size={22} /></div><p className="eyebrow-small">NO VERIFIED RECORDS</p><h3>{resource?.state === "ready" ? "The connected service returned an empty collection." : "This surface is waiting for a backend capability."}</h3><p>{resource?.message ?? "Create or connect the underlying capability before treating it as active."}</p></div>}
        {isSettings && <DemoModeBoundary enabled={preferences.demoMode} onChange={() => onPreferencesChange({ demoMode: !preferences.demoMode })} />}
      </div>
    </section>
    <aside className="workspace-aside">
      {cards.map((card) => <div className="surface-card detail-card" key={card.label}><p className="eyebrow-small">{card.label}</p><h3>{card.value}</h3><p>{card.detail}</p></div>)}
      <div className="surface-card detail-card"><p className="eyebrow-small">NEXT SAFE STEP</p><p>Connect this endpoint in the upstream David AI service, then expose evidence, approval state, and failure mode through the run contract.</p><button onClick={() => onNavigate("/activity")} className="text-action">Review activity model <ArrowUpRight size={14} /></button></div>
    </aside>
  </div>;
}

function SecureAccessGate({ loading }: { loading: boolean }) {
  return <div className="david-app secure-gate"><div className="ambient-grid" /><div className="ambient-noise" /><main className="secure-gate-card"><div className="secure-gate-mark"><Command size={28} /></div><p className="eyebrow">DAVID AI OPERATOR / SECURE WORKSPACE</p><h1>{loading ? "Confirming secure access" : "Your David AI workspace is private."}</h1><p>{loading ? "David is checking your session before loading memories, projects, tasks, and operator run history." : "Sign in to open your persistent command center and begin an authenticated David AI Operator conversation."}</p>{loading ? <Skeleton className="h-10 w-44 bg-cyan-200/10" /> : <Button className="primary-action" onClick={() => startLogin()}><ShieldCheck size={16} /> Secure sign in</Button>}</main></div>;
}

export default function Home() {
  const { loading: authLoading, isAuthenticated } = useAuth();
  const [location, setLocation] = useLocation();
  const [navOpen, setNavOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [coreState, setCoreState] = useState<OperatorCoreState>("idle");
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [isResponding, setIsResponding] = useState(false);
  const [selectedMemoryIds, setSelectedMemoryIds] = useState<string[]>([]);
  const [voiceOutputEnabled, setVoiceOutputEnabled] = useState(true);
  const [preferences, setPreferences] = useState<OperatorPreferences>({ reducedMotion: false, highContrast: false, quietMode: false, compactLayout: false, demoMode: false, accent: "cyan" });
  const [voiceIntent, setVoiceIntent] = useState<string | null>(null);
  const [lifecycleSummary, setLifecycleSummary] = useState("ACTIONS REMAIN REVIEWABLE");
  const [objective, setObjective] = useState("");
  const [now, setNow] = useState(() => new Date());
  const [messages, setMessages] = useState<Message[]>([{ role: "assistant", content: "I’m David. Share an outcome, question, or creative direction. I’ll only report connected capability as available when the backend provides evidence." }]);
  const active = normalizePath(location);
  const statusQuery = trpc.david.status.useQuery(undefined, { retry: false, refetchInterval: 60_000 });
  const externalStatusQuery = trpc.davidApi.status.useQuery(undefined, { retry: false, refetchInterval: 120_000 });
  const utils = trpc.useUtils();
  const conversationsQuery = trpc.david.conversations.list.useQuery(undefined, { retry: false, enabled: isAuthenticated });
  const memorySummaryQuery = trpc.david.memory.list.useQuery(undefined, { retry: false, enabled: isAuthenticated });
  const projectSummaryQuery = trpc.david.projects.list.useQuery(undefined, { retry: false, enabled: isAuthenticated });
  const taskSummaryQuery = trpc.david.tasks.list.useQuery(undefined, { retry: false, enabled: isAuthenticated });
  const runSummaryQuery = trpc.david.runs.list.useQuery(undefined, { retry: false, enabled: isAuthenticated });
  const chatMutation = trpc.david.chat.useMutation();
  const transcribeMutation = trpc.davidApi.voice.transcribe.useMutation();
  const synthesizeMutation = trpc.davidApi.voice.synthesize.useMutation();
  const conversationDetailQuery = trpc.david.conversations.get.useQuery({ id: conversationId ?? "" }, { retry: false, enabled: isAuthenticated && Boolean(conversationId) });

  const voice = useOperatorVoice({
    transcribe: async (audioBase64) => {
      const result = await transcribeMutation.mutateAsync({ audioBase64, language: "en" });
      const text = result.data?.text;
      if (result.state !== "ready" || typeof text !== "string") throw new Error(result.message || "Speech transcription is unavailable.");
      return text;
    },
    synthesize: async (text) => {
      const result = await synthesizeMutation.mutateAsync({ text });
      const payload = result.data;
      const audioBase64 = payload?.audio_base64;
      if (result.state !== "ready" || typeof audioBase64 !== "string") throw new Error(result.message || "Kenny voice output is unavailable.");
      return { audioBase64, audioFormat: typeof payload?.audio_format === "string" ? payload.audio_format : "mp3" };
    },
    onTranscript: (text) => setVoiceIntent(text),
  });

  useEffect(() => { const timer = window.setInterval(() => setNow(new Date()), 30_000); return () => window.clearInterval(timer); }, []);
  useEffect(() => {
    if (isResponding || !conversationDetailQuery.data) return;
    setMessages(conversationDetailQuery.data.messages.map((message) => ({ role: message.role, content: message.content })));
  }, [conversationDetailQuery.data, isResponding]);

  useEffect(() => {
    if (voice.state === "listening") { setCoreState("listening"); setLifecycleSummary("LISTENING — VOICE INPUT ACTIVE"); }
    if (voice.state === "transcribing") { setCoreState("thinking"); setLifecycleSummary("TRANSCRIBING — SENDING AUDIO TO DAVID AI OPERATOR"); }
    if (voice.state === "reasoning") { setCoreState("thinking"); setLifecycleSummary("ANALYSING REQUEST — PREPARING VERIFIED RESPONSE"); }
    if (voice.state === "speaking") { setCoreState("speaking"); setLifecycleSummary("KENNY VOICE OUTPUT ACTIVE"); }
    if (voice.state === "degraded") { setCoreState("degraded"); setLifecycleSummary("VOICE SERVICE NEEDS ATTENTION"); }
    if (voice.state === "cancelled") { setCoreState("complete"); setLifecycleSummary("VOICE OUTPUT CANCELLED — STANDING BY"); }
  }, [voice.state]);

  const navigate = (path: string) => { setLocation(path); setNavOpen(false); };
  const status = statusQuery.data as OperatorRuntimeStatus | undefined;
  const externalHealth = externalStatusQuery.data?.health as RemoteResult<unknown> | undefined;
  const resources: DavidResources = {
    runs: workspaceResult(runSummaryQuery.data, runSummaryQuery.error, "operator run"),
    projects: workspaceResult(projectSummaryQuery.data, projectSummaryQuery.error, "project"),
    memories: workspaceResult(memorySummaryQuery.data, memorySummaryQuery.error, "memory"),
    providers: externalHealth ? { state: externalHealth.state, status: externalHealth.status, data: { builtIn: status, external: externalStatusQuery.data }, message: `Built-in LLM: ${status?.runtime === "ready" ? status.model : "checking"}. External David service: ${externalHealth.message}` } : { state: status?.runtime === "ready" ? "ready" : "unavailable", status: status?.runtime === "ready" ? 200 : null, data: status, message: status?.runtime === "ready" ? `Built-in LLM active: ${status.model}. External David service is still being checked.` : "Checking the David AI model runtime…" },
  };
  const appStatus = status?.runtime === "ready" ? "online" : statusQuery.isLoading ? "pending" : "degraded";
  const activeRun = runSummaryQuery.data?.find((run) => run.conversationId === conversationId);
  const currentTask = taskSummaryQuery.data?.find((task) => task.status !== "done");
  const activePlan = parsePersistedPlan(activeRun?.planData);

  const sendObjective = async (value: string) => {
    if (!isAuthenticated) { startLogin(); return; }
    const text = value.trim();
    if (!text || isResponding) return;
    setMessages((current) => [...current, { role: "user", content: text }]);
    setObjective("");
    setIsResponding(true);
    try {
      const rawSession = sessionStorage.getItem("manus-cookie") ?? "";
      const token = rawSession.split(";").map((value) => value.trim()).find((value) => value.startsWith(`${COOKIE_NAME}=`))?.slice(`${COOKIE_NAME}=`.length);
      setMessages((current) => [...current, { role: "assistant", content: "" }]);
      let spokenReply = "";
      await runOperatorStream({ message: text, conversationId, memoryIds: selectedMemoryIds, token, beginReasoning: voice.beginReasoning, finishReasoning: voice.finishReasoning, setCoreState, setLifecycleSummary, onToken: (nextToken) => { spokenReply += nextToken; setMessages((current) => current.map((message, index) => index === current.length - 1 ? { ...message, content: `${message.content}${nextToken}` } : message)); }, onRunEvent: (payload) => { if (!payload.state) return; setCoreState(payload.state === "failed" ? "degraded" : payload.state); setLifecycleSummary(payload.summary?.toUpperCase() ?? "DAVID AI RUN UPDATED"); }, onComplete: (payload) => { setConversationId(payload.conversationId); void Promise.all([utils.david.memory.list.invalidate(), utils.david.projects.list.invalidate(), utils.david.tasks.list.invalidate(), utils.david.runs.list.invalidate(), utils.david.conversations.list.invalidate(), utils.david.conversations.get.invalidate()]); if (voiceOutputEnabled && !preferences.quietMode && spokenReply.trim()) void voice.speak(spokenReply); } });
    } catch (error) {
      setMessages((current) => [...current, { role: "assistant", content: `**David could not complete that request.** ${error instanceof Error ? error.message : "Please try again."}` }]);
      setCoreState("degraded");
      setLifecycleSummary("RUN DEGRADED — REVIEW THE RESPONSE FOR DETAILS");
    } finally {
      setIsResponding(false);
    }
  };

  useEffect(() => {
    if (!voiceIntent || isResponding) return;
    setVoiceIntent(null);
    void sendObjective(voiceIntent);
  }, [voiceIntent, isResponding]);

  const content = useMemo(() => {
    if (active === "overview") return <Dashboard onNavigate={navigate} onObjective={(value) => { navigate("/conversation"); void sendObjective(value); }} status={status} resources={resources} isLoading={statusQuery.isLoading} coreState={coreState} lifecycleSummary={lifecycleSummary} voiceAmplitude={voice.amplitude} activePlan={activePlan} />;
    if (active === "conversation") return <Conversation messages={messages} onSend={(value) => void sendObjective(value)} pending={isResponding} status={status} conversations={conversationsQuery.data ?? []} activeConversationId={conversationId} onSelectConversation={(id) => setConversationId(id)} memories={memorySummaryQuery.data ?? []} selectedMemoryIds={selectedMemoryIds} onToggleMemory={(id) => setSelectedMemoryIds((current) => current.includes(id) ? current.filter((item) => item !== id) : current.length < 12 ? [...current, id] : current)} activePlan={activePlan} voice={voice} voiceOutputEnabled={voiceOutputEnabled} onToggleVoiceOutput={() => setVoiceOutputEnabled((value) => !value)} />;
    return <Workspace page={active} resources={resources} status={status} onNavigate={navigate} preferences={preferences} onPreferencesChange={(next) => setPreferences((current) => ({ ...current, ...next }))} />;
  }, [active, status, resources, statusQuery.isLoading, coreState, messages, isResponding, lifecycleSummary, conversationsQuery.data, conversationId, memorySummaryQuery.data, selectedMemoryIds, activePlan, voice, voiceOutputEnabled, preferences]);

  if (authLoading || !isAuthenticated) return <SecureAccessGate loading={authLoading} />;

  return <div className={cn("david-app", preferences.reducedMotion && "david-reduced-motion", preferences.highContrast && "david-high-contrast", preferences.compactLayout && "david-compact-layout", preferences.demoMode && "david-demo-mode", `david-accent-${preferences.accent}`)}>
    <div className="ambient-grid" /><div className="ambient-noise" />
    <aside className={cn("sidebar-shell", collapsed && "sidebar-collapsed", navOpen && "sidebar-open")}>
      <div className="brand-row"><button className="brand-mark" onClick={() => navigate("/")} aria-label="Open David AI Operator overview"><span>D</span></button>{!collapsed && <div className="brand-copy"><span>DAVID</span><small>AI OPERATOR / OS</small></div>}<button className="collapse-button" onClick={() => setCollapsed((value) => !value)} aria-label="Collapse navigation">{collapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}</button></div>
      <nav className="nav-scroll" aria-label="Primary navigation">{navGroups.map((group) => <div className="nav-group" key={group.label}><p>{collapsed ? "•" : group.label}</p>{group.items.map((item) => { const Icon = item.icon; const selected = item.key === active; return <button key={item.key} className={cn("nav-item", selected && "nav-active")} onClick={() => navigate(item.path)} title={collapsed ? item.label : undefined}><Icon size={17} /><span>{item.label}</span>{selected && !collapsed && <ChevronRight size={14} />}</button>; })}</div>)}</nav>
      <div className="sidebar-footer"><div className="foot-status"><Signal state={appStatus} label={appStatus === "online" ? "SYSTEM ONLINE" : appStatus === "pending" ? "CHECKING" : "LIMITED MODE"} /></div>{!collapsed && <p>David only marks a capability active when the connected service returns evidence.</p>}</div>
    </aside>
    {navOpen && <button className="mobile-scrim" aria-label="Close navigation" onClick={() => setNavOpen(false)} />}
    <main className={cn("main-shell", collapsed && "main-expanded")}>
      <header className="topbar"><div className="topbar-left"><button className="mobile-menu" onClick={() => setNavOpen(true)} aria-label="Open navigation"><Menu size={20} /></button><div><p className="breadcrumb">{pageMeta[active].eyebrow}</p><span className="top-date">{now.toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" })} · {now.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" })}</span></div></div><div className="topbar-right"><HomeShellStatus demoMode={preferences.demoMode} health={externalHealth} /><Signal state={appStatus} label={appStatus === "online" ? "ONLINE" : appStatus === "pending" ? "CHECKING" : "DEGRADED"} /><OperatorActivityAccess onOpen={() => navigate("/activity")} /><CurrentTaskAccess taskTitle={currentTask?.title} onOpen={() => navigate("/tasks")} /><button className="icon-button" aria-label="Open David AI conversation" onClick={() => navigate("/conversation")}><Search size={17} /></button><button className="icon-button" aria-label="Open David AI settings" onClick={() => navigate("/settings")}><MoreHorizontal size={18} /></button></div></header>
      <div className="main-content"><section className="page-intro"><div><p className="eyebrow">{pageMeta[active].eyebrow}</p><h1>{pageMeta[active].title}</h1><p>{pageMeta[active].description}</p></div>{active === "overview" && <div className="objective-box"><Input value={objective} onChange={(event) => setObjective(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter") void sendObjective(objective); }} placeholder="Give David an outcome…" aria-label="David objective" /><Button disabled={!objective.trim() || isResponding} onClick={() => void sendObjective(objective)} className="primary-action"><Send size={15} /> Start</Button></div>}</section>{content}</div>
      <footer className="operator-telemetry" aria-label="David AI Operator telemetry"><span>LOCAL TIME <strong>{now.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</strong></span><span>VOICE <strong>{voice.state.toUpperCase()}</strong></span><span title={currentTask?.title}>CURRENT TASK <button className="telemetry-run" disabled={!currentTask} onClick={() => navigate("/tasks")}>{currentTask?.title ? currentTask.title.slice(0, 36) : "NO ACTIVE TASK"}</button></span><span title={activeRun?.objective}>RUN CONTEXT <button className="telemetry-run" disabled={!activeRun} onClick={() => navigate("/runs")}>{activeRun?.objective ? activeRun.objective.slice(0, 36) : "NO ACTIVE RUN"}</button></span><span>EXTERNAL SERVICE <strong>{externalHealth?.state === "ready" ? "CONNECTED" : externalHealth?.state === "degraded" ? "LIMITED" : "CHECKING"}</strong></span><span>QUIET MODE <strong>{preferences.quietMode ? "ON" : "OFF"}</strong></span>{preferences.demoMode && <span>MODE <strong>DEMONSTRATION</strong></span>}</footer>
    </main>
  </div>;
}
