export type DebugLevel = "info" | "success" | "warn" | "error";

export type DebugEntry = {
  id: number;
  time: string;
  level: DebugLevel;
  message: string;
  details?: string;
};

const MAX_ENTRIES = 250;
let sequence = 0;
let entries: DebugEntry[] = [];
const listeners = new Set<(entries: DebugEntry[]) => void>();

function stringify(value: unknown) {
  if (value instanceof Error) return `${value.name}: ${value.message}`;
  if (typeof value === "string") return value;
  try { return JSON.stringify(value); } catch { return String(value); }
}

export function debugLog(level: DebugLevel, message: string, details?: unknown) {
  const entry: DebugEntry = {
    id: ++sequence,
    time: new Date().toLocaleTimeString(),
    level,
    message,
    details: details === undefined ? undefined : stringify(details),
  };
  entries = [...entries, entry].slice(-MAX_ENTRIES);
  listeners.forEach((listener) => listener(entries));

  const payload = details === undefined ? message : [message, details];
  if (level === "error") console.error("[ZentraFit]", ...([payload].flat()));
  else if (level === "warn") console.warn("[ZentraFit]", ...([payload].flat()));
  else console.info("[ZentraFit]", ...([payload].flat()));
}

export function getDebugEntries() { return entries; }
export function subscribeDebug(listener: (entries: DebugEntry[]) => void) {
  listeners.add(listener);
  return () => { listeners.delete(listener); };
}
export function clearDebugEntries() { entries = []; listeners.forEach((listener) => listener(entries)); }

let installed = false;
export function installGlobalDebugHandlers() {
  if (installed || typeof window === "undefined") return;
  installed = true;
  window.addEventListener("error", (event) => debugLog("error", "Error no controlado en la interfaz", { message: event.message, file: event.filename, line: event.lineno, column: event.colno }));
  window.addEventListener("unhandledrejection", (event) => debugLog("error", "Promesa rechazada sin controlar", event.reason));
  debugLog("info", "Diagnóstico frontend iniciado", { url: window.location.href, userAgent: navigator.userAgent });
}

export function exportDebugText() {
  return entries.map((entry) => `[${entry.time}] ${entry.level.toUpperCase()} ${entry.message}${entry.details ? ` | ${entry.details}` : ""}`).join("\n");
}
