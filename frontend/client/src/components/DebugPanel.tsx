import { useEffect, useMemo, useState } from "react";
import { Bug, Check, Clipboard, Download, Trash2, X } from "lucide-react";
import { clearDebugEntries, exportDebugText, getDebugEntries, subscribeDebug, type DebugEntry } from "@/lib/debugLogger";

export default function DebugPanel() {
  const enabled = typeof window !== "undefined" && new URLSearchParams(window.location.search).get("debug") === "1";
  const [open, setOpen] = useState(false);
  const [entries, setEntries] = useState<DebugEntry[]>(getDebugEntries());
  const [copied, setCopied] = useState(false);

  useEffect(() => subscribeDebug(setEntries), []);
  const errorCount = useMemo(() => entries.filter((entry) => entry.level === "error").length, [entries]);
  if (!enabled) return null;

  const copyLogs = async () => {
    await navigator.clipboard?.writeText(exportDebugText());
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  };

  const downloadLogs = () => {
    const blob = new Blob([exportDebugText()], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `zentrafit-debug-${new Date().toISOString().replace(/[:.]/g, "-")}.log`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return <>
    <button onClick={() => setOpen(!open)} aria-label="Abrir diagnóstico" className="fixed bottom-4 right-4 z-[100] inline-flex items-center gap-2 rounded-full border border-[#a2ff00]/60 bg-[#101110] px-4 py-3 text-xs font-black uppercase tracking-[.12em] text-[#a2ff00] shadow-2xl hover:bg-[#a2ff00] hover:text-black"><Bug size={16} /> Diagnóstico {errorCount > 0 && <span className="rounded-full bg-red-500 px-2 py-0.5 text-white">{errorCount}</span>}</button>
    {open && <aside className="fixed bottom-20 right-4 z-[99] flex h-[min(620px,calc(100vh-120px))] w-[min(520px,calc(100vw-32px))] flex-col overflow-hidden rounded-3xl border border-[#a2ff00]/40 bg-[#101110] text-white shadow-2xl"><header className="flex items-center justify-between border-b border-white/10 bg-black/30 px-4 py-3"><div><p className="text-[10px] font-black uppercase tracking-[.2em] text-[#a2ff00]">ZentraFit</p><h2 className="font-display text-lg font-black uppercase">Diagnóstico de conexión</h2></div><button onClick={() => setOpen(false)} className="rounded-full p-2 text-white/50 hover:bg-white/10 hover:text-white"><X size={18} /></button></header><div className="flex gap-2 border-b border-white/10 p-3"><button onClick={copyLogs} className="flex items-center gap-2 rounded-full bg-[#a2ff00] px-3 py-2 text-[10px] font-black uppercase tracking-[.1em] text-black">{copied ? <Check size={14} /> : <Clipboard size={14} />} {copied ? "Copiado" : "Copiar"}</button><button onClick={downloadLogs} className="flex items-center gap-2 rounded-full border border-white/15 px-3 py-2 text-[10px] font-black uppercase tracking-[.1em] text-white/70"><Download size={14} /> Descargar</button><button onClick={clearDebugEntries} className="ml-auto flex items-center gap-2 rounded-full border border-red-400/30 px-3 py-2 text-[10px] font-black uppercase tracking-[.1em] text-red-300"><Trash2 size={14} /> Limpiar</button></div><div className="flex-1 space-y-2 overflow-auto p-3">{entries.length === 0 && <p className="p-6 text-center text-sm text-white/40">Todavía no hay eventos.</p>}{entries.map((entry) => <article key={entry.id} className="rounded-xl border border-white/10 bg-white/[.04] p-3 font-mono text-[11px]"><div className="flex gap-2"><span className="text-white/35">{entry.time}</span><span className={entry.level === "error" ? "text-red-300" : entry.level === "warn" ? "text-amber-300" : entry.level === "success" ? "text-[#a2ff00]" : "text-sky-300"}>{entry.level.toUpperCase()}</span></div><p className="mt-1 break-words text-white/85">{entry.message}</p>{entry.details && <pre className="mt-1 max-h-28 overflow-auto whitespace-pre-wrap break-words text-white/45">{entry.details}</pre>}</article>)}</div><footer className="border-t border-white/10 px-4 py-3 text-[10px] leading-4 text-white/40">Comparte el contenido con soporte. El panel no muestra contraseñas ni la clave secreta de Django.</footer></aside>}
  </>;
}
