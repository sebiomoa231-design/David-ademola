export type Tone = "calm" | "focused" | "analytical" | "creative" | "direct";

export type VoicePhase = "idle" | "listening" | "thinking" | "processing" | "speaking" | "muted" | "error";

export type HealthStatus = "healthy" | "degraded" | "offline" | "unknown";

export interface BackendHealth {
  status?: string;
  service?: string;
  version?: string;
  [key: string]: unknown;
}

export interface VoiceStatus {
  stt_configured?: boolean;
  tts_configured?: boolean;
  tts_engine?: string | null;
  tts_voice?: string | null;
  supported_languages?: string[];
  default_language_mode?: string;
}

export interface ChatResponse {
  reply: string;
  provider?: string;
  conversation_id?: string;
}

export interface MemoryItem {
  id?: string;
  type?: string;
  content: string;
  confidence?: number;
  importance?: number;
  source?: string;
  tags?: string[];
  created_at?: string;
}

export interface ProjectItem {
  id?: string;
  name: string;
  description?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
}

export interface TaskItem {
  id?: string;
  title?: string;
  description?: string;
  status?: string;
  priority?: string;
  project_id?: string;
  created_at?: string;
}

export interface ConversationItem {
  id?: string;
  title?: string;
  messages?: Array<{ role: string; content: string; created_at?: string }>;
  created_at?: string;
  updated_at?: string;
}

export interface Capability {
  id: string;
  name?: string;
  category?: string;
  description?: string;
  state?: string;
  readiness?: string[];
  available?: boolean;
  reason?: string;
  agent?: string;
  skill?: string;
  tool?: string;
  provider?: string;
  adapter?: string;
  mode?: string;
  keywords?: string[];
  fallback_capabilities?: string[];
}

export interface Adapter {
  id: string;
  name?: string;
  kind?: string;
  state?: string;
  readiness?: string[];
  available?: boolean;
  reason?: string;
  endpoint?: string | null;
}

export interface ReadinessResponse {
  status?: string;
  capabilities?: Capability[];
  adapters?: Adapter[];
  [key: string]: unknown;
}

export interface RouteResult {
  objective: string;
  candidates: Array<Capability & { capability_id?: string; score?: number }>;
  selected?: (Capability & { capability_id?: string; score?: number }) | null;
  fallback_chain?: string[];
}

export interface Goal {
  id: string;
  objective: string;
  context?: Record<string, unknown>;
  created_at?: string;
}

export interface PlanStep {
  capability?: string;
  agent?: string;
  skill?: string;
  tool?: string;
  provider?: string;
  state?: string;
  [key: string]: unknown;
}

export interface GoalPlan {
  goal_id?: string;
  steps?: PlanStep[];
  [key: string]: unknown;
}

export interface Run {
  id: string;
  goal_id?: string;
  objective?: string;
  requested_capability?: string | null;
  status?: string;
  approved?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface RunDetails {
  run?: Run;
  events?: Array<{ type?: string; event_type?: string; message?: string; created_at?: string; [key: string]: unknown }>;
  attempts?: Array<{ capability?: string; status?: string; error?: string; [key: string]: unknown }>;
  artifacts?: Array<{ id?: string; name?: string; type?: string; status?: string; [key: string]: unknown }>;
  verification?: { status?: string; message?: string; [key: string]: unknown } | null;
}

export interface ProviderDirectoryItem {
  id: string;
  capabilities?: string[];
  state?: string;
  readiness?: string[];
}

export interface SettingsResponse {
  [key: string]: unknown;
}


export type AssetKind = "image" | "video" | "audio" | "document" | "website" | "other";

export interface AssetItem {
  id: string;
  owner_id?: string;
  project_id?: string | null;
  filename: string;
  storage_path: string;
  content_type?: string;
  size_bytes?: number;
  kind?: AssetKind;
  metadata?: Record<string, unknown>;
  favorite?: boolean;
  signed_url?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface GenerationItem {
  id: string;
  project_id?: string | null;
  asset_id?: string | null;
  kind?: AssetKind;
  prompt?: string;
  provider?: string;
  status?: string;
  output?: string;
  metadata?: Record<string, unknown>;
  created_at?: string;
}

export interface SupabaseStatus {
  configured: boolean;
  database_enabled: boolean;
  storage_bucket: string;
  migration_required?: boolean;
}
