"use client";
import { useEffect, useState } from "react";
import { connectSSE } from "@/lib/api";
import { Activity } from "lucide-react";

export default function MonitorPage() {
  const [events, setEvents] = useState<any[]>([]);
  const [status, setStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");

  useEffect(() => {
    const es = connectSSE(
      "default-org",
      (msg) => {
        setEvents((prev) => [msg, ...prev].slice(0, 50));
      },
      () => setStatus("connected"),
      () => setStatus("disconnected")
    );
    return () => es.close();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Live Monitor</h1>
        <p className="text-muted text-sm mt-1">Real-time SSE stream of agent events.</p>
      </div>
      <div className="bg-card border border-border rounded-md overflow-hidden">
        <div className="px-5 py-3 border-b border-border bg-muted/5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity
              className={`w-4 h-4 ${
                status === "connected"
                  ? "text-emerald-500 animate-pulse"
                  : status === "connecting"
                  ? "text-amber-500 animate-spin"
                  : "text-rose-500"
              }`}
            />
            <span className="text-xs font-medium">
              {status === "connected"
                ? "Live — Connected to event stream"
                : status === "connecting"
                ? "Connecting to event stream..."
                : "Disconnected — Reconnecting"}
            </span>
          </div>
          <span
            className={`px-2 py-0.5 text-[10px] uppercase font-semibold rounded-full ${
              status === "connected"
                ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                : status === "connecting"
                ? "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                : "bg-rose-500/10 text-rose-500 border border-rose-500/20"
            }`}
          >
            {status}
          </span>
        </div>
        <div className="divide-y divide-border max-h-[600px] overflow-auto">
          {events.length === 0 && (
            <div className="px-5 py-8 text-center text-muted text-sm">
              Waiting for real-time agent events...
            </div>
          )}
          {events.map((e, i) => (
            <div key={i} className="px-5 py-2.5 text-xs font-mono flex items-center justify-between text-muted hover:bg-muted/5 transition-colors">
              <span className="text-foreground/90">{typeof e === "string" ? e : JSON.stringify(e)}</span>
              <span className="text-[10px] text-muted-foreground ml-4">{new Date().toLocaleTimeString()}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
