"use client";

import {
  Activity,
  Archive,
  ArrowRight,
  BrainCircuit,
  Check,
  ChevronRight,
  CircleHelp,
  ClipboardList,
  Cloud,
  Code2,
  Command,
  Cpu,
  Database,
  ExternalLink,
  FileText,
  Fingerprint,
  FolderKanban,
  Gauge,
  Globe2,
  Headphones,
  Image as ImageIcon,
  Layers3,
  LayoutDashboard,
  Loader2,
  LockKeyhole,
  Menu,
  Mic,
  MicOff,
  Monitor,
  MoreHorizontal,
  Network,
  PanelRight,
  Pause,
  Play,
  Plus,
  Radio,
  RefreshCw,
  Search,
  Send,
  Settings,
  ShieldCheck,
  Sparkles,
  Square,
  TerminalSquare,
  Trash2,
  Upload,
  UserRound,
  Video,
  Wand2,
  Wifi,
  WifiOff,
  X,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { api, toAudioUrl } from "../lib/api";
import type {
  Adapter,
  AssetItem,
  BackendHealth,
  Capability,
  ChatResponse,
  ConversationItem,
  GoalPlan,
  GenerationItem,
  MemoryItem,
  ProjectItem,
  ReadinessResponse,
  RouteResult,
  RunDetails,
  SupabaseStatus,
  TaskItem,
  VoicePhase,
  VoiceStatus,
} from "../lib/types";

type IconType = LucideIcon;

type Message = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  provider?: string;
  createdAt: string;
};

type Toast = { kind: "success" | "error" | "info"; text: string };

const navItems: Array<{ id: string; label: string; icon: IconType; group?: string }> = [
  { id: "dashboard", label: "Command center", icon: LayoutDashboard, group: "Workspace" },
  { id: "chat", label: "David chat", icon: Command, group: "Workspace" },
  { id: "agents", label: "Agent runs", icon: BrainCircuit, group: "Workspace" },
  { id: "voice", label: "Voice", icon: Headphones, group: "Workspace" },
  { id: "content", label: "Content", icon: FileText, group: "Workspace" },
  { id: "memory", label: "Memory", icon: Database, group: "Workspace" },
  { id: "tasks", label: "Tasks", icon: ClipboardList, group: "Workspace" },
  { id: "projects", label: "Projects", icon: FolderKanban, group: "Workspace" },
  { id: "library", label: "Library", icon: Archive, group: "Workspace" },
  { id: "activity", label: "Activity", icon: Activity, group: "Observe" },
  { id: "providers", label: "Providers", icon: Network, group: "Observe" },
  { id: "devices", label: "Devices", icon: Monitor, group: "Observe" },
  { id: "connectors", label: "Connectors", icon: Layers3, group: "Operate" },
  { id: "automation", label: "Automation", icon: TerminalSquare, group: "Operate" },
  { id: "website-builder", label: "Website builder", icon: Globe2, group: "Creative Suite" },
  { id: "video-studio", label: "Video studio", icon: Video, group: "Creative Suite" },
  { id: "image-studio", label: "Image studio", icon: ImageIcon, group: "Creative Suite" },
  { id: "music-studio", label: "Music studio", icon: Headphones, group: "Creative Suite" },
  { id: "artwork-studio", label: "Artwork studio", icon: Sparkles, group: "Creative Suite" },
  { id: "enhance-studio", label: "Enhance media", icon: Wand2, group: "Creative Suite" },
  { id: "edit-studio", label: "Edit studio", icon: ClipboardList, group: "Creative Suite" },
  { id: "reshoot-studio", label: "Reshoot studio", icon: RefreshCw, group: "Creative Suite" },
  { id: "settings", label: "Settings", icon: Settings, group: "System" },
  { id: "owner", label: "Owner console", icon: ShieldCheck, group: "System" },
];

const routeLabels: Record<string, string> = {
  dashboard: "Command center",
  chat: "David chat",
  agents: "Agent runs",
  voice: "Voice",
  content: "Content",
  memory: "Memory",
  tasks: "Tasks",
  projects: "Projects",
  library: "Library",
  activity: "Activity",
  providers: "Providers",
  devices: "Devices",
  connectors: "Connectors",
  automation: "Automation",
  "website-builder": "Website builder",
  "video-studio": "Video studio",
  "image-studio": "Image studio",
  "music-studio": "Music studio",
  "artwork-studio": "Artwork studio",
  "enhance-studio": "Enhance media",
  "edit-studio": "Edit studio",
  "reshoot-studio": "Reshoot studio",
  settings: "Settings",
  owner: "Owner console",
};

const routeAliases: Record<string, string> = {
  "agent-runs": "agents",
  runs: "agents",
  website: "website-builder",
  video: "video-studio",
  image: "image-studio",
  music: "music-studio",
  artwork: "artwork-studio",
  enhance: "enhance-studio",
  edit: "edit-studio",
  reshoot: "reshoot-studio",
};

const toneOptions = ["calm", "focused", "analytical", "creative", "direct"] as const;

function uid(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

function safeArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

function formatDate(value?: string) {
  if (!value) return "just now";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function stateClass(state?: string) {
  const normalized = state?.toLowerCase() || "unknown";
  if (normalized.includes("ready") || normalized.includes("healthy") || normalized.includes("available") || normalized === "ok") return "text-signal";
  if (normalized.includes("config") || normalized.includes("approval") || normalized.includes("credential") || normalized.includes("degraded")) return "text-amber";
  if (normalized.includes("offline") || normalized.includes("unavailable") || normalized.includes("error")) return "text-crimson";
  return "text-smoke";
}

function StateDot({ state, label }: { state?: string; label?: string }) {
  return (
    <span className="inline-flex items-center gap-2 text-xs">
      <span className={`h-2 w-2 rounded-full ${stateClass(state).replace("text-", "bg-")}`} />
      <span className={stateClass(state)}>{label || state || "UNKNOWN"}</span>
    </span>
  );
}

function Button({ children, variant = "default", className = "", ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "default" | "primary" | "ghost" | "danger" }) {
  const styles = {
    default: "border-white/10 bg-white/[0.04] text-white hover:bg-white/[0.08]",
    primary: "border-crimson/60 bg-crimson text-white shadow-glow hover:bg-ember",
    ghost: "border-transparent bg-transparent text-smoke hover:bg-white/[0.06] hover:text-white",
    danger: "border-crimson/30 bg-crimson/10 text-ember hover:bg-crimson/20",
  };
  return (
    <button className={`inline-flex min-h-10 items-center justify-center gap-2 rounded-lg border px-3 text-sm font-semibold transition ${styles[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}

function Card({ children, className = "", red = false }: { children: React.ReactNode; className?: string; red?: boolean }) {
  return <section className={`panel rounded-2xl p-5 ${red ? "panel-red" : ""} ${className}`}>{children}</section>;
}

function SectionHeading({ eyebrow, title, detail, action }: { eyebrow: string; title: string; detail?: string; action?: React.ReactNode }) {
  return (
    <div className="mb-5 flex items-end justify-between gap-4">
      <div>
        <p className="micro-label">{eyebrow}</p>
        <h2 className="mt-1 text-xl font-semibold tracking-tight text-white">{title}</h2>
        {detail && <p className="mt-1 text-sm text-smoke">{detail}</p>}
      </div>
      {action}
    </div>
  );
}

function CoreVisual({ phase = "idle", small = false }: { phase?: VoicePhase | string; small?: boolean }) {
  return (
    <div className={`relative flex items-center justify-center ${small ? "h-36" : "h-56"}`}>
      <div className={`ai-core ${small ? "ai-core-small" : ""}`} aria-label={`David AI core ${phase}`} role="img">
        <Sparkles className="relative z-10 h-8 w-8 text-white/90" />
        <span className="core-status">{phase}</span>
      </div>
    </div>
  );
}

function Metric({ label, value, detail, icon: Icon, tone = "red" }: { label: string; value: string; detail: string; icon: IconType; tone?: "red" | "green" | "blue" | "amber" }) {
  const colors = { red: "text-ember", green: "text-signal", blue: "text-blue-300", amber: "text-amber" };
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.025] p-4">
      <div className="flex items-center justify-between"><span className="micro-label">{label}</span><Icon className={`h-4 w-4 ${colors[tone]}`} /></div>
      <div className="mt-3 text-2xl font-semibold text-white">{value}</div>
      <p className="mt-1 text-xs text-smoke">{detail}</p>
    </div>
  );
}

function CapabilityRow({ item }: { item: Capability }) {
  return (
    <div className="flex items-start justify-between gap-3 rounded-xl border border-white/8 bg-black/20 p-3">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2"><span className="font-semibold text-white">{item.name || item.id}</span><span className="rounded-full border border-white/10 px-2 py-0.5 text-[10px] uppercase tracking-wider text-smoke">{item.category || "capability"}</span></div>
        <p className="mt-1 truncate text-xs text-smoke">{item.id} {item.adapter ? `· ${item.adapter}` : ""}</p>
      </div>
      <StateDot state={item.state || (item.available ? "AVAILABLE" : "UNAVAILABLE")} />
    </div>
  );
}

function EmptyState({ icon: Icon, title, detail, action }: { icon: IconType; title: string; detail: string; action?: React.ReactNode }) {
  return <div className="flex min-h-44 flex-col items-center justify-center rounded-xl border border-dashed border-white/10 bg-black/10 p-6 text-center"><Icon className="mb-3 h-7 w-7 text-smoke" /><h3 className="font-semibold text-white">{title}</h3><p className="mt-1 max-w-sm text-sm text-smoke">{detail}</p>{action && <div className="mt-4">{action}</div>}</div>;
}

function DavidApp({ route }: { route: string }) {
  const router = useRouter();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [fabricReady, setFabricReady] = useState<ReadinessResponse | null>(null);
  const [voice, setVoice] = useState<VoiceStatus | null>(null);
  const [capabilities, setCapabilities] = useState<Capability[]>([]);
  const [adapters, setAdapters] = useState<Adapter[]>([]);
  const [providers, setProviders] = useState<Array<Record<string, unknown>>>([]);
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [projects, setProjects] = useState<ProjectItem[]>([]);
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [assets, setAssets] = useState<AssetItem[]>([]);
  const [generations, setGenerations] = useState<GenerationItem[]>([]);
  const [storageStatus, setStorageStatus] = useState<SupabaseStatus | null>(null);
  const [toast, setToast] = useState<Toast | null>(null);
  const [tone, setTone] = useState<(typeof toneOptions)[number]>("focused");
  const [isRefreshing, setIsRefreshing] = useState(false);

  const currentRoute = pathname?.split("/").filter(Boolean).slice(-1)[0] || route || "dashboard";
  const normalizedRoute = routeAliases[currentRoute] || currentRoute;
  const activeRoute = normalizedRoute === "auth" ? "auth" : routeLabels[normalizedRoute] ? normalizedRoute : "dashboard";

  const notify = (kind: Toast["kind"], text: string) => {
    setToast({ kind, text });
    window.setTimeout(() => setToast(null), 4200);
  };

  const refresh = async () => {
    setIsRefreshing(true);
    const results = await Promise.allSettled([
      api.health(),
      api.voiceStatus(),
      api.intelligence.readiness(),
      api.intelligence.capabilities(),
      api.intelligence.adapters(),
      api.intelligence.providers(),
      api.memories(),
      api.projects(),
      api.tasks(),
      api.conversations(),
      api.library.status(),
      api.library.assets(),
      api.library.generations(),
    ]);
    const [healthResult, voiceResult, readinessResult, capabilityResult, adapterResult, providerResult, memoryResult, projectResult, taskResult, conversationResult, storageResult, assetsResult, generationsResult] = results;
    if (healthResult.status === "fulfilled") setHealth(healthResult.value);
    if (voiceResult.status === "fulfilled") setVoice(voiceResult.value);
    if (readinessResult.status === "fulfilled") setFabricReady(readinessResult.value);
    if (capabilityResult.status === "fulfilled") setCapabilities(safeArray<Capability>(capabilityResult.value.capabilities));
    if (adapterResult.status === "fulfilled") setAdapters(safeArray<Adapter>(adapterResult.value.adapters));
    if (providerResult.status === "fulfilled") {
      const value = providerResult.value as { providers?: unknown[] };
      setProviders(safeArray<Record<string, unknown>>(value.providers));
    }
    if (memoryResult.status === "fulfilled") setMemories(safeArray<MemoryItem>(memoryResult.value));
    if (projectResult.status === "fulfilled") setProjects(safeArray<ProjectItem>(projectResult.value));
    if (taskResult.status === "fulfilled") setTasks(safeArray<TaskItem>(taskResult.value));
    if (conversationResult.status === "fulfilled") setConversations(safeArray<ConversationItem>(conversationResult.value));
    if (storageResult.status === "fulfilled") setStorageStatus(storageResult.value);
    if (assetsResult.status === "fulfilled") setAssets(safeArray<AssetItem>(assetsResult.value));
    if (generationsResult.status === "fulfilled") setGenerations(safeArray<GenerationItem>(generationsResult.value));
    setIsRefreshing(false);
  };

  useEffect(() => { void refresh(); }, []);

  if (activeRoute === "auth") return <AuthWorkspace onSuccess={() => router.push("/dashboard")} notify={notify} />;

  const go = (id: string) => {
    setMobileOpen(false);
    router.push(`/${id}`);
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-ink">
      <div className="shell-grid absolute inset-0" />
      <div className="scan-lines absolute inset-0" />
      <div className="noise" />
      <div className="relative z-10 flex min-h-screen">
        <aside className={`fixed inset-y-0 left-0 z-40 w-72 transform border-r border-white/10 bg-[#07070b]/95 p-5 backdrop-blur-xl transition-transform lg:static lg:translate-x-0 ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>
          <div className="flex items-center justify-between"><button className="flex items-center gap-3 text-left" onClick={() => go("dashboard")} aria-label="Go to David AI command center"><span className="grid h-10 w-10 place-items-center rounded-xl border border-crimson/60 bg-crimson/10 shadow-glow"><Sparkles className="h-5 w-5 text-ember" /></span><span><span className="block font-bold tracking-wide text-white">DAVID AI</span><span className="micro-label">intelligence fabric</span></span></button><button className="rounded-lg p-2 text-smoke hover:bg-white/5 lg:hidden" onClick={() => setMobileOpen(false)} aria-label="Close navigation"><X className="h-5 w-5" /></button></div>
          <div className="mt-7 rounded-xl border border-white/10 bg-white/[0.025] p-3"><div className="flex items-center justify-between"><span className="micro-label">Fabric state</span><StateDot state={String(fabricReady?.status || (health ? "HEALTHY" : "CONNECTING"))} /></div><div className="mt-3 flex items-center justify-between text-xs text-smoke"><span>Capabilities</span><span className="text-white">{capabilities.length || "—"}</span></div><div className="mt-1 flex items-center justify-between text-xs text-smoke"><span>Adapters</span><span className="text-white">{adapters.length || "—"}</span></div></div>
          <nav className="mt-7 space-y-5" aria-label="Primary navigation">{["Workspace", "Observe", "Operate", "Studios", "System"].map((group) => <div key={group}><p className="mb-2 px-3 micro-label">{group}</p><div className="space-y-1">{navItems.filter((item) => item.group === group).map((item) => { const Icon = item.icon; const active = activeRoute === item.id; return <button key={item.id} onClick={() => go(item.id)} className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm transition ${active ? "border border-crimson/30 bg-crimson/10 text-white shadow-[inset_3px_0_0_#ff2b3d]" : "text-smoke hover:bg-white/[0.04] hover:text-white"}`}><Icon className={`h-4 w-4 ${active ? "text-ember" : ""}`} /><span>{item.label}</span>{active && <ChevronRight className="ml-auto h-3.5 w-3.5 text-ember" />}</button>; })}</div></div>)}</nav>
          <div className="absolute bottom-5 left-5 right-5 rounded-xl border border-white/10 bg-black/20 p-3"><div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-signal shadow-[0_0_12px_#37e3a4]" /><span className="text-xs font-semibold text-white">Human-guided mode</span></div><p className="mt-1 text-[11px] leading-4 text-smoke">Destructive actions remain approval-gated.</p></div>
        </aside>
        {mobileOpen && <button className="fixed inset-0 z-30 bg-black/65 lg:hidden" onClick={() => setMobileOpen(false)} aria-label="Close navigation overlay" />}
        <main className="min-w-0 flex-1">
          <header className="sticky top-0 z-20 border-b border-white/10 bg-[#050508]/80 backdrop-blur-xl"><div className="flex min-h-[76px] items-center justify-between gap-4 px-4 sm:px-6 lg:px-9"><div className="flex items-center gap-3"><button className="rounded-xl border border-white/10 p-2 text-smoke hover:bg-white/5 lg:hidden" onClick={() => setMobileOpen(true)} aria-label="Open navigation"><Menu className="h-5 w-5" /></button><div><p className="micro-label">{activeRoute === "dashboard" ? "David AI / home" : `David AI / ${activeRoute}`}</p><h1 className="mt-1 text-lg font-semibold text-white">{routeLabels[activeRoute] || "Command center"}</h1></div></div><div className="flex items-center gap-2 sm:gap-3"><div className="hidden items-center gap-2 rounded-xl border border-white/10 bg-white/[0.025] px-3 py-2 sm:flex"><span className="h-2 w-2 rounded-full bg-signal" /><span className="text-xs text-smoke">{health ? "Backend connected" : "Checking backend"}</span></div><select className="hidden rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2 text-xs text-smoke outline-none sm:block" value={tone} onChange={(event) => setTone(event.target.value as (typeof toneOptions)[number])} aria-label="David tone"><option value="calm">Calm</option><option value="focused">Focused</option><option value="analytical">Analytical</option><option value="creative">Creative</option><option value="direct">Direct</option></select><button className="rounded-xl border border-white/10 p-2 text-smoke hover:bg-white/5" onClick={() => void refresh()} aria-label="Refresh command center" disabled={isRefreshing}>{isRefreshing ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}</button><button className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.04] p-2 text-left hover:bg-white/[0.07]" onClick={() => go("owner")} aria-label="Open owner console"><span className="grid h-7 w-7 place-items-center rounded-lg bg-crimson/20 text-ember"><UserRound className="h-4 w-4" /></span><span className="hidden text-xs font-semibold text-white sm:block">OWNER</span></button></div></div></header>
          <div className="mx-auto max-w-[1600px] p-4 sm:p-6 lg:p-9">{renderWorkspace(activeRoute, { health, voice, fabricReady, capabilities, adapters, providers, memories, projects, tasks, conversations, assets, generations, storageStatus, tone, notify, refresh, go })}</div>
        </main>
      </div>
      {toast && <div className={`fixed bottom-5 right-5 z-50 max-w-sm rounded-xl border px-4 py-3 text-sm shadow-2xl ${toast.kind === "error" ? "border-crimson/40 bg-crimson/15 text-ember" : toast.kind === "success" ? "border-signal/30 bg-signal/10 text-signal" : "border-white/10 bg-panel text-white"}`} role="status">{toast.text}</div>}
    </div>
  );
}

type WorkspaceProps = {
  health: BackendHealth | null;
  voice: VoiceStatus | null;
  fabricReady: ReadinessResponse | null;
  capabilities: Capability[];
  adapters: Adapter[];
  providers: Array<Record<string, unknown>>;
  memories: MemoryItem[];
  projects: ProjectItem[];
  tasks: TaskItem[];
  conversations: ConversationItem[];
  assets: AssetItem[];
  generations: GenerationItem[];
  storageStatus: SupabaseStatus | null;
  tone: string;
  notify: (kind: Toast["kind"], text: string) => void;
  refresh: () => Promise<void>;
  go: (id: string) => void;
};

function renderWorkspace(route: string, props: WorkspaceProps) {
  switch (route) {
    case "chat": return <ChatWorkspace voice={props.voice} tone={props.tone} conversations={props.conversations} notify={props.notify} />;
    case "agents": return <AgentWorkspace capabilities={props.capabilities} notify={props.notify} />;
    case "voice": return <VoiceWorkspace voice={props.voice} notify={props.notify} />;
    case "content": return <ContentWorkspace notify={props.notify} />;
    case "memory": return <MemoryWorkspace memories={props.memories} notify={props.notify} refresh={props.refresh} />;
    case "tasks": return <TasksWorkspace tasks={props.tasks} projects={props.projects} notify={props.notify} refresh={props.refresh} />;
    case "projects": return <ProjectsWorkspace projects={props.projects} notify={props.notify} refresh={props.refresh} />;
    case "library": return <LibraryWorkspace assets={props.assets} generations={props.generations} storageStatus={props.storageStatus} projects={props.projects} notify={props.notify} refresh={props.refresh} />;
    case "providers": return <ProvidersWorkspace providers={props.providers} adapters={props.adapters} capabilities={props.capabilities} fabricReady={props.fabricReady} />;
    case "devices": return <DevicesWorkspace voice={props.voice} />;
    case "connectors": return <ConnectorsWorkspace adapters={props.adapters} />;
    case "automation": return <AutomationWorkspace capabilities={props.capabilities} notify={props.notify} />;
    case "website-builder": return <WebsiteBuilderWorkspace notify={props.notify} />;
    case "video-studio": return <StudioWorkspace kind="video" capabilities={props.capabilities} />;
    case "image-studio": return <StudioWorkspace kind="image" capabilities={props.capabilities} />;
    case "music-studio": return <UnavailableStudioWorkspace title="Music studio" detail="Music generation has no configured backend worker in the current David AI deployment." icon={Headphones} />;
    case "artwork-studio": return <UnavailableStudioWorkspace title="Artwork studio" detail="Artwork composition is waiting for a verified backend capability and artifact contract." icon={Sparkles} />;
    case "enhance-studio": return <UnavailableStudioWorkspace title="Enhance media" detail="Media enhancement is not connected to a verified processing worker yet." icon={Wand2} />;
    case "edit-studio": return <UnavailableStudioWorkspace title="Edit studio" detail="Non-destructive media editing needs a verified asset-editing backend before controls are enabled." icon={ClipboardList} />;
    case "reshoot-studio": return <UnavailableStudioWorkspace title="Reshoot studio" detail="Reshoot planning needs an approved generation and asset-reference workflow before it can be activated." icon={RefreshCw} />;
    case "activity": return <ActivityWorkspace conversations={props.conversations} tasks={props.tasks} />;
    case "settings": return <SettingsWorkspace tone={props.tone} voice={props.voice} />;
    case "owner": return <OwnerWorkspace health={props.health} fabricReady={props.fabricReady} capabilities={props.capabilities} adapters={props.adapters} />;
    default: return <DashboardWorkspace {...props} />;
  }
}

function DashboardWorkspace({ health, voice, fabricReady, capabilities, adapters, providers, memories, projects, tasks, tone, notify, refresh, go }: WorkspaceProps) {
  const readyCount = capabilities.filter((item) => item.available || String(item.state).toLowerCase().includes("ready")).length;
  const providerCount = providers.length || capabilities.filter((item) => item.provider).length;
  return <div className="space-y-6"><div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]"><Card red className="relative overflow-hidden"><div className="absolute right-0 top-0 h-64 w-64 rounded-full bg-crimson/10 blur-3xl" /><div className="relative grid gap-6 md:grid-cols-[1fr_0.8fr] md:items-center"><div><p className="micro-label text-ember">David AI / command center</p><h2 className="mt-4 max-w-2xl text-4xl font-semibold leading-tight tracking-[-0.045em] text-white sm:text-5xl">Turn intent into <span className="text-ember">verified action.</span></h2><p className="mt-4 max-w-xl text-base leading-7 text-smoke">A human-guided intelligence workspace for chat, memory, orchestration, creative production, and accountable automation.</p><div className="mt-7 flex flex-wrap gap-3"><Button variant="primary" onClick={() => go("chat")}><Command className="h-4 w-4" />Open David chat</Button><Button onClick={() => go("agents")}><BrainCircuit className="h-4 w-4" />Run an agent</Button><Button onClick={() => go("website-builder")}><Globe2 className="h-4 w-4" />Build a website</Button><Button onClick={() => go("video-studio")}><Video className="h-4 w-4" />Plan a video</Button></div><div className="mt-6 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-smoke"><span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-signal" />{health ? "Backend connection live" : "Backend connection pending"}</span><span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-ember" />Tone: {tone}</span><span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-amber" />Approval gates active</span></div></div><CoreVisual phase={voice?.tts_configured ? "ready" : "idle"} /></div></Card><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1"><Card><SectionHeading eyebrow="System pulse" title="Live posture" detail="Read from the current backend and Fabric registry." action={<Button variant="ghost" className="px-2" onClick={() => void refresh()}><RefreshCw className="h-4 w-4" /></Button>} /><div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4"><Metric label="Capabilities" value={String(capabilities.length || "—")} detail={`${readyCount} ready or available`} icon={Layers3} tone="red" /><Metric label="Adapters" value={String(adapters.length || "—")} detail="External boundaries" icon={Network} tone="blue" /><Metric label="Projects" value={String(projects.length || "—")} detail="JSON-backed workspaces" icon={FolderKanban} tone="green" /><Metric label="Tasks" value={String(tasks.length || "—")} detail="Tracked work items" icon={ClipboardList} tone="amber" /></div></Card><Card><div className="flex items-start justify-between gap-3"><div><p className="micro-label">Voice lifecycle</p><h3 className="mt-1 font-semibold text-white">{voice?.tts_configured ? "Piper TTS ready" : "Voice not configured"}</h3><p className="mt-1 text-sm text-smoke">{voice?.stt_configured ? "Speech input is configured." : "Microphone capture is available; backend STT is not exposed."}</p></div><Headphones className={`h-5 w-5 ${voice?.tts_configured ? "text-signal" : "text-amber"}`} /></div><div className="mt-4 flex items-center justify-between rounded-xl border border-white/10 bg-black/20 px-3 py-2"><span className="text-xs text-smoke">Engine</span><span className="text-xs font-semibold text-white">{voice?.tts_engine || "NOT CONFIGURED"}</span></div></Card></div></div><div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]"><AgentCommandPanel capabilities={capabilities} notify={notify} /><Card><SectionHeading eyebrow="Memory signal" title="Recent context" detail="Live memory records from David's backend." action={<Button variant="ghost" onClick={() => go("memory")}>View all <ArrowRight className="h-4 w-4" /></Button>} />{memories.length ? <div className="space-y-3">{memories.slice(0, 4).map((memory, index) => <div key={memory.id || index} className="rounded-xl border border-white/8 bg-black/15 p-3"><div className="flex items-center justify-between gap-3"><span className="text-xs font-semibold uppercase tracking-wider text-ember">{memory.type || "memory"}</span><span className="text-[11px] text-smoke">{formatDate(memory.created_at)}</span></div><p className="mt-2 line-clamp-2 text-sm text-white/85">{memory.content}</p></div>)}</div> : <EmptyState icon={Database} title="No memory signal yet" detail="Chat with David or add a memory to begin building context." action={<Button onClick={() => go("chat")}>Start a conversation</Button>} />}</Card></div></div>;
}

function AgentCommandPanel({ capabilities, notify }: { capabilities: Capability[]; notify: WorkspaceProps["notify"] }) {
  const [objective, setObjective] = useState("");
  const [selectedCapability, setSelectedCapability] = useState("");
  const [route, setRoute] = useState<RouteResult | null>(null);
  const [plan, setPlan] = useState<GoalPlan | null>(null);
  const [runId, setRunId] = useState("");
  const [runDetails, setRunDetails] = useState<RunDetails | null>(null);
  const [working, setWorking] = useState(false);

  const run = async () => {
    if (!objective.trim()) return notify("info", "Add an objective before starting a run.");
    setWorking(true);
    try {
      const routed = await api.intelligence.route(objective, selectedCapability || undefined);
      setRoute(routed);
      const goal = await api.intelligence.createGoal(objective, { tone: "focused", source: "command-center" });
      const nextPlan = await api.intelligence.planGoal(goal.id);
      setPlan(nextPlan);
      const createdRun = await api.intelligence.createRun(goal.id, objective, routed.selected?.capability_id || selectedCapability || undefined);
      setRunId(createdRun.id);
      const result = await api.intelligence.executeRun(createdRun.id, { objective, requested_capability: routed.selected?.capability_id || selectedCapability || undefined, input: { source: "command-center" } });
      const details = await api.intelligence.runDetails(createdRun.id);
      setRunDetails(details);
      notify("success", String(result.status || "Agent run recorded."));
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Agent run failed");
    } finally {
      setWorking(false);
    }
  };

  return <Card red><SectionHeading eyebrow="Agent orchestration" title="Delegate a real objective" detail="David routes through the live capability registry and records the run envelope." action={<span className="micro-label">human approval aware</span>} /><div className="grid gap-3 md:grid-cols-[1fr_220px_auto]"><textarea value={objective} onChange={(event) => setObjective(event.target.value)} className="min-h-12 resize-none rounded-xl border border-white/10 bg-black/20 px-3 py-3 text-sm text-white outline-none placeholder:text-smoke focus:border-crimson/60" placeholder="Describe an objective for David to route and verify..." aria-label="Agent objective" /><select value={selectedCapability} onChange={(event) => setSelectedCapability(event.target.value)} className="rounded-xl border border-white/10 bg-black/20 px-3 py-3 text-sm text-smoke outline-none"><option value="">Auto route</option>{capabilities.slice(0, 28).map((item) => <option key={item.id} value={item.id}>{item.name || item.id}</option>)}</select><Button variant="primary" onClick={() => void run()} disabled={working}>{working ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}{working ? "Running" : "Start run"}</Button></div>{(route || plan || runId) && <div className="mt-5 grid gap-3 md:grid-cols-3"><div className="rounded-xl border border-white/10 bg-black/20 p-3"><p className="micro-label">Selected</p><p className="mt-2 text-sm font-semibold text-white">{route?.selected?.capability_id || "planning"}</p><p className="mt-1 text-xs text-smoke">{route?.selected?.state || "route recorded"}</p></div><div className="rounded-xl border border-white/10 bg-black/20 p-3"><p className="micro-label">Plan steps</p><p className="mt-2 text-sm font-semibold text-white">{plan?.steps?.length ?? "—"}</p><p className="mt-1 text-xs text-smoke">primary and fallback metadata</p></div><div className="rounded-xl border border-white/10 bg-black/20 p-3"><p className="micro-label">Run</p><p className="mt-2 truncate text-sm font-semibold text-white">{runId || "not created"}</p><p className={`mt-1 text-xs ${stateClass(runDetails?.run?.status)}`}>{runDetails?.run?.status || "recorded"}</p></div></div>}</Card>;
}

function ChatWorkspace({ voice, tone, conversations, notify }: { voice: VoiceStatus | null; tone: string; conversations: ConversationItem[]; notify: WorkspaceProps["notify"] }) {
  const [messages, setMessages] = useState<Message[]>([{ id: "intro", role: "assistant", content: "I’m David. Give me an objective, a question, or a creative direction. I’ll keep you informed when an action needs approval.", createdAt: new Date().toISOString() }]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [voicePhase, setVoicePhase] = useState<VoicePhase>("idle");
  const [conversationId, setConversationId] = useState<string | undefined>();
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const send = async (event?: FormEvent) => {
    event?.preventDefault();
    const message = draft.trim();
    if (!message || loading) return;
    setDraft("");
    setMessages((current) => [...current, { id: uid("user"), role: "user", content: message, createdAt: new Date().toISOString() }]);
    setLoading(true);
    setVoicePhase("thinking");
    try {
      const response: ChatResponse = await api.chat(message, conversationId);
      setConversationId(response.conversation_id || conversationId);
      setMessages((current) => [...current, { id: uid("assistant"), role: "assistant", content: response.reply, provider: response.provider, createdAt: new Date().toISOString() }]);
      setVoicePhase("idle");
    } catch (error) {
      setMessages((current) => [...current, { id: uid("system"), role: "system", content: error instanceof Error ? error.message : "David could not reach the backend.", createdAt: new Date().toISOString() }]);
      setVoicePhase("error");
      notify("error", "Chat request failed. Check backend health and retry.");
    } finally {
      setLoading(false);
    }
  };

  const toggleMic = async () => {
    if (voicePhase === "listening" && mediaRecorder.current) {
      mediaRecorder.current.stop();
      setVoicePhase("processing");
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setVoicePhase("error");
      return notify("error", "This browser does not expose microphone access.");
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorder.current = recorder;
      recorder.onstop = () => { stream.getTracks().forEach((track) => track.stop()); setVoicePhase("idle"); notify("info", voice?.stt_configured ? "Voice capture completed." : "Voice capture completed locally; the backend STT route is not exposed yet."); };
      recorder.start();
      setVoicePhase("listening");
    } catch {
      setVoicePhase("error");
      notify("error", "Microphone permission was not granted.");
    }
  };

  const speak = async (text: string) => {
    setVoicePhase("speaking");
    try {
      const result = await api.synthesize(text);
      if (result.audio_available && result.audio_base64) {
        const audio = new Audio(toAudioUrl(result.audio_base64, result.audio_format || "wav"));
        audioRef.current = audio;
        audio.onended = () => setVoicePhase("idle");
        await audio.play();
      } else {
        setVoicePhase("idle");
        notify("info", result.reason || "Voice output is not configured; the text response remains available.");
      }
    } catch (error) {
      setVoicePhase("error");
      notify("error", error instanceof Error ? error.message : "Voice synthesis failed.");
    }
  };

  return <div className="grid gap-6 xl:grid-cols-[1fr_320px]"><Card className="flex min-h-[680px] flex-col"><div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/10 pb-4"><div><p className="micro-label">Communication console</p><h2 className="mt-1 text-xl font-semibold text-white">Conversation channel</h2></div><div className="flex items-center gap-2"><span className="rounded-full border border-white/10 px-2.5 py-1 text-[10px] uppercase tracking-wider text-smoke">tone: {tone}</span><span className="rounded-full border border-signal/20 bg-signal/5 px-2.5 py-1 text-[10px] uppercase tracking-wider text-signal">{voicePhase}</span></div></div><div className="flex-1 space-y-4 overflow-y-auto py-5" aria-live="polite">{messages.map((message) => <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}><div className={`max-w-[88%] rounded-2xl border px-4 py-3 ${message.role === "user" ? "border-crimson/30 bg-crimson/10" : message.role === "system" ? "border-amber/30 bg-amber/5" : "border-white/10 bg-white/[0.035]"}`}><div className="mb-2 flex items-center justify-between gap-6"><span className={`text-[10px] font-bold uppercase tracking-[0.16em] ${message.role === "user" ? "text-ember" : message.role === "system" ? "text-amber" : "text-signal"}`}>{message.role === "user" ? "YOU" : message.role === "system" ? "SYSTEM" : "DAVID"}</span><span className="text-[10px] text-smoke">{formatDate(message.createdAt)}</span></div><p className="whitespace-pre-wrap text-sm leading-6 text-white/90">{message.content}</p>{message.provider && <p className="mt-3 text-[10px] uppercase tracking-wider text-smoke">provider: {message.provider}</p>}{message.role === "assistant" && <div className="mt-3 flex gap-2"><button className="rounded-lg p-1.5 text-smoke hover:bg-white/5 hover:text-white" onClick={() => void navigator.clipboard?.writeText(message.content)} aria-label="Copy assistant response"><FileText className="h-3.5 w-3.5" /></button><button className="rounded-lg p-1.5 text-smoke hover:bg-white/5 hover:text-white" onClick={() => void speak(message.content)} aria-label="Read assistant response aloud"><Headphones className="h-3.5 w-3.5" /></button></div>}</div></div>)}{loading && <div className="flex items-center gap-2 text-xs text-smoke"><Loader2 className="h-4 w-4 animate-spin text-ember" />David is thinking through the request...</div>}</div><form onSubmit={send} className="border-t border-white/10 pt-4"><div className="flex items-end gap-2 rounded-2xl border border-white/10 bg-black/25 p-2"><button type="button" className={`rounded-xl p-3 ${voicePhase === "listening" ? "bg-crimson/20 text-ember" : "text-smoke hover:bg-white/5 hover:text-white"}`} onClick={() => void toggleMic()} aria-label={voicePhase === "listening" ? "Stop recording" : "Start recording"}>{voicePhase === "listening" ? <Square className="h-4 w-4" /> : voicePhase === "error" ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}</button><textarea value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void send(); } }} className="max-h-36 min-h-12 flex-1 resize-none bg-transparent px-2 py-3 text-sm text-white outline-none placeholder:text-smoke" placeholder="Ask David to reason, plan, create, or explain..." aria-label="Message David" /><button type="submit" className="rounded-xl bg-crimson p-3 text-white shadow-glow transition hover:bg-ember disabled:opacity-50" disabled={!draft.trim() || loading} aria-label="Send message"><Send className="h-4 w-4" /></button></div><div className="mt-2 flex items-center justify-between px-2 text-[10px] uppercase tracking-wider text-smoke"><span>Enter to send · Shift + Enter for newline</span><span>{voice?.tts_configured ? "TTS ready" : "TTS not configured"}</span></div></form></Card><div className="space-y-6"><Card red><CoreVisual phase={voicePhase} small /><div className="mt-2 text-center"><p className="micro-label">Voice-aware state</p><p className="mt-2 text-sm font-semibold text-white">{voicePhase === "listening" ? "Listening for your direction" : voicePhase === "thinking" ? "Processing with David" : voicePhase === "speaking" ? "Speaking response" : voicePhase === "error" ? "Needs attention" : "Ready when you are"}</p><p className="mt-2 text-xs leading-5 text-smoke">The interface reflects real browser permission and backend voice availability.</p></div></Card><Card><SectionHeading eyebrow="Conversation history" title="Recent backend records" detail="The API currently returns conversation metadata only; selecting and replaying historical messages requires a dedicated backend detail endpoint." />{conversations.length ? <div className="mt-4 space-y-2">{conversations.slice(0, 6).map((conversation, index) => <div key={conversation.id || index} className="rounded-xl border border-white/10 bg-black/20 p-3"><p className="truncate text-sm font-semibold text-white">{conversation.title || conversation.id || "Conversation"}</p><p className="mt-1 text-[11px] text-smoke">{formatDate(conversation.updated_at || conversation.created_at)}</p></div>)}</div> : <p className="mt-4 text-sm text-smoke">No backend conversation records are available yet.</p>}</Card><Card><SectionHeading eyebrow="Channel notes" title="Response envelope" /><div className="space-y-3 text-sm text-smoke"><p className="flex items-start gap-2"><Check className="mt-0.5 h-4 w-4 shrink-0 text-signal" />Provider name is shown when returned by the backend.</p><p className="flex items-start gap-2"><Check className="mt-0.5 h-4 w-4 shrink-0 text-signal" />Errors remain visible and retryable.</p><p className="flex items-start gap-2"><Check className="mt-0.5 h-4 w-4 shrink-0 text-amber" />Audio is played only when synthesis returns an audio payload.</p></div></Card></div></div>;
}

function AgentWorkspace({ capabilities, notify }: { capabilities: Capability[]; notify: WorkspaceProps["notify"] }) {
  return <div className="space-y-6"><div className="grid gap-6 xl:grid-cols-[1fr_0.8fr]"><AgentCommandPanel capabilities={capabilities} notify={notify} /><Card><SectionHeading eyebrow="Capability map" title="What David can route" detail="Live records from the Intelligence Fabric." /><div className="max-h-[510px] space-y-2 overflow-y-auto">{capabilities.length ? capabilities.map((item) => <CapabilityRow key={item.id} item={item} />) : <EmptyState icon={BrainCircuit} title="Waiting for registry" detail="Connect the backend to load capability records." />}</div></Card></div><Card><SectionHeading eyebrow="Run lifecycle" title="Accountable execution" detail="Goals become plans, runs, attempts, artifacts, and verification records." /><div className="grid gap-3 md:grid-cols-4">{[["01", "Route", "Select a primary capability"], ["02", "Plan", "Expose fallback candidates"], ["03", "Execute", "Respect approvals and boundaries"], ["04", "Verify", "Return evidence or a clear limitation"]].map(([number, title, detail]) => <div key={number} className="rounded-xl border border-white/10 bg-black/20 p-4"><span className="text-xs font-bold text-ember">{number}</span><h3 className="mt-3 font-semibold text-white">{title}</h3><p className="mt-1 text-xs leading-5 text-smoke">{detail}</p></div>)}</div></Card></div>;
}

function MemoryWorkspace({ memories, notify, refresh }: { memories: MemoryItem[]; notify: WorkspaceProps["notify"]; refresh: WorkspaceProps["refresh"] }) {
  const [query, setQuery] = useState("");
  const [content, setContent] = useState("");
  const [results, setResults] = useState<MemoryItem[]>(memories);
  useEffect(() => setResults(memories), [memories]);
  const search = async (event: FormEvent) => { event.preventDefault(); if (!query.trim()) return setResults(memories); try { setResults(await api.searchMemories(query)); } catch (error) { notify("error", error instanceof Error ? error.message : "Memory search failed"); } };
  const add = async () => { if (!content.trim()) return; try { await api.addMemory({ content, source: "command-center", type: "long-term" }); setContent(""); await refresh(); notify("success", "Memory added to David’s context."); } catch (error) { notify("error", error instanceof Error ? error.message : "Memory write failed"); } };
  return <div className="space-y-6"><Card red><SectionHeading eyebrow="Context layer" title="Memory console" detail="Search, add, and review the records David can use for continuity." /><div className="grid gap-3 md:grid-cols-[1fr_auto]"><form onSubmit={search} className="flex items-center gap-2 rounded-xl border border-white/10 bg-black/20 px-3"><Search className="h-4 w-4 text-smoke" /><input value={query} onChange={(event) => setQuery(event.target.value)} className="w-full bg-transparent py-3 text-sm text-white outline-none placeholder:text-smoke" placeholder="Search memories..." aria-label="Search memories" /></form><Button onClick={() => void add()}><Plus className="h-4 w-4" />Add memory</Button></div><textarea value={content} onChange={(event) => setContent(event.target.value)} className="mt-3 min-h-20 w-full rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-white outline-none placeholder:text-smoke" placeholder="Write a memory for David to retain..." aria-label="New memory" /></Card><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{results.length ? results.map((item, index) => <Card key={item.id || index}><div className="flex items-center justify-between gap-3"><span className="rounded-full border border-crimson/30 bg-crimson/10 px-2 py-1 text-[10px] uppercase tracking-wider text-ember">{item.type || "memory"}</span><span className="text-[11px] text-smoke">{formatDate(item.created_at)}</span></div><p className="mt-4 text-sm leading-6 text-white/90">{item.content}</p><div className="mt-4 flex items-center justify-between text-xs text-smoke"><span>{item.source || "unknown source"}</span><span>importance {item.importance ?? "—"}</span></div></Card>) : <div className="md:col-span-2 xl:col-span-3"><EmptyState icon={Database} title="No matching memories" detail="Try a different search or add a new context record." /></div>}</div></div>;
}

function TasksWorkspace({ tasks, projects, notify, refresh }: { tasks: TaskItem[]; projects: ProjectItem[]; notify: WorkspaceProps["notify"]; refresh: WorkspaceProps["refresh"] }) {
  const [title, setTitle] = useState("");
  const add = async () => { if (!title.trim()) return; try { await api.createTask({ title, description: title, status: "pending", project_id: projects[0]?.id }); setTitle(""); await refresh(); notify("success", "Task created."); } catch (error) { notify("error", error instanceof Error ? error.message : "Task creation failed"); } };
  return <div className="space-y-6"><Card red><SectionHeading eyebrow="Execution queue" title="Tasks" detail="Tasks remain explicit, reviewable, and separate from autonomous claims." /><div className="flex gap-2"><input value={title} onChange={(event) => setTitle(event.target.value)} className="min-h-10 flex-1 rounded-xl border border-white/10 bg-black/20 px-3 text-sm text-white outline-none placeholder:text-smoke" placeholder="Add a task..." aria-label="New task" /><Button variant="primary" onClick={() => void add()}><Plus className="h-4 w-4" />Create task</Button></div></Card><div className="grid gap-3">{tasks.length ? tasks.map((task, index) => <div key={task.id || index} className="panel flex flex-wrap items-center justify-between gap-4 rounded-xl p-4"><div className="flex items-start gap-3"><span className={`mt-1 h-2.5 w-2.5 rounded-full ${stateClass(task.status).replace("text-", "bg-")}`} /><div><h3 className="font-semibold text-white">{task.title || task.description || "Untitled task"}</h3><p className="mt-1 text-xs text-smoke">{task.project_id ? `Project ${task.project_id}` : "Unassigned"} · {task.priority || "normal"}</p></div></div><StateDot state={task.status || "pending"} /></div>) : <EmptyState icon={ClipboardList} title="No tasks in the queue" detail="Create a task to make the next unit of work explicit." />}</div></div>;
}

function ProjectsWorkspace({ projects, notify, refresh }: { projects: ProjectItem[]; notify: WorkspaceProps["notify"]; refresh: WorkspaceProps["refresh"] }) {
  const [name, setName] = useState("");
  const add = async () => { if (!name.trim()) return; try { await api.createProject({ name, description: "Created from David AI Command Center" }); setName(""); await refresh(); notify("success", "Project created."); } catch (error) { notify("error", error instanceof Error ? error.message : "Project creation failed"); } };
  return <div className="space-y-6"><Card red><SectionHeading eyebrow="Creative workspace" title="Projects" detail="Organize work before it becomes a plan, task, or agent run." /><div className="flex gap-2"><input value={name} onChange={(event) => setName(event.target.value)} className="min-h-10 flex-1 rounded-xl border border-white/10 bg-black/20 px-3 text-sm text-white outline-none placeholder:text-smoke" placeholder="New project name..." aria-label="New project name" /><Button variant="primary" onClick={() => void add()}><Plus className="h-4 w-4" />Create project</Button></div></Card><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{projects.length ? projects.map((project, index) => <Card key={project.id || index}><div className="flex items-start justify-between"><div className="grid h-10 w-10 place-items-center rounded-xl bg-crimson/15 text-ember"><FolderKanban className="h-5 w-5" /></div><MoreHorizontal className="h-4 w-4 text-smoke" /></div><h3 className="mt-5 font-semibold text-white">{project.name}</h3><p className="mt-2 min-h-10 text-sm leading-5 text-smoke">{project.description || "No project description yet."}</p><div className="mt-5 flex items-center justify-between border-t border-white/10 pt-3 text-xs text-smoke"><span>{project.status || "active"}</span><span>{formatDate(project.updated_at || project.created_at)}</span></div></Card>) : <div className="md:col-span-2 xl:col-span-3"><EmptyState icon={FolderKanban} title="No projects yet" detail="Create a workspace for the next idea, system, or campaign." /></div>}</div></div>;
}

function ProvidersWorkspace({ providers, adapters, capabilities, fabricReady }: { providers: Array<Record<string, unknown>>; adapters: Adapter[]; capabilities: Capability[]; fabricReady: ReadinessResponse | null }) {
  const providerRows: Array<Record<string, unknown>> = providers.length ? providers : capabilities.filter((item) => item.provider).map((item) => ({ id: item.provider, state: item.state, readiness: item.readiness }));
  return <div className="space-y-6"><div className="grid gap-6 xl:grid-cols-[1fr_0.8fr]"><Card red><SectionHeading eyebrow="Model routing" title="Provider posture" detail="The frontend can observe provider readiness without exposing credentials." /><div className="space-y-3">{providerRows.length ? providerRows.map((provider, index) => <div key={String(provider.id || index)} className="flex items-center justify-between gap-3 rounded-xl border border-white/10 bg-black/20 p-4"><div><p className="font-semibold text-white">{String(provider.id || "provider")}</p><p className="mt-1 text-xs text-smoke">{String(provider.kind || "provider boundary")}</p></div><StateDot state={String(provider.state || "UNKNOWN")} /></div>) : <EmptyState icon={Network} title="No provider directory" detail="The backend has not returned provider records yet." />}</div></Card><Card><SectionHeading eyebrow="Readiness" title="System truth" detail="Unavailable dependencies are surfaced, not masked." /><div className="space-y-3"><StateRow label="Fabric" value={String(fabricReady?.status || "unknown")} /><StateRow label="Adapters" value={`${adapters.length} discovered`} /><StateRow label="Capability records" value={`${capabilities.length} loaded`} /><StateRow label="Credentials" value="Server-side only" /></div></Card></div><Card><SectionHeading eyebrow="Fallback posture" title="Provider switching" detail="The routing API returns fallback candidates when the primary capability is unavailable." /><div className="grid gap-3 sm:grid-cols-3"><StateRow label="Primary" value="Selected by objective" /><StateRow label="Fallback" value="Returned by Fabric" /><StateRow label="User control" value="Approval-aware" /></div></Card></div>;
}

function StateRow({ label, value }: { label: string; value: string }) { return <div className="flex items-center justify-between gap-4 rounded-xl border border-white/10 bg-black/20 px-3 py-3"><span className="text-xs text-smoke">{label}</span><span className="text-xs font-semibold text-white">{value}</span></div>; }

function DevicesWorkspace({ voice }: { voice: VoiceStatus | null }) {
  const [mic, setMic] = useState<"unknown" | "granted" | "denied">("unknown");
  const checkMic = async () => { try { const stream = await navigator.mediaDevices.getUserMedia({ audio: true }); stream.getTracks().forEach((track) => track.stop()); setMic("granted"); } catch { setMic("denied"); } };
  return <div className="space-y-6"><Card red><SectionHeading eyebrow="Edge permissions" title="Devices" detail="Only browser permissions that the platform legitimately exposes are shown." /><div className="grid gap-4 md:grid-cols-3"><PermissionCard icon={Mic} label="Microphone" value={mic === "granted" ? "Granted" : mic === "denied" ? "Denied" : "Not checked"} action={<Button onClick={() => void checkMic()}>Check permission</Button>} /><PermissionCard icon={Headphones} label="Voice backend" value={voice?.tts_configured ? "TTS configured" : "Not configured"} action={<span className="text-xs text-smoke">Read-only status</span>} /><PermissionCard icon={Monitor} label="Current browser" value={typeof navigator !== "undefined" ? navigator.platform : "Browser"} action={<span className="text-xs text-smoke">Session-local</span>} /></div></Card><Card><SectionHeading eyebrow="Future edge layer" title="Companion architecture" detail="Android and device control remain future integrations; unrestricted control is not presented as available." /><div className="rounded-xl border border-dashed border-white/10 p-5 text-sm leading-6 text-smoke">David can report legitimate browser permissions now. Companion-device actions require an authenticated companion service and explicit user approval before they can be enabled.</div></Card></div>;
}

function PermissionCard({ icon: Icon, label, value, action }: { icon: IconType; label: string; value: string; action: React.ReactNode }) { return <div className="rounded-xl border border-white/10 bg-black/20 p-4"><div className="flex items-center justify-between"><Icon className="h-5 w-5 text-ember" /><StateDot state={value} /></div><p className="mt-4 font-semibold text-white">{label}</p><p className="mt-1 text-sm text-smoke">{value}</p><div className="mt-4">{action}</div></div>; }

function VoiceWorkspace({ voice, notify }: { voice: VoiceStatus | null; notify: WorkspaceProps["notify"] }) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [text, setText] = useState("");
  const [phase, setPhase] = useState<"idle" | "generating" | "speaking" | "blocked" | "error">("idle");
  const [detail, setDetail] = useState("Enter text to request the configured backend voice.");

  const stop = () => {
    audioRef.current?.pause();
    if (audioRef.current) audioRef.current.currentTime = 0;
    setPhase("idle");
    setDetail("Playback stopped.");
  };

  const speak = async () => {
    if (!text.trim()) return;
    setPhase("generating");
    setDetail("Requesting audio from the configured voice backend…");
    try {
      const response = await api.synthesize(text);
      if (!response.audio_available || !response.audio_base64) {
        setPhase("blocked");
        setDetail(response.reason || response.text_fallback || "The backend did not return playable audio.");
        return;
      }
      const audio = new Audio(toAudioUrl(response.audio_base64, response.audio_format || "wav"));
      audioRef.current = audio;
      audio.onplay = () => { setPhase("speaking"); setDetail("Audio is playing from the configured backend voice."); };
      audio.onended = () => { setPhase("idle"); setDetail("Playback finished."); };
      audio.onerror = () => { setPhase("error"); setDetail("The returned audio could not be played by this browser."); };
      await audio.play();
    } catch (error) {
      setPhase("error");
      const message = error instanceof Error ? error.message : "Voice synthesis failed";
      setDetail(message);
      notify("error", message);
    }
  };

  useEffect(() => () => { audioRef.current?.pause(); }, []);

  return <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]"><Card red><SectionHeading eyebrow="Voice control" title="Voice workspace" detail="Uses the existing server-side voice endpoint. Browser speech synthesis is not substituted." /><div className="mt-5 space-y-4"><textarea value={text} onChange={(event) => setText(event.target.value)} className="min-h-40 w-full rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-white outline-none placeholder:text-smoke" placeholder="Text for David to say…" aria-label="Text for voice synthesis" /><div className="flex flex-wrap gap-2"><Button variant="primary" onClick={() => void speak()} disabled={phase === "generating" || !text.trim()}>{phase === "generating" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}{phase === "generating" ? "Generating" : "Request voice"}</Button><Button onClick={stop} disabled={phase !== "speaking" && phase !== "generating"}><Square className="h-4 w-4" />Stop</Button></div></div></Card><div className="space-y-6"><Card><SectionHeading eyebrow="Playback status" title={phase === "speaking" ? "Speaking" : phase === "generating" ? "Generating" : "Voice status"} detail={detail} /><div className="mt-5 grid gap-3 sm:grid-cols-2"><StateRow label="TTS backend" value={voice?.tts_configured ? (voice.tts_engine || "Configured") : "Not configured"} /><StateRow label="Speech input" value={voice?.stt_configured ? "Backend configured" : "Not exposed by backend"} /><StateRow label="Output state" value={phase.toUpperCase()} /><StateRow label="Fallback voice" value="Not substituted" /></div></Card><Card><SectionHeading eyebrow="Boundary" title="Truthful voice behavior" detail="Voice capture and transcription controls are shown only when the backend exposes them. This workspace never invents microphone transcription or a browser-default output voice." /></Card></div></div>;
}

function ContentWorkspace({ notify }: { notify: WorkspaceProps["notify"] }) {
  const [brief, setBrief] = useState("");
  const [working, setWorking] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const createPlan = async () => {
    if (!brief.trim()) return;
    setWorking(true);
    try {
      const response = await api.planCreate(brief);
      setResult(response);
      notify("success", "Content plan returned by the backend.");
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Content planning failed");
    } finally { setWorking(false); }
  };
  return <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]"><Card red><SectionHeading eyebrow="Content studio" title="Plan content" detail="Creates a real backend plan; it does not claim publication, delivery, or a completed campaign." /><textarea value={brief} onChange={(event) => setBrief(event.target.value)} className="mt-5 min-h-44 w-full rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-white outline-none placeholder:text-smoke" placeholder="Describe the content objective, audience, and constraints…" aria-label="Content objective" /><Button variant="primary" className="mt-3 w-full" onClick={() => void createPlan()} disabled={!brief.trim() || working}>{working ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}{working ? "Planning" : "Create content plan"}</Button></Card><Card><SectionHeading eyebrow="Plan result" title="Backend response" detail="Any external delivery remains approval- and adapter-gated." />{result ? <pre className="mt-5 max-h-[420px] overflow-auto rounded-xl border border-white/10 bg-black/30 p-4 text-xs leading-5 text-signal">{JSON.stringify(result, null, 2)}</pre> : <EmptyState icon={FileText} title="No content plan yet" detail="Submit a brief to inspect the actual planning response." />}</Card></div>;
}

function AutomationWorkspace({ capabilities, notify }: { capabilities: Capability[]; notify: WorkspaceProps["notify"] }) {
  const [workflows, setWorkflows] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(true);
  const load = async () => {
    setLoading(true);
    try {
      const response = await api.intelligence.workflows() as { workflows?: unknown[] };
      setWorkflows(safeArray<Record<string, unknown>>(response.workflows));
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Automation registry could not be loaded");
    } finally { setLoading(false); }
  };
  useEffect(() => { void load(); }, []);
  const automationCapabilities = capabilities.filter((item) => /automation|workflow|schedule/i.test(`${item.id} ${item.category || ""}`));
  return <div className="space-y-6"><Card red><SectionHeading eyebrow="Automation plane" title="Automation workspace" detail="Shows workflow records returned by the backend. No schedule, webhook, or external action can be created from the UI until the backend exposes that contract." action={<Button onClick={() => void load()} disabled={loading}>{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}Refresh</Button>} /><div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">{workflows.length ? workflows.map((workflow, index) => <div key={String(workflow.id || index)} className="rounded-xl border border-white/10 bg-black/20 p-4"><div className="flex items-start justify-between gap-3"><TerminalSquare className="h-5 w-5 text-ember" /><StateDot state={String(workflow.state || workflow.status || "registered")} /></div><h3 className="mt-4 font-semibold text-white">{String(workflow.name || workflow.id || "Workflow")}</h3><p className="mt-1 text-xs leading-5 text-smoke">{String(workflow.description || "Backend-registered workflow.")}</p></div>) : <EmptyState icon={TerminalSquare} title={loading ? "Loading workflows" : "No workflow records"} detail={loading ? "Reading the backend registry…" : "The backend has not registered an automation workflow for this account."} />}</div></Card><Card><SectionHeading eyebrow="Capability boundary" title="Automation readiness" detail="Registered capabilities remain visible even when they are not executable for this user." /><div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">{automationCapabilities.length ? automationCapabilities.map((item) => <CapabilityRow key={item.id} item={item} />) : <EmptyState icon={TerminalSquare} title="No automation capability registered" detail="No automation worker has been declared as ready by the backend." />}</div></Card></div>;
}

function ConnectorsWorkspace({ adapters }: { adapters: Adapter[] }) { return <div className="space-y-6"><Card red><SectionHeading eyebrow="Integration plane" title="Connectors" detail="Imported repositories become bounded capabilities; credentials and external activation stay server-side." /><div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">{adapters.length ? adapters.map((adapter) => <div key={adapter.id} className="rounded-xl border border-white/10 bg-black/20 p-4"><div className="flex items-start justify-between gap-3"><div className="grid h-9 w-9 place-items-center rounded-lg bg-white/[0.05] text-ember"><Cloud className="h-4 w-4" /></div><StateDot state={adapter.state || (adapter.available ? "available" : "unavailable")} /></div><h3 className="mt-4 font-semibold text-white">{adapter.name || adapter.id}</h3><p className="mt-1 text-xs text-smoke">{adapter.kind || "service adapter"}</p><p className="mt-3 text-xs leading-5 text-smoke">{adapter.reason || adapter.readiness?.join(" · ") || "Readiness is reported by the backend."}</p></div>) : <EmptyState icon={Cloud} title="No connectors loaded" detail="Connect David’s backend to view adapter boundaries." />}</div></Card></div>; }

function WebsiteBuilderWorkspace({ notify }: { notify: WorkspaceProps["notify"] }) { const [prompt, setPrompt] = useState(""); const [result, setResult] = useState<Record<string, unknown> | null>(null); const [working, setWorking] = useState(false); const generate = async () => { if (!prompt.trim()) return; setWorking(true); try { setResult(await api.websiteGenerate(prompt)); notify("success", "Website request accepted by the backend."); } catch (error) { notify("error", error instanceof Error ? error.message : "Website generation failed"); } finally { setWorking(false); } }; return <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]"><Card red><SectionHeading eyebrow="Creative studio" title="Website builder" detail="Send a real generation request and inspect the backend response." /><textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} className="min-h-44 w-full rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-white outline-none placeholder:text-smoke" placeholder="Describe the site you want David to plan..." /><Button variant="primary" className="mt-3 w-full" onClick={() => void generate()} disabled={working}>{working ? <Loader2 className="h-4 w-4 animate-spin" /> : <Wand2 className="h-4 w-4" />}{working ? "Submitting" : "Generate request"}</Button></Card><Card><SectionHeading eyebrow="Build envelope" title="Preview state" detail="No deployment is triggered from this interface." />{result ? <pre className="max-h-[420px] overflow-auto rounded-xl border border-white/10 bg-black/30 p-4 text-xs leading-5 text-signal">{JSON.stringify(result, null, 2)}</pre> : <EmptyState icon={Globe2} title="No build response yet" detail="Submit a prompt to see the actual website backend response here." />}</Card></div>; }

function StudioWorkspace({ kind, capabilities }: { kind: "video" | "image"; capabilities: Capability[] }) { const matches = capabilities.filter((item) => kind === "video" ? String(item.category || "").toLowerCase().includes("video") || item.id.includes("video") : String(item.category || "").toLowerCase().includes("image") || item.id.includes("image") || item.id.includes("comfy")); return <div className="space-y-6"><Card red><SectionHeading eyebrow={`${kind} studio`} title={kind === "video" ? "Video studio" : "Image studio"} detail="The workspace is connected to readiness metadata, not a simulated generation result." /><div className="grid gap-4 md:grid-cols-[1fr_0.8fr]"><div className="rounded-xl border border-white/10 bg-black/20 p-5"><div className="flex items-center gap-3"><div className="grid h-11 w-11 place-items-center rounded-xl bg-crimson/15 text-ember">{kind === "video" ? <Video className="h-5 w-5" /> : <ImageIcon className="h-5 w-5" />}</div><div><h3 className="font-semibold text-white">{kind === "video" ? "Video generation" : "Image generation"}</h3><p className="text-sm text-smoke">{matches.length ? `${matches.length} matching capability record(s)` : "No matching provider is currently registered."}</p></div></div><div className="mt-5 rounded-xl border border-dashed border-white/10 p-5 text-sm leading-6 text-smoke">{matches.length ? "A provider boundary is visible below. Activation requires the corresponding external worker, credentials, and approval policy." : "This workspace is ready for a worker connection. It does not fabricate an asset while the backend capability is unavailable."}</div></div><div className="space-y-3">{matches.length ? matches.map((item) => <CapabilityRow key={item.id} item={item} />) : <EmptyState icon={kind === "video" ? Video : ImageIcon} title="Provider not configured" detail="Use the Providers or Connectors workspace to inspect readiness." />}</div></div></Card></div>; }

function UnavailableStudioWorkspace({ title, detail, icon: Icon }: { title: string; detail: string; icon: LucideIcon }) { return <div className="grid gap-6 xl:grid-cols-[1fr_0.8fr]"><Card red><SectionHeading eyebrow="Creative Suite" title={title} detail="This workspace is part of the Command Center, but no backend worker is currently configured." /><div className="mt-5 rounded-2xl border border-dashed border-amber/30 bg-amber/5 p-6"><Icon className="h-7 w-7 text-amber" /><h3 className="mt-4 font-semibold text-white">Capability unavailable</h3><p className="mt-2 text-sm leading-6 text-smoke">{detail}</p></div></Card><Card><SectionHeading eyebrow="Activation boundary" title="What is required" detail="David AI only enables this workspace after its server-side contract is verified." /><div className="mt-5 space-y-3"><StateRow label="Backend worker" value="Not configured" /><StateRow label="Provider credentials" value="Server-side required" /><StateRow label="Artifact provenance" value="Required before output" /><StateRow label="External delivery" value="Approval required" /></div></Card></div>; }

function ActivityWorkspace({ conversations, tasks }: { conversations: ConversationItem[]; tasks: TaskItem[] }) { const entries = [...conversations.slice(0, 4).map((item) => ({ label: "conversation", detail: item.title || item.id || "Conversation", date: item.updated_at || item.created_at })), ...tasks.slice(0, 4).map((item) => ({ label: "task", detail: item.title || item.description || "Task", date: item.created_at }))]; return <div className="space-y-6"><Card red><SectionHeading eyebrow="Observability" title="Activity feed" detail="A lightweight view assembled from live conversation and task records." />{entries.length ? <div className="space-y-3">{entries.map((entry, index) => <div key={`${entry.label}-${index}`} className="flex items-start gap-3 rounded-xl border border-white/10 bg-black/20 p-4"><div className="mt-1 h-2 w-2 rounded-full bg-ember" /><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center justify-between gap-3"><span className="text-[10px] font-bold uppercase tracking-widest text-ember">{entry.label}</span><span className="text-[11px] text-smoke">{formatDate(entry.date)}</span></div><p className="mt-1 text-sm text-white">{entry.detail}</p></div></div>)}</div> : <EmptyState icon={Activity} title="No activity records" detail="Activity will appear as David receives conversations and tasks." />}</Card></div>; }

function SettingsWorkspace({ tone, voice }: { tone: string; voice: VoiceStatus | null }) { return <div className="grid gap-6 xl:grid-cols-2"><Card red><SectionHeading eyebrow="Personalization" title="Settings" detail="Client preferences are local UI state until a server settings endpoint is exposed." /><div className="space-y-3"><StateRow label="Default tone" value={tone} /><StateRow label="Language" value="AUTO" /><StateRow label="Theme" value="Red futuristic / dark" /><StateRow label="Voice engine" value={voice?.tts_engine || "Not configured"} /></div></Card><Card><SectionHeading eyebrow="Security" title="Guardrails" /><div className="space-y-3"><StateRow label="API keys" value="Server-side only" /><StateRow label="Approval gates" value="Active" /><StateRow label="Destructive actions" value="Fail closed" /><StateRow label="Reduced motion" value="Browser controlled" /></div></Card></div>; }

function OwnerWorkspace({ health, fabricReady, capabilities, adapters }: { health: BackendHealth | null; fabricReady: ReadinessResponse | null; capabilities: Capability[]; adapters: Adapter[] }) { return <div className="space-y-6"><Card red><SectionHeading eyebrow="Administrative plane" title="Owner console" detail="Operational visibility without exposing backend credentials." /><div className="grid gap-3 md:grid-cols-4"><Metric label="Backend" value={health ? "LIVE" : "WAIT"} detail="GET /api/health" icon={Wifi} tone="green" /><Metric label="Fabric" value={String(fabricReady?.status || "UNKNOWN").toUpperCase()} detail="Readiness aggregate" icon={Gauge} tone="red" /><Metric label="Capabilities" value={String(capabilities.length)} detail="Registry records" icon={Layers3} tone="blue" /><Metric label="Adapters" value={String(adapters.length)} detail="Service boundaries" icon={Network} tone="amber" /></div></Card><div className="grid gap-6 lg:grid-cols-2"><Card><SectionHeading eyebrow="Security" title="Approval posture" /><div className="space-y-3"><StateRow label="Publishing" value="Approval required" /><StateRow label="Deployment" value="Approval required" /><StateRow label="Purchases" value="Blocked by default" /><StateRow label="Credentials" value="Never shown in UI" /></div></Card><Card><SectionHeading eyebrow="System" title="Backend envelope" /><pre className="overflow-auto rounded-xl border border-white/10 bg-black/30 p-4 text-xs leading-5 text-smoke">{JSON.stringify(health || { status: "waiting" }, null, 2)}</pre></Card></div></div>; }

function AuthWorkspace({ onSuccess, notify }: { onSuccess: () => void; notify: WorkspaceProps["notify"] }) { const [mode, setMode] = useState<"login" | "register">("login"); const [name, setName] = useState(""); const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [working, setWorking] = useState(false); const submit = async (event: FormEvent) => { event.preventDefault(); setWorking(true); try { if (mode === "login") await api.login(email, password); else await api.register(name, email, password); notify("success", mode === "login" ? "Signed in." : "Registration submitted."); onSuccess(); } catch (error) { notify("error", error instanceof Error ? error.message : "Authentication failed"); } finally { setWorking(false); } }; return <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-ink p-5"><div className="shell-grid absolute inset-0" /><div className="relative z-10 grid w-full max-w-5xl gap-8 lg:grid-cols-[1fr_420px] lg:items-center"><div className="hidden lg:block"><p className="micro-label text-ember">David AI / secure access</p><h1 className="mt-5 max-w-xl text-6xl font-semibold leading-[0.95] tracking-[-0.06em] text-white">A calmer interface for <span className="text-ember">ambitious work.</span></h1><p className="mt-6 max-w-lg text-base leading-7 text-smoke">The command center keeps your context, agent runs, voice state, and operational boundaries visible in one place.</p><CoreVisual phase="idle" /></div><Card red><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-crimson/15 text-ember"><Fingerprint className="h-5 w-5" /></span><div><p className="font-semibold text-white">{mode === "login" ? "Welcome back" : "Create an access record"}</p><p className="text-xs text-smoke">Owner approval remains backend-controlled.</p></div></div><form onSubmit={submit} className="mt-7 space-y-4">{mode === "register" && <input required value={name} onChange={(event) => setName(event.target.value)} className="min-h-11 w-full rounded-xl border border-white/10 bg-black/20 px-3 text-sm text-white outline-none placeholder:text-smoke" placeholder="Full name" aria-label="Full name" />}<input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} className="min-h-11 w-full rounded-xl border border-white/10 bg-black/20 px-3 text-sm text-white outline-none placeholder:text-smoke" placeholder="Email" aria-label="Email" /><input required minLength={6} type="password" value={password} onChange={(event) => setPassword(event.target.value)} className="min-h-11 w-full rounded-xl border border-white/10 bg-black/20 px-3 text-sm text-white outline-none placeholder:text-smoke" placeholder="Password" aria-label="Password" /><Button type="submit" variant="primary" className="w-full" disabled={working}>{working ? <Loader2 className="h-4 w-4 animate-spin" /> : <LockKeyhole className="h-4 w-4" />}{working ? "Checking" : mode === "login" ? "Enter command center" : "Register"}</Button></form><button className="mt-5 w-full text-center text-xs text-smoke hover:text-white" onClick={() => setMode(mode === "login" ? "register" : "login")}>{mode === "login" ? "Need an account? Register" : "Already registered? Sign in"}</button></Card></div></div>; }

export default DavidApp;


function LibraryWorkspace({
  assets,
  generations,
  storageStatus,
  projects,
  notify,
  refresh,
}: {
  assets: AssetItem[];
  generations: GenerationItem[];
  storageStatus: SupabaseStatus | null;
  projects: ProjectItem[];
  notify: WorkspaceProps["notify"];
  refresh: WorkspaceProps["refresh"];
}) {
  const [filter, setFilter] = useState("all");
  const [uploading, setUploading] = useState(false);
  const [selectedProject, setSelectedProject] = useState("");
  const visibleAssets = useMemo(
    () => filter === "all" ? assets : assets.filter((asset) => asset.kind === filter),
    [assets, filter],
  );

  const upload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setUploading(true);
    const kind = file.type.startsWith("image/") ? "image" : file.type.startsWith("video/") ? "video" : file.type.startsWith("audio/") ? "audio" : file.type.includes("pdf") || file.type.includes("text") ? "document" : "other";
    try {
      await api.uploadFile(file, selectedProject || undefined, kind);
      await refresh();
      notify("success", storageStatus?.database_enabled ? "Asset uploaded to private Supabase Storage." : "Asset saved to the local fallback; apply the Supabase migration for persistence.");
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Asset upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const toggleFavorite = async (asset: AssetItem) => {
    try {
      await api.library.favorite(asset.id, !asset.favorite);
      await refresh();
    } catch (error) {
      notify("error", error instanceof Error ? error.message : "Favorite update failed.");
    }
  };

  return <div className="space-y-6">
    <Card red>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="micro-label">Persistent creative library</p>
          <h2 className="mt-1 text-xl font-semibold text-white">Assets, outputs, and history</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-smoke">David AI keeps project assets in a private bucket and records generation metadata in PostgreSQL. Signed previews are temporary and never expose the storage bucket publicly.</p>
        </div>
        <div className={`rounded-xl border px-3 py-2 text-right ${storageStatus?.database_enabled ? "border-signal/30 bg-signal/5" : "border-amber/30 bg-amber/5"}`}>
          <p className="text-[10px] uppercase tracking-[0.18em] text-smoke">Storage state</p>
          <p className={`mt-1 text-xs font-bold uppercase tracking-wider ${storageStatus?.database_enabled ? "text-signal" : "text-amber"}`}>{storageStatus?.database_enabled ? "private / persistent" : "migration required"}</p>
          <p className="mt-1 text-[10px] text-smoke">bucket: {storageStatus?.storage_bucket || "Davidai"}</p>
        </div>
      </div>
      <div className="mt-5 flex flex-wrap items-center gap-2">
        <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl bg-crimson px-4 py-2.5 text-sm font-semibold text-white shadow-glow transition hover:bg-ember has-[:disabled]:cursor-not-allowed has-[:disabled]:opacity-50">
          {uploading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
          {uploading ? "Uploading..." : "Upload asset"}
          <input type="file" className="sr-only" onChange={upload} disabled={uploading} />
        </label>
        <select value={selectedProject} onChange={(event) => setSelectedProject(event.target.value)} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2.5 text-xs text-smoke outline-none" aria-label="Assign uploaded asset to project">
          <option value="">No project assignment</option>
          {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
        </select>
        <div className="ml-auto flex flex-wrap gap-1 rounded-xl border border-white/10 bg-black/20 p-1">
          {["all", "image", "video", "audio", "document", "website", "other"].map((value) => <button key={value} onClick={() => setFilter(value)} className={`rounded-lg px-2.5 py-1.5 text-[10px] uppercase tracking-wider transition ${filter === value ? "bg-white/10 text-white" : "text-smoke hover:text-white"}`}>{value}</button>)}
        </div>
      </div>
    </Card>

    {visibleAssets.length ? <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{visibleAssets.map((asset) => <Card key={asset.id}>
      <div className="relative flex aspect-[16/10] items-center justify-center overflow-hidden rounded-xl border border-white/10 bg-black/30">
        {asset.signed_url && asset.kind === "image" ? <img src={asset.signed_url} alt={asset.filename} className="h-full w-full object-cover" /> : asset.signed_url && asset.kind === "video" ? <video src={asset.signed_url} controls className="h-full w-full object-cover" /> : asset.kind === "audio" && asset.signed_url ? <audio src={asset.signed_url} controls className="w-[90%]" /> : <div className="text-center"><Archive className="mx-auto h-9 w-9 text-ember" /><p className="mt-2 max-w-[180px] truncate text-xs text-smoke">{asset.filename}</p></div>}
        <button onClick={() => void toggleFavorite(asset)} className={`absolute right-2 top-2 rounded-lg border p-2 backdrop-blur ${asset.favorite ? "border-amber/40 bg-amber/15 text-amber" : "border-white/10 bg-black/40 text-smoke hover:text-white"}`} aria-label={asset.favorite ? "Remove from favorites" : "Add to favorites"}><span className="text-xs">{asset.favorite ? "★" : "☆"}</span></button>
      </div>
      <div className="mt-4 flex items-start justify-between gap-3"><div className="min-w-0"><h3 className="truncate text-sm font-semibold text-white">{asset.filename}</h3><p className="mt-1 text-[10px] uppercase tracking-wider text-smoke">{asset.kind || "other"} · {asset.content_type || "unknown type"}</p></div><span className="shrink-0 text-[10px] text-smoke">{asset.size_bytes ? `${Math.round(asset.size_bytes / 1024)} KB` : "—"}</span></div>
      {asset.project_id && <p className="mt-3 text-xs text-smoke">Project: {projects.find((project) => project.id === asset.project_id)?.name || asset.project_id}</p>}
    </Card>)}</div> : <EmptyState icon={Archive} title="No assets in the Library yet" detail={storageStatus?.database_enabled ? "Upload an image, audio file, video, or document to create the first private asset record." : "Apply the David AI migration and enable server-side persistence before using the remote Library."} />}

    <Card>
      <SectionHeading eyebrow="Generation ledger" title="Recent outputs" detail="Creative Suite and website-builder records are kept as inspectable history." />
      <div className="mt-4 space-y-2">{generations.length ? generations.slice(0, 8).map((generation) => <div key={generation.id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-black/20 px-4 py-3"><div className="flex items-center gap-3"><span className="grid h-8 w-8 place-items-center rounded-lg bg-crimson/15 text-ember">{generation.kind === "website" ? <Globe2 className="h-4 w-4" /> : generation.kind === "video" ? <Video className="h-4 w-4" /> : <Sparkles className="h-4 w-4" />}</span><div><p className="text-sm font-medium text-white">{generation.prompt || `${generation.kind || "other"} generation`}</p><p className="mt-1 text-[10px] uppercase tracking-wider text-smoke">{generation.provider || "unknown provider"} · {generation.status || "completed"}</p></div></div><span className="text-[10px] text-smoke">{formatDate(generation.created_at)}</span></div>) : <p className="rounded-xl border border-dashed border-white/10 px-4 py-6 text-center text-sm text-smoke">No generation records yet. Website-builder outputs and future creative jobs will appear here.</p>}</div>
    </Card>
  </div>;
}
