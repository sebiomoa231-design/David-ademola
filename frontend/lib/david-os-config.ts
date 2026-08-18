export type DavidPreferenceKey =
  | "approvalGates"
  | "longTermMemory"
  | "backgroundMonitoring"
  | "voiceActivation"
  | "quietMode"
  | "reducedMotion"
  | "highContrast";

export type DavidSettings = Record<DavidPreferenceKey, boolean>;

export const defaultDavidSettings: DavidSettings = {
  approvalGates: true,
  longTermMemory: true,
  backgroundMonitoring: false,
  voiceActivation: false,
  quietMode: false,
  reducedMotion: false,
  highContrast: false,
};

export const DAVID_SETTINGS_STORAGE_KEY = "david-ai.settings.v1";

export function readDavidSettings(): DavidSettings {
  if (typeof window === "undefined") return defaultDavidSettings;
  try {
    const raw = window.localStorage.getItem(DAVID_SETTINGS_STORAGE_KEY);
    if (!raw) return defaultDavidSettings;
    const parsed = JSON.parse(raw) as Partial<DavidSettings>;
    return { ...defaultDavidSettings, ...parsed };
  } catch {
    return defaultDavidSettings;
  }
}

export function writeDavidSettings(settings: DavidSettings): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(DAVID_SETTINGS_STORAGE_KEY, JSON.stringify(settings));
}

export type DavidOSState = "idle" | "listening" | "thinking" | "speaking" | "error";

export const davidStateCopy: Record<DavidOSState, { label: string; detail: string; action: string }> = {
  idle: { label: "IDLE / STANDBY", detail: "System is calm and waiting.", action: "NO ACTIVE TASK" },
  listening: { label: "LISTENING", detail: "Microphone active. Listening to user.", action: "VOICE INPUT" },
  thinking: { label: "PROCESSING / THINKING", detail: "Analyzing request and preparing response.", action: "ANALYZING REQUEST" },
  speaking: { label: "RESPONSE READY", detail: "Answer or result is ready.", action: "RESPONDING" },
  error: { label: "SYSTEM ALERT", detail: "Voice service needs attention.", action: "CHECK CONNECTION" },
};
