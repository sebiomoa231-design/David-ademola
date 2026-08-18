"use client";

import {
  Activity,
  ArrowUpRight,
  AudioLines,
  AudioWaveform,
  Bot,
  BrainCircuit,
  Check,
  ChevronRight,
  CircleHelp,
  Clock3,
  Command,
  Copy,
  Database,
  FileText,
  Film,
  FolderKanban,
  Gauge,
  Globe2,
  Github,
  Headphones,
  Image as ImageIcon,
  LayoutDashboard,
  PenLine,
  Library,
  LifeBuoy,
  Link2,
  LockKeyhole,
  Menu,
  MessageSquare,
  Mic,
  MoreHorizontal,
  Palette,
  Pause,
  Play,
  Plus,
  Rocket,
  Search,
  Send,
  Sun,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Target,
  TimerReset,
  Upload,
  UserRound,
  Users,
  Video,
  Wand2,
  WandSparkles,
  X,
  Zap,
  RefreshCw,
  Trash2,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "@/lib/api";
import { useVoiceOS } from "@/hooks/useVoiceOS";
import { defaultDavidSettings, davidStateCopy, readDavidSettings, writeDavidSettings, type DavidPreferenceKey, type DavidSettings } from "@/lib/david-os-config";
import {
  baseExecutionSteps,
  phaseFromRunStatus,
  stepsForPhase,
  type ExecutionPhase,
  type ExecutionSnapshot,
} from "@/lib/execution-state";

type RouteKey =
  | "operating-system"
  | "freehand"
  | "lighting"
  | "dashboard"
  | "chat"
  | "projects"
  | "tasks"
  | "agents"
  | "memory"
  | "creative"
  | "website-builder"
  | "video-studio"
  | "voice-studio"
  | "image-studio"
  | "music-studio"
  | "enhance-studio"
  | "edit-studio"
  | "reshoot-studio"
  | "files"
  | "providers"
  | "activity"
  | "devices"
  | "settings"
  | "owner";

type Message = { id: string; role: "user" | "assistant"; text: string; time: string; status?: string };
type Toast = { kind: "success" | "info" | "error"; text: string } | null;

const navGroups: { label: string; items: { route: RouteKey; label: string; icon: LucideIcon; badge?: string }[] }[] = [
  {
    label: "Command center",
    items: [
      { route: "operating-system", label: "David OS", icon: Command, badge: "LIVE" },
      { route: "freehand", label: "Freehand", icon: PenLine },
      { route: "lighting", label: "Lighting", icon: Sun },
      { route: "dashboard", label: "Overview", icon: LayoutDashboard },
      { route: "chat", label: "Conversation", icon: MessageSquare, badge: "AI" },
      { route: "agents", label: "Agents", icon: Bot },
    ],
  },
  {
    label: "Work systems",
    items: [
      { route: "projects", label: "Projects", icon: FolderKanban },
      { route: "tasks", label: "Tasks", icon: Target, badge: "4" },
      { route: "memory", label: "Memory", icon: BrainCircuit },
      { route: "files", label: "Files & knowledge", icon: Library },
    ],
  },
  {
    label: "Creative studio",
    items: [
      { route: "creative", label: "Creative suite", icon: Palette },
      { route: "website-builder", label: "Website builder", icon: Globe2 },
      { route: "video-studio", label: "Video studio", icon: Video },
      { route: "voice-studio", label: "Voice studio", icon: Headphones },
      { route: "image-studio", label: "Image lab", icon: ImageIcon },
      { route: "music-studio", label: "Music studio", icon: AudioWaveform },
      { route: "enhance-studio", label: "Enhance media", icon: Wand2 },
      { route: "edit-studio", label: "Edit studio", icon: SlidersHorizontal },
      { route: "reshoot-studio", label: "Reshoot studio", icon: RefreshCw },
    ],
  },
  {
    label: "System",
    items: [
      { route: "providers", label: "Providers", icon: Zap },
      { route: "activity", label: "Activity log", icon: Activity },
      { route: "devices", label: "Devices", icon: SlidersHorizontal },
      { route: "settings", label: "Settings", icon: Settings },
    ],
  },
];

const routeMeta: Record<RouteKey, { eyebrow: string; title: string; description: string }> = {
  "operating-system": { eyebrow: "David AI / Operating system", title: "David is listening.", description: "A voice-first command environment for conversation, delegation, execution, and verified results." },
  freehand: { eyebrow: "David AI / Freehand canvas", title: "Sketch the system.", description: "A local drawing surface for visual thinking. Nothing is uploaded until you explicitly export or attach it." },
  lighting: { eyebrow: "David AI / Lighting control", title: "Tune the atmosphere.", description: "Adjust the local interface illumination and core response without pretending to control physical devices." },
  dashboard: { eyebrow: "David AI / Command center", title: "Good morning, David is ready.", description: "Turn one clear objective into a coordinated plan, finished work, and a decision-ready summary." },
  chat: { eyebrow: "David AI / Conversation", title: "What should we move forward today?", description: "Ask a question, delegate a goal, or start a creative production workflow." },
  projects: { eyebrow: "David AI / Work systems", title: "Projects with momentum.", description: "Keep goals, tasks, files, and agent runs connected in one operating view." },
  tasks: { eyebrow: "David AI / Work systems", title: "Your execution queue.", description: "See what is running, what needs approval, and what David can take off your plate next." },
  agents: { eyebrow: "David AI / Command center", title: "A coordinated team of specialists.", description: "Delegate research, strategy, creative, engineering, and quality-control work to focused agents." },
  memory: { eyebrow: "David AI / Work systems", title: "A business brain that compounds.", description: "Your preferences, decisions, documents, and brand context stay available when you need them." },
  creative: { eyebrow: "David AI / Creative studio", title: "From brief to finished media.", description: "Create connected websites, videos, voices, images, documents, and campaign assets." },
  "website-builder": { eyebrow: "David AI / Creative studio", title: "Describe the site. David builds the system.", description: "Generate an on-brand landing page, internal tool, or customer portal from one brief." },
  "video-studio": { eyebrow: "David AI / Creative studio", title: "A production room for every idea.", description: "Build scripts, scenes, voiceovers, captions, and social cuts from a single concept." },
  "voice-studio": { eyebrow: "David AI / Creative studio", title: "Give every idea a voice.", description: "Shape narration, dialogue, and spoken interaction with a clear review boundary before playback." },
  "image-studio": { eyebrow: "David AI / Creative studio", title: "Build the visual language.", description: "Create campaign visuals, thumbnails, diagrams, and variants from a brand-aware brief." },
  "music-studio": { eyebrow: "David AI / Creative studio", title: "Score the next moment.", description: "Plan a soundtrack or sonic identity with duration, mood, and delivery requirements in view." },
  "enhance-studio": { eyebrow: "David AI / Creative studio", title: "Make the source stronger.", description: "Prepare an enhancement pass for image, video, or audio while preserving provenance and approval." },
  "edit-studio": { eyebrow: "David AI / Creative studio", title: "Edit with intent.", description: "Describe the cut, cleanup, translation, or transformation you want before David prepares the edit plan." },
  "reshoot-studio": { eyebrow: "David AI / Creative studio", title: "Reimagine the shot.", description: "Direct a reshoot or scene variation with continuity notes, reference assets, and a reviewable brief." },
  files: { eyebrow: "David AI / Work systems", title: "Your knowledge, organized.", description: "Upload source material once and let David retrieve, summarize, and connect it across projects." },
  providers: { eyebrow: "David AI / System", title: "Capability health at a glance.", description: "See which models and services are configured, healthy, or waiting for a connection." },
  activity: { eyebrow: "David AI / System", title: "Everything David does, visible.", description: "Review decisions, approvals, generated artifacts, and system events with confidence." },
  devices: { eyebrow: "David AI / System", title: "David across your workspace.", description: "Manage trusted devices, voice access, and the surfaces where your agent can act." },
  settings: { eyebrow: "David AI / System", title: "Make the system yours.", description: "Control memory, approvals, brand behavior, notifications, and integrations." },
  owner: { eyebrow: "David AI / Owner console", title: "The control plane.", description: "Monitor the platform, review governance, and shape the next capability layer." },
};

const starterPrompts = [
  "Plan a launch campaign for my next product",
  "Turn this idea into a landing page",
  "Review my active projects and pick the next action",
  "Create a weekly business performance workflow",
];

const activityItems = [
  { icon: Check, title: "Launch brief approved", detail: "Marketing workflow / 12 minutes ago", color: "signal" },
  { icon: Video, title: "Product teaser assembled", detail: "Creative studio / 38 minutes ago", color: "crimson" },
  { icon: Database, title: "Knowledge source indexed", detail: "Brand handbook.pdf / 1 hour ago", color: "blue" },
  { icon: ShieldCheck, title: "Approval gate completed", detail: "Website deployment / 2 hours ago", color: "amber" },
];

const formatTime = () => new Intl.DateTimeFormat("en", { hour: "2-digit", minute: "2-digit" }).format(new Date());

const initialExecution: ExecutionSnapshot = {
  phase: "idle",
  objective: "",
  message: "Ready for a governed objective.",
  steps: baseExecutionSteps,
};

function executionMessage(phase: ExecutionPhase): string {
  if (phase === "planning") return "David is translating the objective into a structured plan.";
  if (phase === "awaiting_approval") return "The plan is ready. Sensitive actions are paused until you approve them.";
  if (phase === "executing") return "Approved work is running through the selected capability path.";
  if (phase === "verifying") return "David is checking the result and recording execution evidence.";
  if (phase === "completed") return "The run completed and its result is ready for review.";
  if (phase === "degraded") return "The backend could not complete this run. Nothing was falsely marked as finished.";
  if (phase === "cancelled") return "The run was cancelled and no further external action will be taken.";
  return "Ready for a governed objective.";
}

function routeFromPath(pathname: string): RouteKey {
  const clean = pathname.replace(/^\//, "").split("/")[0] as RouteKey;
  return clean && clean in routeMeta ? clean : "dashboard";
}

function cx(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export default function DavidCommandCenter({ initialRoute = "dashboard" }: { initialRoute?: string }) {
  const pathname = usePathname() || `/${initialRoute}`;
  const router = useRouter();
  const activeRoute = pathname === "/" ? (initialRoute as RouteKey) : routeFromPath(pathname);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [toast, setToast] = useState<Toast>(null);
  const [connected, setConnected] = useState(true);
  const [draft, setDraft] = useState("");
  const [working, setWorking] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { id: "welcome", role: "assistant", text: "I’m David. Give me an objective, a question, or a creative direction. I’ll plan the work, show you what will happen, and ask before sensitive actions.", time: "09:41" },
  ]);
  const [execution, setExecution] = useState<ExecutionSnapshot>(initialExecution);
  const [preferences, setPreferences] = useState<DavidSettings>(defaultDavidSettings);
  useEffect(() => setPreferences(readDavidSettings()), []);
  useEffect(() => writeDavidSettings(preferences), [preferences]);
  const setPreference = (key: DavidPreferenceKey, value: boolean) => setPreferences((current) => ({ ...current, [key]: value }));
  const voice = useVoiceOS({
    onResult: (result) => {
      setMessages((current) => [
        ...current,
        { id: crypto.randomUUID(), role: "user", text: result.transcript, time: formatTime(), status: "voice command" },
        { id: crypto.randomUUID(), role: "assistant", text: result.response, time: formatTime(), status: result.agentsUsed.length ? `delegated · ${result.agentsUsed.join(", ")}` : "voice response" },
      ]);
      setToast({ kind: "success", text: result.agentsUsed.length ? `David delegated to ${result.agentsUsed.length} sub-agent${result.agentsUsed.length === 1 ? "" : "s"}.` : "David completed the voice response." });
    },
    onError: (message) => setToast({ kind: "error", text: message }),
  });

  useEffect(() => {
    let mounted = true;
    api.health().then(() => mounted && setConnected(true)).catch(() => mounted && setConnected(false));
    return () => { mounted = false; };
  }, []);

  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(null), 3600);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const navigate = (route: RouteKey) => {
    router.push(route === "dashboard" ? "/" : `/${route}`);
    setMobileOpen(false);
  };

  const submitMessage = async (value = draft) => {
    const text = value.trim();
    if (!text || working) return;
    const userMessage: Message = { id: crypto.randomUUID(), role: "user", text, time: formatTime() };
    setMessages((current) => [...current, userMessage]);
    setDraft("");
    setWorking(true);
    try {
      const response = await api.orchestrator.process(text, { source: "text_command_center" });
      const reply = response.text || "David has prepared the next step.";
      const delegated = response.agents_used?.length ? `delegated · ${response.agents_used.join(", ")}` : "live response";
      setMessages((current) => [...current, { id: crypto.randomUUID(), role: "assistant", text: reply, time: formatTime(), status: delegated }]);
    } catch {
      setMessages((current) => [...current, { id: crypto.randomUUID(), role: "assistant", text: "I’m in interface mode because the backend is not reachable right now. Your workspace is ready; reconnect the API to execute this request live.", time: formatTime(), status: "offline-ready" }]);
      setToast({ kind: "info", text: "David saved the conversation locally. Connect the API to execute live actions." });
    } finally {
      setWorking(false);
    }
  };

  const runObjective = async (objective: string) => {
    const text = objective.trim();
    if (!text || execution.phase === "planning" || execution.phase === "executing" || execution.phase === "verifying") return;

    setExecution({ phase: "planning", objective: text, message: executionMessage("planning"), steps: stepsForPhase("planning") });
    setToast({ kind: "info", text: "David is building a governed execution plan." });

    try {
      const goal = await api.intelligence.createGoal(text);
      setExecution((current) => ({ ...current, goalId: goal.id, message: "Goal captured. David is sequencing the required capabilities.", steps: stepsForPhase("planning") }));

      const plan = await api.intelligence.planGoal(goal.id);
      const firstCapability = plan.steps?.[0]?.capability || plan.steps?.[0]?.skill || plan.steps?.[0]?.tool;
      let selectedCapability = firstCapability ? String(firstCapability) : undefined;
      try {
        const route = await api.intelligence.route(text, selectedCapability);
        selectedCapability = String(route.selected?.capability_id || route.selected?.id || selectedCapability || "") || undefined;
      } catch {
        // Routing is advisory; the governed run endpoint remains the execution authority.
      }

      setExecution((current) => ({
        ...current,
        phase: "planning",
        selectedCapability,
        message: "Plan assembled. David is checking execution permissions and provider readiness.",
        steps: stepsForPhase("planning", plan),
      }));

      const run = await api.intelligence.createRun(goal.id, text, selectedCapability);
      const details = await api.intelligence.runDetails(run.id).catch(() => undefined);
      const phase = phaseFromRunStatus(details?.run?.status || run.status, details?.run?.approved ?? run.approved);
      setExecution({
        phase,
        objective: text,
        goalId: goal.id,
        runId: run.id,
        selectedCapability,
        message: executionMessage(phase),
        steps: stepsForPhase(phase, plan, details),
        events: details?.events?.slice(-4).map((event) => ({ label: String(event.type || event.event_type || "Execution event"), detail: event.message ? String(event.message) : undefined, state: "complete" as const })),
      });
      setToast({ kind: phase === "completed" ? "success" : phase === "degraded" ? "error" : "info", text: phase === "awaiting_approval" ? "Approval is required before David can continue." : executionMessage(phase) });
    } catch {
      const phase: ExecutionPhase = "degraded";
      setExecution({ phase, objective: text, message: executionMessage(phase), steps: stepsForPhase(phase) });
      setToast({ kind: "error", text: "The execution service is unavailable. David kept the request in a truthful degraded state." });
    }
  };

  return (
    <div className={cx("david-shell", activeRoute === "operating-system" && "david-shell-os", preferences.reducedMotion && "david-pref-reduced-motion", preferences.highContrast && "david-pref-high-contrast", preferences.quietMode && "david-pref-quiet")}>
      <div className="shell-grid" />
      <div className="noise" />
      <Sidebar activeRoute={activeRoute} open={mobileOpen} onClose={() => setMobileOpen(false)} onNavigate={navigate} />
      <main className="david-main">
        <header className="topbar">
          <div className="topbar-left">
            <button className="icon-button mobile-menu" onClick={() => setMobileOpen(true)} aria-label="Open navigation"><Menu size={18} /></button>
            <div>
              <div className="micro-label">{routeMeta[activeRoute].eyebrow}</div>
              <div className="topbar-title">David operating normally</div>
            </div>
          </div>
            <div className="topbar-actions">
            <VoiceHUD voice={voice} />
            <div className={cx("connection-pill", connected ? "is-online" : "is-offline")}><span className="status-dot" />{connected ? "API connected" : "Interface mode"}</div>
            <button className="icon-button" onClick={() => setToast({ kind: "info", text: "Command search is ready for your next prompt." })} aria-label="Search"><Search size={17} /></button>
            <button className="profile-chip" onClick={() => navigate("settings")}><span className="avatar">D</span><span className="profile-name">David Ademola</span><ChevronRight size={15} /></button>
          </div>
        </header>

        <div className="page-frame">
          {activeRoute === "operating-system" && <OperatingSystemView voice={voice} connected={connected} preferences={preferences} onPreferenceChange={setPreference} onNavigate={navigate} />}
          {activeRoute === "freehand" && <FreehandView />}
          {activeRoute === "lighting" && <LightingView />}
          {activeRoute === "dashboard" && <Dashboard onNavigate={navigate} onRunObjective={(prompt) => void runObjective(prompt)} execution={execution} />}
          {activeRoute === "chat" && <ChatView messages={messages} draft={draft} setDraft={setDraft} working={working} onSubmit={() => void submitMessage()} onPrompt={(prompt) => void submitMessage(prompt)} onNavigate={navigate} />}
          {activeRoute === "projects" && <ProjectsView onNavigate={navigate} notify={setToast} />}
          {activeRoute === "tasks" && <TasksView notify={setToast} />}
          {activeRoute === "agents" && <AgentsView notify={setToast} />}
          {activeRoute === "memory" && <MemoryView notify={setToast} />}
          {activeRoute === "creative" && <CreativeView onNavigate={navigate} notify={setToast} />}
          {activeRoute === "website-builder" && <WebsiteBuilder notify={setToast} />}
          {activeRoute === "video-studio" && <VideoStudio notify={setToast} />}
          {activeRoute === "voice-studio" && <MultimodalStudio kind="voice" notify={setToast} />}
          {activeRoute === "image-studio" && <MultimodalStudio kind="image" notify={setToast} />}
          {activeRoute === "music-studio" && <MultimodalStudio kind="music" notify={setToast} />}
          {activeRoute === "enhance-studio" && <MultimodalStudio kind="enhance" notify={setToast} />}
          {activeRoute === "edit-studio" && <MultimodalStudio kind="edit" notify={setToast} />}
          {activeRoute === "reshoot-studio" && <MultimodalStudio kind="reshoot" notify={setToast} />}
          {activeRoute === "files" && <FilesView notify={setToast} />}
          {activeRoute === "providers" && <ProvidersView notify={setToast} />}
          {activeRoute === "activity" && <ActivityView />}
          {activeRoute === "devices" && <DevicesView notify={setToast} />}
          {activeRoute === "settings" && <SettingsView notify={setToast} preferences={preferences} onPreferenceChange={setPreference} />}
          {activeRoute === "owner" && <OwnerView notify={setToast} />}
        </div>
      </main>
      {toast && <div className={cx("toast", `toast-${toast.kind}`)}><span className="toast-mark">{toast.kind === "success" ? <Check size={15} /> : toast.kind === "error" ? <X size={15} /> : <CircleHelp size={15} />}</span><span>{toast.text}</span></div>}
    </div>
  );
}

function VoiceHUD({ voice }: { voice: ReturnType<typeof useVoiceOS> }) {
  const active = voice.state !== "idle";
  const label = voice.state === "listening" ? "LISTENING" : voice.state === "thinking" ? "PROCESSING" : voice.state === "speaking" ? "SPEAKING" : voice.state === "error" ? "VOICE ERROR" : "STANDBY";
  return (
    <div className={cx("voice-os-hud", `voice-state-${voice.state}`)} data-state={voice.state}>
      <div className="voice-core-mini" style={{ transform: `scale(${1 + voice.volume * 0.22})` }} aria-hidden="true">
        <span className="voice-core-ring voice-core-ring-one" />
        <span className="voice-core-ring voice-core-ring-two" />
        <span className="voice-core-sphere" />
      </div>
      <div className="voice-os-copy">
        <span className="voice-os-label">DAVID / {label}</span>
        <strong>{voice.activeAction || "Ready for your voice"}</strong>
        {(voice.interimTranscript || voice.transcript) && <small>{voice.interimTranscript || voice.transcript}</small>}
      </div>
      <button className="voice-os-button" onClick={voice.state === "speaking" ? voice.cancel : voice.toggle} disabled={voice.state === "thinking"} aria-label={voice.state === "speaking" ? "Stop David speaking" : "Talk to David"}>
        {voice.state === "listening" ? <Mic size={15} /> : voice.state === "speaking" ? <AudioLines size={15} /> : <Mic size={15} />}
      </button>
      {active && <button className="voice-os-stop" onClick={voice.cancel} aria-label="Stop voice operation"><X size={13} /></button>}
    </div>
  );
}

function Sidebar({ activeRoute, open, onClose, onNavigate }: { activeRoute: RouteKey; open: boolean; onClose: () => void; onNavigate: (route: RouteKey) => void }) {
  return <>
    {open && <button className="mobile-scrim" onClick={onClose} aria-label="Close navigation" />}
    <aside className={cx("sidebar", open && "sidebar-open")}>
      <div className="brand-row"><div className="brand-mark"><Sparkles size={17} /></div><div><div className="brand-name">DAVID<span>AI</span></div><div className="brand-subtitle">Personal operating system</div></div><button className="icon-button mobile-close" onClick={onClose} aria-label="Close navigation"><X size={18} /></button></div>
      <div className="workspace-selector"><div className="workspace-orb"><BrainCircuit size={16} /></div><div className="workspace-copy"><span className="workspace-label">Active workspace</span><strong>David Ademola</strong></div><MoreHorizontal size={17} className="muted-icon" /></div>
      <nav className="side-nav">{navGroups.map((group) => <div className="nav-group" key={group.label}><div className="nav-group-label">{group.label}</div>{group.items.map(({ route, label, icon: Icon, badge }) => <button key={route} onClick={() => onNavigate(route)} className={cx("nav-item", activeRoute === route && "nav-item-active")}><Icon size={17} strokeWidth={activeRoute === route ? 2.2 : 1.8} /><span>{label}</span>{badge && <span className={cx("nav-badge", badge === "AI" && "nav-badge-red")}>{badge}</span>}</button>)}</div>)}</nav>
      <div className="sidebar-bottom"><button className="upgrade-card" onClick={() => onNavigate("owner")}><div className="upgrade-icon"><Rocket size={16} /></div><div><strong>Unlock David Pro</strong><span>More runs, memory, and automation</span></div><ArrowUpRight size={15} /></button><div className="sidebar-foot"><div className="status-dot" /> <span>All systems nominal</span><button onClick={() => onNavigate("settings")} aria-label="Open settings"><Settings size={14} /></button></div></div>
    </aside>
  </>;
}

function PageHeader({ route, action }: { route: RouteKey; action?: React.ReactNode }) {
  const meta = routeMeta[route];
  return <div className="page-header"><div><div className="micro-label">{meta.eyebrow}</div><h1>{meta.title}</h1><p>{meta.description}</p></div>{action}</div>;
}

function OperatingSystemView({ voice, connected, preferences, onPreferenceChange, onNavigate }: { voice: ReturnType<typeof useVoiceOS>; connected: boolean; preferences: DavidSettings; onPreferenceChange: (key: DavidPreferenceKey, value: boolean) => void; onNavigate: (route: RouteKey) => void }) {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(timer);
  }, []);
  const isExecuting = voice.state === "thinking" && /DELEGATING|ASSIGNED|EXECUTING/i.test(voice.activeAction);
  const baseStateConfig = davidStateCopy[voice.state];
  const stateConfig = voice.state === "idle" && voice.response
    ? { ...baseStateConfig, label: "RESPONSE READY", detail: "Answer or result is ready.", action: "RESPONSE READY" }
    : voice.state === "thinking" && isExecuting
      ? { ...baseStateConfig, label: "EXECUTING ACTION", detail: "Performing the requested action.", action: "DELEGATED WORK IN PROGRESS" }
      : baseStateConfig;
  const clock = new Intl.DateTimeFormat("en", { hour: "2-digit", minute: "2-digit", second: "2-digit" }).format(now);
  const micStatus = voice.state === "listening" ? "ON" : "OFF";
  const networkStatus = connected ? "ONLINE" : "OFFLINE";
  const waveform = [0.2, 0.42, 0.7, 0.34, 0.9, 0.5, 0.25, 0.62, 0.34, 0.78, 0.4, 0.25, 0.58, 0.86, 0.36, 0.64, 0.24, 0.5, 0.32, 0.72];
  return <div className={cx("os-view", `os-state-${voice.state}`, isExecuting && "os-executing", voice.response && "os-has-response")}>

    <div className="os-view-header"><div><span className="micro-label">DAVID AI / VOICE-FIRST OPERATING SYSTEM</span><h1>Command the system naturally.</h1><p>Speak a goal. David interprets it, assigns governed sub-agents, and returns an audible, reviewable result.</p></div><div className="os-header-status"><span className="status-dot" />{connected ? "NETWORK CONNECTED" : "CONNECTION UNAVAILABLE"}</div></div>
    <div className="os-stage os-reference-stage" aria-live="polite">
      <div className="os-reference-title"><span>ORBITAL</span><strong>CORE</strong></div>
      <div className="os-reference-lines" />
      <aside className="os-hud-panel os-hud-left"><section><span className="os-hud-label">SYSTEM</span><p>Dashboard</p><p>Files</p><p>Devices</p><p>Network</p></section><section><span className="os-hud-label">APPLICATIONS</span><p>Browser</p><p>Terminal</p><p>Code Editor</p><p>Media Player</p></section><section><span className="os-hud-label">QUICK ACCESS</span><p>Notes</p><p>Calendar</p><p>Tasks</p></section></aside>
      <aside className="os-hud-panel os-hud-right"><section><span className="os-hud-label">NOTIFICATIONS</span><p>{voice.response ? "1 active response" : "No new notifications"}</p></section><section><span className="os-hud-label">SYSTEM HEALTH</span><p>MIC <b>{micStatus}</b></p><p>NET <b>{networkStatus}</b></p><p>MODE <b>GOVERNED</b></p></section></aside>
      <div className="os-reference-axis" />
      <div className="os-reference-core" style={{ transform: `translate(-50%, -50%) scale(${1 + voice.volume * 0.18})` }}><span className="os-reference-ticks">{Array.from({ length: 12 }, (_, index) => <i key={index} style={{ transform: `rotate(${index * 30}deg)` }} />)}</span><span className="os-core-orbit os-orbit-a" /><span className="os-core-orbit os-orbit-b" /><span className="os-core-orbit os-orbit-c" /><span className="os-reference-ring ring-one" /><span className="os-reference-ring ring-two" /><span className="os-reference-ring ring-three" /><span className="os-reference-sphere" /><span className="os-core-nucleus" /></div>
      <div className="os-reference-readout"><span>DAVID AI</span><strong>{stateConfig.label}</strong><small>{stateConfig.detail}{preferences.quietMode ? " · QUIET MODE" : ""}</small><em>{voice.activeAction || stateConfig.action}</em></div>
      {(voice.state === "listening" || voice.state === "speaking") && <div className="os-reference-waveform" aria-label="Voice activity waveform">{waveform.map((height, index) => <i key={index} style={{ height: `${Math.max(4, height * (voice.state === "listening" ? 34 + voice.volume * 42 : 24))}px` }} />)}</div>}
      {voice.state === "listening" && <div className="os-video-state-card os-listening-card"><span>MICROPHONE ACTIVE</span><p>{voice.interimTranscript || voice.transcript || "Listening for your command..."}</p></div>}
      {isExecuting && <div className="os-video-state-card os-executing-card"><span>OPENING DAVID WORKSPACE</span><strong>ACTION IN PROGRESS</strong><div><i /></div></div>}
      {voice.response && <div className="os-video-state-card os-response-card"><p>{voice.response}</p><button className="os-card-clear" onClick={voice.clearTranscript}><Trash2 size={13} /> Clear transcript</button></div>}
      {(voice.transcript || voice.interimTranscript) && voice.state !== "listening" && <div className="os-transcript-panel"><span className="micro-label">LIVE TRANSCRIPT</span>{voice.transcript && <p><em>YOU</em> {voice.transcript}</p>}{voice.interimTranscript && !voice.transcript && <p><em>LISTENING</em> {voice.interimTranscript}</p>}<button className="text-button" onClick={voice.clearTranscript}><Trash2 size={13} /> Delete transcript</button></div>}
      <div className="os-reference-bottom"><span>{clock}</span><span>ACTIVE TASK: {voice.activeAction || "NONE"}</span><span>MIC: {micStatus}</span><span>NETWORK: {networkStatus}</span><span>SYSTEM: OPTIMAL</span></div>
    </div>
    <div className="os-controls"><button className="button button-primary" onClick={voice.state === "speaking" ? voice.cancel : voice.toggle} disabled={voice.state === "thinking"}><Mic size={16} />{voice.state === "listening" ? "Stop & process" : voice.state === "speaking" ? "Stop speaking" : "Talk to David"}</button><button className="button button-secondary" onClick={voice.isPaused ? voice.resume : voice.pause} disabled={!voice.isSpeaking}><Pause size={16} />{voice.isPaused ? "Resume" : "Pause"}</button><button className="button button-secondary" onClick={() => void voice.replay()} disabled={!voice.response}><Play size={16} />Replay</button><button className="button button-secondary" onClick={voice.cancel} disabled={voice.state === "idle"}><X size={16} />Cancel</button><button className="button button-secondary" onClick={() => onNavigate("agents")}><Bot size={16} />Open sub-agents</button><button className="button button-secondary" onClick={() => onNavigate("chat")}><MessageSquare size={16} />Text fallback</button></div>
    {voice.error && <div className="os-warning"><span className="status-tag tag-amber">VOICE WARNING</span><span>{voice.error}</span></div>}
    {voice.response && <div className="os-response panel-card"><div><span className="micro-label">RESPONSE READY</span><h2>David has returned a result.</h2><p>{voice.response}</p></div><span className="os-response-mark"><AudioLines size={18} /></span></div>}
  </div>;
}

function Dashboard({ onNavigate, onRunObjective, execution }: { onNavigate: (route: RouteKey) => void; onRunObjective: (prompt: string) => void; execution: ExecutionSnapshot }) {
  return <div className="dashboard-page">
    <div className="hero-panel"><div className="hero-copy"><div className="eyebrow-pill"><span className="status-dot" /> COMMAND CENTER / LIVE</div><h1>Good morning, <span>David</span> is ready.</h1><p>One objective in. A coordinated plan, finished work, and a clear next decision out.</p><div className="hero-actions"><button className="button button-primary" onClick={() => onNavigate("chat")}><Command size={16} /> Start a command</button><button className="button button-secondary" onClick={() => onNavigate("creative")}><WandSparkles size={16} /> Open creative studio</button></div><div className="hero-trust"><ShieldCheck size={14} /> Approval gates protect sensitive actions <span>·</span> <Database size={14} /> 128 memories indexed</div></div><div className="hero-core-wrap"><div className="core-orbit core-orbit-one" /><div className="core-orbit core-orbit-two" /><div className="ai-core-large"><div className="core-glint" /><div className="core-center"><Sparkles size={25} /></div></div><div className="core-caption"><span>DAVID CORE</span><strong>Ready to orchestrate</strong></div></div></div>
    <div className="stat-grid"><StatCard label="Active projects" value="06" trend="+2 this week" icon={FolderKanban} tone="red" /><StatCard label="Tasks in motion" value="14" trend="4 need approval" icon={Target} tone="amber" /><StatCard label="Knowledge indexed" value="128" trend="+12 this month" icon={BrainCircuit} tone="blue" /><StatCard label="System readiness" value="98.4%" trend="All core services nominal" icon={Gauge} tone="green" /></div>
    <div className="dashboard-grid"><section className="panel-card command-panel"><SectionHeader eyebrow="EXECUTION LAYER" title="Give David an objective" detail="David will route the work, build a plan, and show you the approval points." icon={Target} /><PromptBox onPrompt={onRunObjective} /></section><section className="panel-card radar-panel"><SectionHeader eyebrow="TODAY'S RADAR" title="What needs your attention" icon={Activity} action={<button className="text-button" onClick={() => onNavigate("activity")}>View log <ArrowUpRight size={14} /></button>} /><div className="radar-list"><RadarItem icon={ShieldCheck} title="Approve website deployment" detail="Project: Atlas launch" tag="Approval" tone="amber" onClick={() => onNavigate("projects")} /><RadarItem icon={Video} title="Product teaser is ready" detail="3 cuts generated from your brief" tag="Ready" tone="green" onClick={() => onNavigate("video-studio")} /><RadarItem icon={BrainCircuit} title="New knowledge connected" detail="Brand handbook / 14 pages" tag="Indexed" tone="blue" onClick={() => onNavigate("memory")} /></div></section></div>
    <ExecutionTimeline execution={execution} />
    <section className="section-block"><SectionHeader eyebrow="CAPABILITY MAP" title="One agent, many coordinated systems" detail="Start with a surface or let David choose the right workflow for your goal." icon={Sparkles} action={<button className="text-button" onClick={() => onNavigate("creative")}>Explore all capabilities <ArrowUpRight size={14} /></button>} /><div className="capability-grid"><CapabilityCard icon={Bot} title="Delegate work" detail="Route research, strategy, operations, and quality control to focused agents." color="red" onClick={() => onNavigate("agents")} /><CapabilityCard icon={Palette} title="Create anything" detail="Produce connected websites, videos, images, voice, and documents." color="purple" onClick={() => onNavigate("creative")} /><CapabilityCard icon={Database} title="Build context" detail="Connect files and business knowledge so every answer gets smarter." color="blue" onClick={() => onNavigate("memory")} /><CapabilityCard icon={Zap} title="Automate repeat work" detail="Schedule recurring workflows and keep your business moving in the background." color="amber" onClick={() => onNavigate("tasks")} /></div></section>
    <section className="section-block"><SectionHeader eyebrow="RECENT SIGNAL" title="Your latest work" icon={Activity} action={<button className="text-button" onClick={() => onNavigate("activity")}>Open activity <ArrowUpRight size={14} /></button>} /><div className="activity-grid">{activityItems.slice(0, 3).map((item) => <ActivityRow key={item.title} {...item} />)}</div></section>
  </div>;
}

function ExecutionTimeline({ execution }: { execution: ExecutionSnapshot }) {
  const phaseTone = execution.phase === "completed" ? "green" : execution.phase === "degraded" || execution.phase === "cancelled" ? "red" : execution.phase === "awaiting_approval" ? "amber" : "blue";
  const phaseLabel = execution.phase === "idle" ? "READY" : execution.phase.replace(/_/g, " ").toUpperCase();
  return <section className={cx("execution-timeline panel-card", `execution-${execution.phase}`)}><div className="execution-heading"><div><div className="micro-label">STATE-DRIVEN EXECUTION</div><h2>David shows the work, not just the answer.</h2><p>{execution.objective || "Every objective moves through intent, plan, policy, execution, verification, and traceable result."}</p></div><span className={cx("status-tag", `tag-${phaseTone}`)}><span className="status-dot" /> {phaseLabel}</span></div><div className="execution-status"><span className={cx("execution-core", `tone-${phaseTone}`)}><Sparkles size={18} /></span><div><strong>{execution.message}</strong><small>{execution.runId ? `Run ${execution.runId.slice(0, 10)} · ` : "No run created yet · "}{execution.selectedCapability ? `Capability: ${execution.selectedCapability}` : "Governed by workspace policy"}</small></div>{execution.phase === "awaiting_approval" && <span className="approval-chip"><ShieldCheck size={14} /> Approval gate</span>}</div><div className="execution-steps">{execution.steps.map((step, index) => <div className={cx("execution-step", `step-${step.state}`)} key={step.id}><span className="execution-step-marker">{step.state === "complete" ? <Check size={13} /> : step.state === "active" ? <Play size={12} /> : step.state === "blocked" ? <ShieldCheck size={13} /> : step.state === "failed" ? <X size={13} /> : <span>{index + 1}</span>}</span><span className="execution-step-copy"><strong>{step.title}</strong><small>{step.detail}</small></span>{step.state === "active" && <span className="execution-live">Live</span>}</div>)}</div></section>;
}

function ChatView({ messages, draft, setDraft, working, onSubmit, onPrompt, onNavigate }: { messages: Message[]; draft: string; setDraft: (value: string) => void; working: boolean; onSubmit: () => void; onPrompt: (prompt: string) => void; onNavigate: (route: RouteKey) => void }) {
  return <div className="chat-page"><PageHeader route="chat" action={<div className="header-actions"><button className="button button-secondary" onClick={() => onNavigate("agents")}><Bot size={16} /> Delegate</button><button className="button button-primary" onClick={() => onNavigate("creative")}><Plus size={16} /> New workspace</button></div>} /><div className="chat-layout"><section className="panel-card chat-card"><div className="chat-card-top"><div className="assistant-identity"><div className="mini-core"><Sparkles size={15} /></div><div><strong>David / General intelligence</strong><span>Planning, creating, and executing with approval</span></div></div><div className="live-label"><span className="status-dot" /> Live</div></div><div className="messages">{messages.map((message) => <div className={cx("message-row", message.role === "user" && "message-row-user")} key={message.id}><div className={cx("message-avatar", message.role === "user" ? "user-avatar" : "assistant-avatar")}>{message.role === "user" ? <UserRound size={15} /> : <Sparkles size={15} />}</div><div className={cx("message-bubble", message.role === "user" && "message-bubble-user")}><div className="message-meta"><span>{message.role === "user" ? "You" : "David"}</span><time>{message.time}</time>{message.status && <em>{message.status}</em>}</div><p>{message.text}</p>{message.role === "assistant" && <div className="message-tools"><button onClick={() => void navigator.clipboard?.writeText(message.text)}><Copy size={13} /> Copy</button><button onClick={() => onPrompt(`Continue from this response: ${message.text}`)}><ArrowUpRight size={13} /> Continue</button></div>}</div></div>)}{working && <div className="message-row"><div className="message-avatar assistant-avatar"><Sparkles size={15} /></div><div className="message-bubble thinking-bubble"><div className="thinking-dots"><span /><span /><span /></div><span>David is routing your request</span></div></div>}</div><div className="chat-composer"><div className="composer-tools"><button title="Attach files"><Upload size={17} /></button><button title="Voice input"><Mic size={17} /></button><span>Use @ to reference a project or file</span></div><div className="composer-input"><textarea value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); onSubmit(); } }} placeholder="Ask David to plan, create, analyze, or execute..." rows={2} /><button className="send-button" onClick={onSubmit} disabled={working || !draft.trim()} aria-label="Send message">{working ? <TimerReset size={17} className="spin" /> : <Send size={17} />}</button></div><div className="composer-hint"><span>David checks sensitive actions before execution.</span><kbd>Enter</kbd><span>to send</span></div></div></section><aside className="chat-side"><div className="panel-card side-card"><SectionHeader eyebrow="CONTEXT" title="Active context" icon={BrainCircuit} /><ContextRow label="Workspace" value="David Ademola" /><ContextRow label="Memory" value="128 items" /><ContextRow label="Brand voice" value="Confident / direct" /><ContextRow label="Approval policy" value="Protected" /><button className="full-width-button" onClick={() => onNavigate("memory")}>Manage context <ArrowUpRight size={14} /></button></div><div className="panel-card side-card"><SectionHeader eyebrow="STARTER COMMANDS" title="Jumpstart a workflow" icon={Zap} />{starterPrompts.slice(0, 3).map((prompt) => <button className="starter-command" key={prompt} onClick={() => onPrompt(prompt)}><span>{prompt}</span><ChevronRight size={15} /></button>)}</div></aside></div></div>;
}

function ProjectsView({ onNavigate, notify }: { onNavigate: (route: RouteKey) => void; notify: (toast: Toast) => void }) {
  const projects = [{ name: "Atlas product launch", type: "Campaign system", progress: 78, status: "Needs approval", color: "red", meta: "12 tasks · 8 assets" }, { name: "Founder operating system", type: "Internal workspace", progress: 46, status: "In motion", color: "blue", meta: "7 tasks · 3 agents" }, { name: "Creator content engine", type: "Content pipeline", progress: 24, status: "Planning", color: "purple", meta: "18 tasks · 0 approvals" }];
  return <div><PageHeader route="projects" action={<button className="button button-primary" onClick={() => notify({ kind: "success", text: "New project workspace created." })}><Plus size={16} /> New project</button>} /><div className="filter-row"><div className="filter-search"><Search size={16} /><input placeholder="Search projects" /></div><button className="filter-button"><SlidersHorizontal size={15} /> All projects <ChevronRight size={14} /></button></div><div className="project-grid">{projects.map((project) => <button className="project-card panel-card" key={project.name} onClick={() => notify({ kind: "info", text: `${project.name} opened in workspace view.` })}><div className={cx("project-cover", `cover-${project.color}`)}><div className="project-cover-grid" /><span>{project.type}</span><MoreHorizontal size={18} /></div><div className="project-card-body"><div className="project-card-title"><div><h3>{project.name}</h3><p>{project.meta}</p></div><span className={cx("status-tag", project.status === "Needs approval" ? "tag-amber" : project.status === "In motion" ? "tag-green" : "tag-blue")}>{project.status}</span></div><div className="progress-meta"><span>Project progress</span><strong>{project.progress}%</strong></div><div className="progress-track"><span style={{ width: `${project.progress}%` }} /></div><div className="project-footer"><span><Bot size={14} /> 3 agents available</span><ChevronRight size={16} /></div></div></button>)}</div><div className="split-grid section-block"><div className="panel-card padded-card"><SectionHeader eyebrow="WORKFLOW LIBRARY" title="Start from a proven system" icon={Library} /><div className="mini-list">{["Product launch system", "Weekly executive review", "Customer support brain"].map((item) => <button key={item} className="mini-list-row" onClick={() => notify({ kind: "info", text: `${item} template selected.` })}><span className="template-icon"><WandSparkles size={15} /></span><span><strong>{item}</strong><small>Reusable workflow template</small></span><Plus size={15} /></button>)}</div></div><div className="panel-card padded-card"><SectionHeader eyebrow="PROJECT SIGNAL" title="Next recommended action" icon={Sparkles} /><div className="recommendation"><div className="recommendation-icon"><ShieldCheck size={17} /></div><div><strong>Approve the Atlas deployment</strong><p>David has validated the website build and found no blocking issues.</p><button className="text-button" onClick={() => onNavigate("activity")}>Review evidence <ArrowUpRight size={14} /></button></div></div></div></div></div>;
}

function TasksView({ notify }: { notify: (toast: Toast) => void }) {
  const tasks = [{ title: "Approve Atlas landing page deployment", project: "Atlas product launch", state: "Requires approval", tone: "amber", icon: ShieldCheck }, { title: "Generate three short-form product cuts", project: "Atlas product launch", state: "Running", tone: "red", icon: Video }, { title: "Index customer interview transcripts", project: "Founder operating system", state: "Queued", tone: "blue", icon: Database }, { title: "Prepare weekly business performance brief", project: "Operations", state: "Scheduled for Friday", tone: "green", icon: FileText }];
  return <div><PageHeader route="tasks" action={<button className="button button-primary" onClick={() => notify({ kind: "success", text: "Task draft created. Add it to a project when ready." })}><Plus size={16} /> Add task</button>} /><div className="task-summary"><div><span className="micro-label">Today</span><strong>14 tasks in motion</strong><p>4 active · 2 waiting · 8 completed</p></div><div className="task-summary-progress"><span style={{ width: "72%" }} /><small>72% weekly completion</small></div></div><div className="task-board"><div className="board-column"><div className="column-heading"><span>Needs approval</span><b>1</b></div>{tasks.slice(0, 1).map((task) => <TaskCard key={task.title} task={task} notify={notify} />)}</div><div className="board-column"><div className="column-heading"><span>In motion</span><b>1</b></div>{tasks.slice(1, 2).map((task) => <TaskCard key={task.title} task={task} notify={notify} />)}</div><div className="board-column"><div className="column-heading"><span>Queued & scheduled</span><b>2</b></div>{tasks.slice(2).map((task) => <TaskCard key={task.title} task={task} notify={notify} />)}</div></div></div>;
}

function TaskCard({ task, notify }: { task: { title: string; project: string; state: string; tone: string; icon: LucideIcon }; notify: (toast: Toast) => void }) { const Icon = task.icon; return <button className="task-card" onClick={() => notify({ kind: task.tone === "amber" ? "info" : "success", text: task.tone === "amber" ? "Approval details opened." : `${task.title} marked for review.` })}><div className={cx("task-icon", `tone-${task.tone}`)}><Icon size={16} /></div><div className="task-card-content"><strong>{task.title}</strong><span>{task.project}</span><div className="task-card-meta"><em className={cx("status-tag", `tag-${task.tone}`)}>{task.state}</em><MoreHorizontal size={15} /></div></div></button>; }

function AgentsView({ notify }: { notify: (toast: Toast) => void }) {
  const [agents, setAgents] = useState<Array<Record<string, unknown>>>([]);
  const [objective, setObjective] = useState("Review the current David operating system and recommend the next safe improvement.");
  const [loading, setLoading] = useState(true);
  const [dispatching, setDispatching] = useState(false);

  useEffect(() => {
    let mounted = true;
    api.orchestrator.agents()
      .then((payload) => mounted && setAgents(payload.agents || []))
      .catch(() => mounted && notify({ kind: "error", text: "The live sub-agent registry is unavailable." }))
      .finally(() => mounted && setLoading(false));
    return () => { mounted = false; };
  }, [notify]);

  async function dispatchObjective() {
    const text = objective.trim();
    if (!text || dispatching) return;
    setDispatching(true);
    try {
      const result = await api.orchestrator.process(text, { source: "agent_registry", requested_by: "owner" });
      notify({ kind: "success", text: `David completed the orchestration with ${result.tasks_completed}/${result.total_tasks} sub-agent task${result.total_tasks === 1 ? "" : "s"}.` });
    } catch {
      notify({ kind: "error", text: "David could not dispatch this objective through the live orchestrator." });
    } finally {
      setDispatching(false);
    }
  }

  return <div>
    <PageHeader route="agents" action={<button className="button button-primary" onClick={dispatchObjective} disabled={dispatching}><Play size={16} /> {dispatching ? "Delegating..." : "Assign objective"}</button>} />
    <div className="agent-banner panel-card"><div className="agent-banner-icon"><Bot size={25} /></div><div><div className="eyebrow-pill">LIVE MULTI-AGENT ORCHESTRATION</div><h2>David assigns duties to governed specialists.</h2><p>Each sub-agent receives a bounded objective, operates inside David's policy, and returns evidence to the main operating system.</p></div><div className="agent-flow"><span>Objective</span><ChevronRight size={15} /><span>Route</span><ChevronRight size={15} /><span>Sub-agents</span><ChevronRight size={15} /><span>Result</span></div></div>
    <div className="panel-card agent-dispatch-panel"><div><div className="micro-label">ASSIGN A DUTY</div><h2>Give David one outcome to coordinate.</h2></div><textarea value={objective} onChange={(event) => setObjective(event.target.value)} rows={3} placeholder="Describe the outcome you want David and the specialist agents to deliver..." /><div className="agent-dispatch-footer"><span><ShieldCheck size={14} /> High-impact actions remain behind approval gates.</span><button className="button button-primary" onClick={dispatchObjective} disabled={!objective.trim() || dispatching}><Send size={14} /> {dispatching ? "Working..." : "Run through David"}</button></div></div>
    {loading ? <div className="panel-card padded-card"><span className="micro-label">LOADING SUB-AGENTS</span></div> : <div className="agent-grid">{agents.map((agent) => { const role = String(agent.role || "agent"); const name = String(agent.name || role.replaceAll("_", " ")); const busy = Boolean(agent.is_busy); return <button className="panel-card agent-card" key={role} onClick={() => { setObjective(`Assign the ${name} to ${objective}`); notify({ kind: "info", text: `${name} selected for the next objective.` }); }}><div className="agent-card-top"><div className="agent-icon tone-blue"><Bot size={20} /></div><span className={cx("status-tag", busy ? "tag-red" : "tag-green")}>{busy ? "Working" : "Available"}</span></div><h3>{name}</h3><p className="agent-role">{String(agent.role || "specialist")}</p><p className="agent-detail">{busy ? "Currently processing a governed sub-task." : "Ready to receive a bounded duty from David."}</p><div className="agent-card-footer"><span>{String(agent.completed_tasks || 0)} completed · {String(agent.active_tasks || 0)} active</span><ArrowUpRight size={16} /></div></button>; })}</div>}
  </div>;
}

function MemoryView({ notify }: { notify: (toast: Toast) => void }) { const memories = [{ title: "Brand voice", detail: "Confident, direct, warm. Avoid jargon and empty superlatives.", tag: "Preference", icon: Palette }, { title: "Launch objective", detail: "Atlas should become the clearest entry point for first-time customers.", tag: "Decision", icon: Target }, { title: "Brand handbook", detail: "14 pages · Indexed 1 hour ago · 86 searchable passages", tag: "Source", icon: FileText }, { title: "Customer profile", detail: "Business owners who need leverage without adding headcount.", tag: "Knowledge", icon: Users }]; return <div><PageHeader route="memory" action={<button className="button button-primary" onClick={() => notify({ kind: "success", text: "Memory capture opened." })}><Plus size={16} /> Add memory</button>} /><div className="memory-overview"><div className="memory-score"><div className="score-ring"><strong>92</strong><span>/100</span></div><div><span className="micro-label">CONTEXT QUALITY</span><h2>David knows how you work.</h2><p>Connect two more sources to improve project-level recommendations.</p></div></div><div className="memory-facts"><div><strong>128</strong><span>memories</span></div><div><strong>24</strong><span>sources</span></div><div><strong>06</strong><span>projects</span></div></div></div><div className="memory-grid">{memories.map((memory) => { const Icon = memory.icon; return <button className="panel-card memory-card" key={memory.title} onClick={() => notify({ kind: "info", text: `${memory.title} memory opened for editing.` })}><div className="memory-card-top"><span className="memory-icon"><Icon size={17} /></span><span className="status-tag tag-blue">{memory.tag}</span><MoreHorizontal size={16} /></div><h3>{memory.title}</h3><p>{memory.detail}</p><div className="memory-card-footer"><span>Last used today</span><ArrowUpRight size={15} /></div></button>; })}</div></div>; }

function CreativeView({ onNavigate, notify }: { onNavigate: (route: RouteKey) => void; notify: (toast: Toast) => void }) { const tools = [{ title: "Website builder", detail: "Brief to responsive, on-brand site.", icon: Globe2, route: "website-builder" as RouteKey, color: "red" }, { title: "Video studio", detail: "Script, scenes, voice, and social cuts.", icon: Film, route: "video-studio" as RouteKey, color: "purple" }, { title: "Voice studio", detail: "Natural narration and real-time conversation.", icon: AudioLines, route: "creative" as RouteKey, color: "blue" }, { title: "Image lab", detail: "Campaign visuals, thumbnails, and diagrams.", icon: ImageIcon, route: "creative" as RouteKey, color: "amber" }, { title: "Document forge", detail: "Reports, proposals, briefs, and decks.", icon: FileText, route: "creative" as RouteKey, color: "green" }, { title: "Asset library", detail: "A searchable home for every generated artifact.", icon: Library, route: "files" as RouteKey, color: "red" }]; return <div><PageHeader route="creative" action={<button className="button button-primary" onClick={() => notify({ kind: "success", text: "New creative workspace created." })}><Plus size={16} /> New creation</button>} /><div className="creative-hero panel-card"><div><div className="eyebrow-pill">CONNECTED PRODUCTION</div><h2>One brief. Every format.</h2><p>David can turn a product idea into the pages, images, videos, voiceovers, and documents your team needs.</p></div><div className="creative-pipeline"><span>Brief</span><ChevronRight size={15} /><span>Plan</span><ChevronRight size={15} /><span>Generate</span><ChevronRight size={15} /><span>Review</span></div></div><div className="creative-grid">{tools.map((tool) => { const Icon = tool.icon; return <button className="panel-card creative-card" key={tool.title} onClick={() => onNavigate(tool.route)}><div className={cx("creative-icon", `tone-${tool.color}`)}><Icon size={21} /></div><div><h3>{tool.title}</h3><p>{tool.detail}</p></div><ArrowUpRight size={16} className="card-arrow" /></button>; })}</div></div>; }

function WebsiteBuilder({ notify }: { notify: (toast: Toast) => void }) { const [brief, setBrief] = useState("A conversion-focused launch page for Atlas, a calm operating system for independent business owners."); const [building, setBuilding] = useState(false); const [result, setResult] = useState<Record<string, unknown> | null>(null); const [error, setError] = useState(""); async function buildWebsite() { if (!brief.trim() || building) return; setBuilding(true); setError(""); setResult(null); try { const response = await api.websiteGenerate(brief); setResult(response); notify({ kind: "success", text: "Website generation returned a real result for review." }); } catch (cause) { const message = cause instanceof Error ? cause.message : "Website generation is unavailable."; setError(message); notify({ kind: "error", text: "No website was generated. Check the backend and provider configuration." }); } finally { setBuilding(false); } } async function saveBrief() { try { await api.planCreate(brief); notify({ kind: "success", text: "Build brief saved as a live plan." }); } catch { notify({ kind: "error", text: "The build brief could not be saved because the planning service is unavailable." }); } } return <div><PageHeader route="website-builder" action={<div className="header-actions"><button className="button button-secondary" onClick={() => { const html = typeof result?.html === "string" ? result.html : ""; if (!html) { notify({ kind: "info", text: "Generate a real website result before opening a preview." }); return; } const url = URL.createObjectURL(new Blob([html], { type: "text/html" })); window.open(url, "_blank", "noopener,noreferrer"); window.setTimeout(() => URL.revokeObjectURL(url), 60000); }}><Globe2 size={16} /> Preview</button><button className="button button-primary" onClick={() => void buildWebsite()} disabled={building || !brief.trim()}><Rocket size={16} /> {building ? "Calling website service..." : "Build website"}</button></div>} /><div className="builder-layout"><section className="panel-card builder-prompt"><SectionHeader eyebrow="BUILD BRIEF" title="Tell David what to build" detail="The agent will propose the structure, copy, visual direction, and implementation plan." icon={WandSparkles} /><textarea value={brief} onChange={(event) => setBrief(event.target.value)} /><div className="builder-options"><button className="option-chip active"><Palette size={14} /> Brand-aware</button><button className="option-chip"><Globe2 size={14} /> Responsive</button><button className="option-chip"><ShieldCheck size={14} /> Review before publish</button></div><div className="builder-action-row"><span><LockKeyhole size={14} /> Publishing always requires approval</span><button className="button button-primary" onClick={() => void saveBrief()}><Check size={15} /> Save brief</button></div>{error && <div className="provider-result"><span className="micro-label">WEBSITE RESULT</span><p>Generation unavailable: {error}</p></div>}{result && <div className="provider-result"><span className="micro-label">WEBSITE RESULT</span><p>Backend returned a reviewable website payload. Preview it only when an HTML artifact is present.</p></div>}</section><section className="panel-card browser-preview"><div className="browser-top"><div className="browser-dots"><span /><span /><span /></div><span>atlas.david.ai / preview</span><MoreHorizontal size={17} /></div><div className="preview-content"><div className="preview-nav"><strong>ATLAS</strong><span>Product</span><span>How it works</span><span>Pricing</span><button>Start free</button></div><div className="preview-hero"><span className="eyebrow-pill">A CALMER WAY TO OPERATE</span><h2>Your business, with more leverage.</h2><p>Bring your plans, systems, and next best actions into one intelligent workspace.</p><button><Sparkles size={14} /> Explore Atlas</button></div><div className="preview-blocks"><div /><div /><div /></div></div></section></div></div>; }

function VideoStudio({ notify }: { notify: (toast: Toast) => void }) {
  const [prompt, setPrompt] = useState("A 30-second cinematic product teaser for Atlas. Dark cyan HUD, restrained orbital light, confident pacing, premium founder-focused tone.");
  const [working, setWorking] = useState(false);
  const [result, setResult] = useState<string>("");
  async function renderVideo() {
    if (!prompt.trim() || working) return;
    setWorking(true);
    setResult("");
    try {
      const response = await api.providers.execute("video", { prompt, duration_seconds: 30, aspect_ratio: "16:9" }, ["gemini", "runway", "luma"]);
      const url = String(response.artifact_url || response.url || response.output_url || "");
      setResult(url ? `Video artifact ready: ${url}` : "The provider accepted the request but returned no artifact URL. David will not mark this as complete.");
      notify({ kind: url ? "success" : "info", text: url ? "Verified video artifact returned." : "Video provider returned no artifact; nothing was marked generated." });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Video provider unavailable";
      setResult(`Video generation unavailable: ${message}`);
      notify({ kind: "error", text: "No verified video was generated. Check the provider configuration and deployment." });
    } finally {
      setWorking(false);
    }
  }
  return <div><PageHeader route="video-studio" action={<button className="button button-primary" onClick={() => void renderVideo()} disabled={working || !prompt.trim()}><Play size={16} /> {working ? "Requesting provider..." : "Generate video"}</button>} /><div className="video-studio-layout"><section className="panel-card video-prompt-card"><SectionHeader eyebrow="PROVIDER-BACKED PRODUCTION" title="Shape the next cut" icon={Film} /><textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} /><div className="video-controls"><div><span className="micro-label">FORMAT</span><span className="select-like">Landscape 16:9</span></div><div><span className="micro-label">LIGHTING</span><span className="select-like">Dark cyan orbital</span></div><div><span className="micro-label">OUTPUT</span><span className="select-like">One verified artifact</span></div></div><button className="button button-primary wide-button" onClick={() => void renderVideo()} disabled={working || !prompt.trim()}><WandSparkles size={16} /> {working ? "Calling provider" : "Generate video"}</button>{result && <div className="provider-result"><span className="micro-label">PROVIDER RESULT</span><p>{result}</p></div>}</section><section className="panel-card timeline-card"><div className="timeline-header"><div><div className="micro-label">TRUTHFUL RENDER STATE</div><h2>No fake timeline</h2></div><span className={cx("status-tag", working ? "tag-amber" : result.startsWith("Video artifact") ? "tag-green" : "tag-blue")}>{working ? "Working" : result.startsWith("Video artifact") ? "Verified artifact" : result ? "Unavailable" : "Ready"}</span></div><div className="video-canvas"><div className="canvas-orbit" /><div className="canvas-brand">DAVID OS</div><div className="canvas-copy">Provider-backed.<br /><span>Reviewable.</span></div><div className="canvas-caption">The preview updates only after a real provider response.</div></div><div className="timeline-track"><div className="timeline-row"><span className="track-label"><Film size={13} /> Provider</span><div className="track-bar"><i className={working ? "active" : ""} /><i /><i /></div></div><div className="timeline-row"><span className="track-label"><AudioLines size={13} /> Voice</span><div className="voice-wave"><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /><span /></div></div></div></section></div></div>;
}

function FreehandView() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const drawing = useRef(false);
  const [color, setColor] = useState("#39e6e6");
  const [size, setSize] = useState(3);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    context.fillStyle = "#020507";
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.strokeStyle = "rgba(57,230,230,.09)";
    context.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 40) { context.beginPath(); context.moveTo(x, 0); context.lineTo(x, canvas.height); context.stroke(); }
    for (let y = 0; y < canvas.height; y += 40) { context.beginPath(); context.moveTo(0, y); context.lineTo(canvas.width, y); context.stroke(); }
  }, []);
  function point(event: React.PointerEvent<HTMLCanvasElement>) { const canvas = canvasRef.current; if (!canvas) return null; const rect = canvas.getBoundingClientRect(); return { x: (event.clientX - rect.left) * canvas.width / rect.width, y: (event.clientY - rect.top) * canvas.height / rect.height }; }
  function start(event: React.PointerEvent<HTMLCanvasElement>) { const canvas = canvasRef.current; const context = canvas?.getContext("2d"); const p = point(event); if (!context || !p) return; drawing.current = true; canvas?.setPointerCapture(event.pointerId); context.beginPath(); context.moveTo(p.x, p.y); }
  function move(event: React.PointerEvent<HTMLCanvasElement>) { if (!drawing.current) return; const canvas = canvasRef.current; const context = canvas?.getContext("2d"); const p = point(event); if (!context || !p) return; context.strokeStyle = color; context.lineWidth = size; context.lineCap = "round"; context.lineJoin = "round"; context.lineTo(p.x, p.y); context.stroke(); }
  function clear() { const canvas = canvasRef.current; const context = canvas?.getContext("2d"); if (!canvas || !context) return; context.clearRect(0, 0, canvas.width, canvas.height); context.fillStyle = "#020507"; context.fillRect(0, 0, canvas.width, canvas.height); }
  function exportCanvas() { const canvas = canvasRef.current; if (!canvas) return; const link = document.createElement("a"); link.download = "david-freehand.png"; link.href = canvas.toDataURL("image/png"); link.click(); }
  return <div className="tool-page"><PageHeader route="freehand" action={<div className="header-actions"><button className="button button-secondary" onClick={clear}><X size={16} /> Clear</button><button className="button button-primary" onClick={exportCanvas}><Upload size={16} /> Export PNG</button></div>} /><section className="panel-card freehand-panel"><div className="tool-toolbar"><div><span className="micro-label">INK COLOR</span><input aria-label="Ink color" type="color" value={color} onChange={(event) => setColor(event.target.value)} /></div><label><span className="micro-label">BRUSH SIZE</span><input aria-label="Brush size" type="range" min="1" max="20" value={size} onChange={(event) => setSize(Number(event.target.value))} /><strong>{size}px</strong></label><span className="freehand-note">Local canvas · nothing uploaded</span></div><canvas ref={canvasRef} width={1200} height={620} className="freehand-canvas" onPointerDown={start} onPointerMove={move} onPointerUp={() => { drawing.current = false; }} onPointerLeave={() => { drawing.current = false; }} aria-label="Freehand drawing canvas" /></section></div>;
}

function LightingView() {
  const [cyan, setCyan] = useState(72);
  const [blue, setBlue] = useState(28);
  const [ambient, setAmbient] = useState(22);
  const [quiet, setQuiet] = useState(false);
  return <div className="tool-page"><PageHeader route="lighting" action={<span className="connection-pill is-online"><span className="status-dot" /> Local interface control</span>} /><div className="lighting-layout"><section className="panel-card lighting-preview" style={{ background: `radial-gradient(circle at 50% 42%, rgba(57,230,230,${cyan / 500}), rgba(57,167,255,${blue / 700}) 20%, rgba(2,5,7,${Math.max(.75, 1 - ambient / 100)})), #020507` }}><div className="lighting-core" style={{ boxShadow: `0 0 ${20 + cyan / 2}px rgba(57,230,230,${cyan / 100}), 0 0 ${50 + blue}px rgba(57,167,255,${blue / 100})` }}><span /></div><span className="micro-label">PREVIEW / LOCAL ONLY</span><h2>Atmosphere follows your settings.</h2><p>This control changes David’s interface illumination. It does not claim to control physical lights or devices.</p></section><section className="panel-card lighting-controls"><span className="micro-label">LIGHTING MIXER</span><h2>Adjust the system glow.</h2><label><span>Cyan intensity <strong>{cyan}%</strong></span><input type="range" min="0" max="100" value={cyan} onChange={(event) => setCyan(Number(event.target.value))} /></label><label><span>Blue response <strong>{blue}%</strong></span><input type="range" min="0" max="100" value={blue} onChange={(event) => setBlue(Number(event.target.value))} /></label><label><span>Ambient darkness <strong>{ambient}%</strong></span><input type="range" min="0" max="70" value={ambient} onChange={(event) => setAmbient(Number(event.target.value))} /></label><button className={cx("quiet-toggle", quiet && "is-on")} onClick={() => setQuiet((current) => !current)}><span className="status-dot" /> {quiet ? "Quiet mode on" : "Quiet mode off"}</button></section></div></div>;
}

type MultimodalKind = "voice" | "image" | "music" | "enhance" | "edit" | "reshoot";

const multimodalConfig: Record<MultimodalKind, { route: RouteKey; label: string; eyebrow: string; icon: LucideIcon; description: string; placeholder: string; steps: string[]; accent: string }> = {
  voice: { route: "voice-studio", label: "Voice studio", eyebrow: "SPEECH + VOICE", icon: Headphones, description: "Shape narration, dialogue, and spoken interaction with an approval-aware playback boundary.", placeholder: "A warm, confident narration for the Atlas product launch…", steps: ["Script", "Voice", "Preview", "Approve"] , accent: "blue" },
  image: { route: "image-studio", label: "Image lab", eyebrow: "VISUAL GENERATION", icon: ImageIcon, description: "Turn a visual direction into brand-aware campaign images, thumbnails, diagrams, and variants.", placeholder: "A premium editorial product image for Atlas with warm window light…", steps: ["Brief", "Composition", "Variants", "Review"], accent: "purple" },
  music: { route: "music-studio", label: "Music studio", eyebrow: "SOUND + SCORE", icon: AudioWaveform, description: "Plan a soundtrack or sonic identity with mood, duration, instruments, and delivery context.", placeholder: "A restrained cinematic score for a 30-second founder-focused product film…", steps: ["Mood", "Structure", "Mix", "License"], accent: "amber" },
  enhance: { route: "enhance-studio", label: "Enhance media", eyebrow: "MEDIA ENHANCEMENT", icon: Wand2, description: "Prepare an enhancement pass for image, video, or audio while retaining source provenance.", placeholder: "Clean the dialogue, reduce room noise, and preserve the speaker’s natural tone…", steps: ["Source", "Enhance", "Compare", "Export"], accent: "green" },
  edit: { route: "edit-studio", label: "Edit studio", eyebrow: "CONTROLLED EDITING", icon: SlidersHorizontal, description: "Describe the cut, cleanup, translation, or transformation you want before David prepares the edit plan.", placeholder: "Turn this long interview into three social cuts with captions and translated titles…", steps: ["Source", "Edit plan", "Render", "Verify"], accent: "red" },
  reshoot: { route: "reshoot-studio", label: "Reshoot studio", eyebrow: "SCENE DIRECTION", icon: RefreshCw, description: "Direct a scene variation with continuity notes, reference assets, and a reviewable cinematic brief.", placeholder: "Reimagine scene three with a tighter close-up while keeping the same lighting and wardrobe…", steps: ["Reference", "Direction", "Variation", "Review"], accent: "purple" },
};

function MultimodalStudio({ kind, notify }: { kind: MultimodalKind; notify: (toast: Toast) => void }) {
  const config = multimodalConfig[kind];
  const Icon = config.icon;
  const [brief, setBrief] = useState(config.placeholder);
  const [stage, setStage] = useState<"idle" | "planning" | "ready" | "approval">("idle");
  const [plan, setPlan] = useState("");
  const [working, setWorking] = useState(false);

  const createPlan = async () => {
    if (!brief.trim() || working) return;
    setWorking(true);
    setStage("planning");
    try {
      const response = await api.chat(`Create a ${config.label} production plan for this brief. Do not claim that media was generated: ${brief}`);
      const raw = response as unknown as Record<string, unknown>;
      setPlan(String(raw.response || raw.message || raw.content || "A production plan was returned by the configured David backend."));
      setStage("ready");
      notify({ kind: "success", text: `${config.label} plan is ready for review.` });
    } catch {
      setPlan("The planning backend is unavailable. The brief is preserved locally and no media was marked as generated.");
      setStage("approval");
      notify({ kind: "info", text: "Brief saved in interface mode. Connect the backend to plan this workflow live." });
    } finally {
      setWorking(false);
    }
  };

  const requestApproval = () => {
    setStage("approval");
    notify({ kind: "info", text: `Approval requested before ${config.label.toLowerCase()} execution.` });
  };

  return <div className="multimodal-page"><PageHeader route={config.route} action={<div className="header-actions"><span className={cx("status-tag", stage === "ready" ? "tag-green" : stage === "approval" ? "tag-amber" : "tag-blue")}><span className="status-dot" /> {stage === "idle" ? "Brief ready" : stage === "planning" ? "Planning" : stage === "ready" ? "Plan ready" : "Approval gate"}</span><button className="button button-primary" onClick={createPlan} disabled={working || !brief.trim()}>{working ? <TimerReset size={16} className="spin" /> : <Sparkles size={16} />}{working ? "Planning..." : "Plan workflow"}</button></div>} /><div className="multimodal-hero panel-card"><div className={cx("multimodal-icon", `tone-${config.accent}`)}><Icon size={25} /></div><div><div className="eyebrow-pill">{config.eyebrow}</div><h2>{config.label} is ready for a real brief.</h2><p>{config.description}</p></div><div className="multimodal-boundary"><ShieldCheck size={15} /><span>Provider and artifact status remain truthful</span></div></div><div className="multimodal-grid"><section className="panel-card multimodal-brief"><SectionHeader eyebrow="PRODUCTION BRIEF" title="Tell David what to make" detail="David will create a plan first. External rendering stays behind provider readiness and approval." icon={WandSparkles} /><textarea value={brief} onChange={(event) => setBrief(event.target.value)} aria-label={`${config.label} production brief`} /><div className="multimodal-actions"><button className="button button-primary" onClick={createPlan} disabled={working || !brief.trim()}>{working ? <TimerReset size={16} className="spin" /> : <Sparkles size={16} />}{working ? "Planning workflow" : "Generate production plan"}</button><button className="button button-secondary" onClick={requestApproval} disabled={!brief.trim()}><ShieldCheck size={16} /> Request approval</button></div></section><section className="panel-card multimodal-plan"><SectionHeader eyebrow="CINEMATIC PIPELINE" title="Visible production stages" detail="Every stage can be connected to a verified worker without changing the creative surface." icon={Film} /><div className="multimodal-steps">{config.steps.map((step, index) => <div className={cx("multimodal-step", stage === "ready" && index === 0 ? "is-ready" : stage === "approval" && index === config.steps.length - 1 ? "is-blocked" : index === 0 ? "is-active" : "")} key={step}><span>{String(index + 1).padStart(2, "0")}</span><strong>{step}</strong>{index < config.steps.length - 1 && <ChevronRight size={14} />}</div>)}</div><div className="multimodal-preview"><div className="preview-orbit" /><Icon size={24} /><span>{plan || "Your production plan and provider evidence will appear here."}</span></div>{stage === "approval" && <div className="multimodal-approval"><ShieldCheck size={16} /><div><strong>Approval required before external action</strong><span>No media is published, sent, or exported automatically.</span></div></div>}</section></div></div>;
}

function FilesView({ notify }: { notify: (toast: Toast) => void }) { return <div><PageHeader route="files" action={<button className="button button-primary" onClick={() => notify({ kind: "success", text: "File picker ready. Uploads will be indexed into memory." })}><Upload size={16} /> Add knowledge</button>} /><div className="knowledge-banner panel-card"><div className="knowledge-icon"><Database size={24} /></div><div><div className="eyebrow-pill">PRIVATE KNOWLEDGE BASE</div><h2>Give David the source material.</h2><p>Upload documents once and use them across conversations, projects, reports, and creative workflows.</p></div><div className="knowledge-stat"><strong>128</strong><span>indexed memories</span></div></div><div className="file-table panel-card"><div className="file-table-header"><span>Name</span><span>Type</span><span>Indexed</span><span>Used by</span><span /></div>{[{ name: "Brand handbook.pdf", type: "PDF · 14 pages", indexed: "1 hour ago", used: "4 projects", icon: FileText }, { name: "Atlas customer interviews", type: "DOCX · 38 pages", indexed: "Yesterday", used: "2 projects", icon: Users }, { name: "Q3 performance.xlsx", type: "Spreadsheet · 2.4 MB", indexed: "Aug 14, 2026", used: "Operations", icon: Gauge }, { name: "Launch assets", type: "Folder · 28 files", indexed: "Aug 12, 2026", used: "Atlas launch", icon: Library }].map((file) => { const Icon = file.icon; return <button className="file-row" key={file.name} onClick={() => notify({ kind: "info", text: `${file.name} opened.` })}><span className="file-name"><span className="file-icon"><Icon size={16} /></span><strong>{file.name}</strong></span><span>{file.type}</span><span>{file.indexed}</span><span>{file.used}</span><ChevronRight size={16} /></button>; })}</div></div>; }

function ProvidersView({ notify }: { notify: (toast: Toast) => void }) { const providers = [{ name: "David Core", type: "Reasoning & orchestration", status: "Healthy", latency: "420ms", icon: BrainCircuit, tone: "green" }, { name: "OpenAI compatible", type: "Text and multimodal generation", status: "Healthy", latency: "680ms", icon: Sparkles, tone: "green" }, { name: "Voice layer", type: "Speech recognition and synthesis", status: "Needs connection", latency: "—", icon: AudioLines, tone: "amber" }, { name: "Creative render", type: "Image and video generation", status: "Healthy", latency: "1.8s", icon: Film, tone: "green" }]; return <div><PageHeader route="providers" action={<button className="button button-secondary" onClick={() => notify({ kind: "success", text: "Provider health check completed." })}><Activity size={16} /> Run health check</button>} /><div className="provider-health panel-card"><div className="health-ring"><strong>98%</strong><span>ready</span></div><div><div className="eyebrow-pill">SYSTEM READINESS</div><h2>Core capabilities are online.</h2><p>One optional voice connection is waiting for configuration. Everything else is ready for supervised work.</p></div><button className="button button-primary" onClick={() => notify({ kind: "info", text: "Provider setup opened." })}>Manage connections <ArrowUpRight size={14} /></button></div><div className="provider-grid">{providers.map((provider) => { const Icon = provider.icon; return <button className="panel-card provider-card" key={provider.name} onClick={() => notify({ kind: "info", text: `${provider.name} configuration opened.` })}><div className="provider-card-top"><span className={cx("provider-icon", `tone-${provider.tone}`)}><Icon size={18} /></span><span className={cx("status-tag", provider.status === "Healthy" ? "tag-green" : "tag-amber")}>{provider.status}</span></div><h3>{provider.name}</h3><p>{provider.type}</p><div className="provider-footer"><span>Latency <strong>{provider.latency}</strong></span><ArrowUpRight size={15} /></div></button>; })}</div></div>; }

function ActivityView() { return <div><PageHeader route="activity" action={<button className="button button-secondary"><FileText size={16} /> Export log</button>} /><div className="activity-summary"><div><span className="micro-label">LAST 7 DAYS</span><strong>86 system events</strong><p>All actions are recorded with source, status, and approval context.</p></div><div className="event-bars"><span style={{ height: "35%" }} /><span style={{ height: "52%" }} /><span style={{ height: "42%" }} /><span style={{ height: "70%" }} /><span style={{ height: "58%" }} /><span style={{ height: "84%" }} /><span style={{ height: "66%" }} /></div></div><div className="panel-card log-card"><div className="log-header"><span>EVENT</span><span>CONTEXT</span><span>TIME</span><span>STATUS</span></div>{activityItems.concat([{ icon: Github, title: "Repository sync completed", detail: "GitHub / David-ademola", color: "purple" }]).map((item) => <div className="log-row" key={item.title}><span className="log-event"><span className={cx("log-icon", `tone-${item.color}`)}><item.icon size={15} /></span><strong>{item.title}</strong></span><span>{item.detail}</span><time>Today</time><span className="status-tag tag-green">Verified</span></div>)}</div></div>; }

function DevicesView({ notify }: { notify: (toast: Toast) => void }) { return <div><PageHeader route="devices" action={<button className="button button-primary" onClick={() => notify({ kind: "info", text: "Device pairing flow started." })}><Plus size={16} /> Pair device</button>} /><div className="device-grid"><div className="panel-card device-card device-active"><div className="device-card-top"><span className="device-icon"><Command size={21} /></span><span className="status-tag tag-green">Current session</span></div><h3>Web command center</h3><p>Chrome · Ubuntu · Last active now</p><div className="device-footer"><ShieldCheck size={14} /> Trusted device</div></div><div className="panel-card device-card"><div className="device-card-top"><span className="device-icon tone-blue"><Mic size={21} /></span><span className="status-tag tag-blue">Ready</span></div><h3>Voice companion</h3><p>Use your voice to ask, interrupt, and approve.</p><button className="text-button" onClick={() => notify({ kind: "info", text: "Voice companion setup opened." })}>Configure voice <ArrowUpRight size={14} /></button></div><div className="panel-card device-card"><div className="device-card-top"><span className="device-icon tone-purple"><Github size={21} /></span><span className="status-tag tag-amber">Connected</span></div><h3>GitHub workspace</h3><p>David-ademola · Repository sync enabled.</p><button className="text-button" onClick={() => notify({ kind: "success", text: "GitHub workspace is connected." })}>Review connection <ArrowUpRight size={14} /></button></div></div></div>; }

function SettingsView({ notify, preferences, onPreferenceChange }: { notify: (toast: Toast) => void; preferences: DavidSettings; onPreferenceChange: (key: DavidPreferenceKey, value: boolean) => void }) {
  const settings: Array<{ key: DavidPreferenceKey; title: string; detail: string; icon: LucideIcon }> = [
    { key: "approvalGates", title: "Approval gates", detail: "Ask before sending, publishing, deleting, or spending.", icon: ShieldCheck },
    { key: "longTermMemory", title: "Long-term memory", detail: "Remember preferences and project context across sessions.", icon: BrainCircuit },
    { key: "backgroundMonitoring", title: "Background monitoring", detail: "Let David watch approved sources and surface changes.", icon: Activity },
    { key: "voiceActivation", title: "Voice activation", detail: "Use voice input and spoken responses when available.", icon: Mic },
    { key: "quietMode", title: "Quiet mode", detail: "Reduce nonessential interface motion and audio cues.", icon: Headphones },
    { key: "reducedMotion", title: "Reduced motion", detail: "Disable nonessential animation while keeping state changes visible.", icon: TimerReset },
    { key: "highContrast", title: "High contrast", detail: "Increase cyan edge contrast and text legibility across the shell.", icon: Sun },
  ];
  return <div><PageHeader route="settings" action={<button className="button button-primary" onClick={() => notify({ kind: "success", text: "Settings saved locally for this browser." })}><Check size={16} /> Save changes</button>} /><div className="settings-layout"><section className="panel-card settings-card"><SectionHeader eyebrow="CONTROL & TRUST" title="How David should act" icon={LockKeyhole} />{settings.map((setting) => { const Icon = setting.icon; const enabled = preferences[setting.key]; return <button className="setting-row" key={setting.key} onClick={() => { onPreferenceChange(setting.key, !enabled); notify({ kind: "info", text: `${setting.title} ${enabled ? "disabled" : "enabled"}.` }); }} aria-pressed={enabled}><span className="setting-icon"><Icon size={17} /></span><span className="setting-copy"><strong>{setting.title}</strong><small>{setting.detail}</small></span><span className={cx("toggle", enabled && "toggle-on")}><span /></span></button>; })}</section><section className="panel-card settings-card"><SectionHeader eyebrow="YOUR IDENTITY" title="Brand and workspace" icon={UserRound} /><div className="profile-form"><label>Workspace name<input defaultValue="David Ademola" /></label><label>Default brand voice<select defaultValue="confident"><option value="confident">Confident / direct</option><option value="warm">Warm / conversational</option><option value="technical">Technical / precise</option></select></label><label>Primary timezone<select defaultValue="london"><option value="london">Europe / London</option><option value="lagos">Africa / Lagos</option><option value="new-york">America / New York</option></select></label></div><div className="settings-note"><ShieldCheck size={15} /> Preferences persist locally and never expose provider secrets.</div></section></div></div>;
}

function OwnerView({ notify }: { notify: (toast: Toast) => void }) { return <div><PageHeader route="owner" action={<button className="button button-secondary" onClick={() => notify({ kind: "info", text: "Owner audit report generated." })}><FileText size={16} /> Generate report</button>} /><div className="owner-grid"><div className="owner-stat panel-card"><span className="micro-label">TOTAL WORKSPACES</span><strong>24</strong><p>+6 this month</p></div><div className="owner-stat panel-card"><span className="micro-label">AUTOMATION RUNS</span><strong>1,284</strong><p>96.8% completed successfully</p></div><div className="owner-stat panel-card"><span className="micro-label">CAPABILITY COVERAGE</span><strong>84%</strong><p>12 optional connectors available</p></div><div className="owner-stat panel-card"><span className="micro-label">TRUST SCORE</span><strong>98.4</strong><p>Approval policy active</p></div></div><div className="split-grid section-block"><div className="panel-card padded-card"><SectionHeader eyebrow="PLATFORM ROADMAP" title="Next capability layers" icon={Rocket} /><div className="roadmap-list">{["Scheduled background agents", "Template marketplace", "Team workspaces and roles", "Public developer actions"].map((item, index) => <div className="roadmap-row" key={item}><span className="roadmap-number">0{index + 1}</span><strong>{item}</strong><span className={cx("status-tag", index < 2 ? "tag-amber" : "tag-blue")}>{index < 2 ? "Building" : "Planned"}</span></div>)}</div></div><div className="panel-card padded-card"><SectionHeader eyebrow="GOVERNANCE" title="Protection is online" icon={ShieldCheck} /><div className="governance-list"><div><Check size={15} /> Sensitive actions require confirmation</div><div><Check size={15} /> Provider keys stay server-side</div><div><Check size={15} /> Activity is recorded for review</div><div><Check size={15} /> Knowledge stays workspace-scoped</div></div><button className="button button-secondary wide-button" onClick={() => notify({ kind: "success", text: "Governance controls reviewed." })}>Review policy <ArrowUpRight size={14} /></button></div></div></div>; }

function StatCard({ label, value, trend, icon: Icon, tone }: { label: string; value: string; trend: string; icon: LucideIcon; tone: string }) { return <div className="stat-card"><div className={cx("stat-icon", `tone-${tone}`)}><Icon size={17} /></div><div><span>{label}</span><strong>{value}</strong><small>{trend}</small></div></div>; }
function SectionHeader({ eyebrow, title, detail, icon: Icon, action }: { eyebrow: string; title: string; detail?: string; icon: LucideIcon; action?: React.ReactNode }) { return <div className="section-header"><div className="section-heading"><span className="section-icon"><Icon size={16} /></span><div><div className="micro-label">{eyebrow}</div><h2>{title}</h2>{detail && <p>{detail}</p>}</div></div>{action}</div>; }
function PromptBox({ onPrompt }: { onPrompt: (prompt: string) => void }) { const [value, setValue] = useState(""); return <div className="prompt-box"><textarea value={value} onChange={(event) => setValue(event.target.value)} placeholder="e.g. Launch a campaign for my new product next month..." rows={3} /><div className="prompt-footer"><div className="prompt-tools"><button><Upload size={14} /></button><button><Mic size={14} /></button><span>David will route the work automatically</span></div><button className="button button-primary" onClick={() => { if (value.trim()) onPrompt(value); }} disabled={!value.trim()}><Send size={14} /> Run objective</button></div><div className="prompt-suggestions">{starterPrompts.slice(0, 2).map((prompt) => <button key={prompt} onClick={() => { setValue(prompt); onPrompt(prompt); }}>{prompt}<ArrowUpRight size={13} /></button>)}</div></div>; }
function RadarItem({ icon: Icon, title, detail, tag, tone, onClick }: { icon: LucideIcon; title: string; detail: string; tag: string; tone: string; onClick: () => void }) { return <button className="radar-item" onClick={onClick}><span className={cx("radar-icon", `tone-${tone}`)}><Icon size={16} /></span><span className="radar-copy"><strong>{title}</strong><small>{detail}</small></span><span className={cx("status-tag", `tag-${tone}`)}>{tag}</span><ChevronRight size={15} /></button>; }
function CapabilityCard({ icon: Icon, title, detail, color, onClick }: { icon: LucideIcon; title: string; detail: string; color: string; onClick: () => void }) { return <button className="capability-card" onClick={onClick}><span className={cx("capability-icon", `tone-${color}`)}><Icon size={19} /></span><span><strong>{title}</strong><small>{detail}</small></span><ArrowUpRight size={15} /></button>; }
function ActivityRow({ icon: Icon, title, detail, color }: { icon: LucideIcon; title: string; detail: string; color: string }) { return <div className="activity-row"><span className={cx("activity-icon", `tone-${color}`)}><Icon size={15} /></span><span><strong>{title}</strong><small>{detail}</small></span><span className="status-tag tag-green">Done</span></div>; }
function ContextRow({ label, value }: { label: string; value: string }) { return <div className="context-row"><span>{label}</span><strong>{value}</strong></div>; }

export { PageHeader };
