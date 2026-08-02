"use client";
import { useEffect, useState } from "react";
import { connectSSE } from "@/lib/api";
import { Activity, ShieldCheck, Zap, AlertTriangle, Play, RefreshCw, Terminal } from "lucide-react";

interface SSEEvent {
  type: string;
  org_id?: string;
  payload?: any;
  timestamp?: string;
  data?: any;
}

export default function MonitorPage() {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [status, setStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");

  useEffect(() => {
    const es = connectSSE(
      "default-org",
      (msg) => {
        const evt: SSEEvent = typeof msg === "string" ? { type: "info", payload: msg } : msg;
        evt.timestamp = new Date().toLocaleTimeString();
        setEvents((prev) => [evt, ...prev].slice(0, 100));
      },
      () => setStatus("connected"),
      () => setStatus("disconnected")
    );
    return () => es.close();
  }, []);

  const renderEventBadge = (evt: SSEEvent) => {
    let rawType = evt.type || "event";
    if (evt.payload && evt.payload.type) rawType = evt.payload.type;
    const data = evt.payload || evt.data || {};

    switch (rawType) {
      case "task_created":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold bg-blue-500/10 text-blue-500 border border-blue-500/20 rounded">
            <Zap className="w-3 h-3" /> TASK CREATED
          </span>
        );
      case "task_started":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded">
            <Play className="w-3 h-3" /> TASK STARTED
          </span>
        );
      case "loop_checked":
        return (
          <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold rounded ${
            data.should_halt
              ? "bg-rose-500/10 text-rose-500 border border-rose-500/20"
              : "bg-purple-500/10 text-purple-500 border border-purple-500/20"
          }`}>
            <RefreshCw className={`w-3 h-3 ${data.should_halt ? "" : "animate-spin"}`} /> LOOP CHECK
          </span>
        );
      case "score_calculated":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold bg-amber-500/10 text-amber-500 border border-amber-500/20 rounded">
            <ShieldCheck className="w-3 h-3" /> SCORE CALCULATED
          </span>
        );
      case "webhook_ingested":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold bg-cyan-500/10 text-cyan-500 border border-cyan-500/20 rounded">
            <Terminal className="w-3 h-3" /> WEBHOOK INGESTED
          </span>
        );
      case "connected":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded">
            <Activity className="w-3 h-3" /> STREAM CONNECTED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold bg-muted text-muted-foreground border border-border rounded">
            <Activity className="w-3 h-3" /> {rawType.toUpperCase()}
          </span>
        );
    }
  };

  const formatPayload = (evt: SSEEvent) => {
    const data = evt.payload || evt.data || {};
    if (typeof data === "string") return data;

    if (data.name || data.task_id) {
      const taskTitle = data.name ? `"${data.name}"` : `Task ${data.task_id?.slice(0, 8)}`;
      if (data.iteration !== undefined) {
        return `${taskTitle} → Loop ${data.iteration} (${data.tokens || 0} tokens)`;
      }
      if (data.overall !== undefined) {
        return `${taskTitle} → Score: ${data.overall} [${data.decision?.toUpperCase()}]`;
      }
      return `${taskTitle} (${data.status || "active"})`;
    }

    if (data.source) {
      return `Source: ${data.source.toUpperCase()} · Event: ${data.event_type || "webhook"}`;
    }

    return JSON.stringify(data);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Live Monitor</h1>
        <p className="text-muted text-sm mt-1">Real-time SSE event stream across all AI agent tasks & webhooks.</p>
      </div>

      <div className="bg-card border border-border rounded-md overflow-hidden">
        {/* Header */}
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
                ? "Live — Connected to Agent Event Stream"
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

        {/* Event List */}
        <div className="divide-y divide-border max-h-[620px] overflow-auto">
          {events.length === 0 && (
            <div className="px-5 py-12 text-center text-muted text-sm">
              <Activity className="w-6 h-6 mx-auto mb-2 text-muted animate-pulse" />
              Waiting for real-time agent activity & webhooks...
            </div>
          )}
          {events.map((e, i) => (
            <div
              key={i}
              className="px-5 py-3 text-xs flex items-center justify-between hover:bg-muted/5 transition-colors gap-4"
            >
              <div className="flex items-center gap-3 overflow-hidden">
                {renderEventBadge(e)}
                <span className="font-mono text-foreground/90 truncate">{formatPayload(e)}</span>
              </div>
              <span className="text-[10px] text-muted-foreground font-mono whitespace-nowrap">
                {e.timestamp || new Date().toLocaleTimeString()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
