"use client";

import { useEffect, useState } from "react";
import { connectSSE } from "@/lib/api";
import {
  Activity,
  ShieldCheck,
  Zap,
  Bot,
  Play,
  RefreshCw,
  Terminal,
  ChevronDown,
  ChevronRight,
  Copy,
  Check,
  Maximize2,
  X,
} from "lucide-react";

interface SSEEvent {
  type: string;
  org_id?: string;
  payload?: any;
  timestamp?: string;
  data?: any;
}

export default function LiveMonitorContent() {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [status, setStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [modalData, setModalData] = useState<{ title: string; data: any } | null>(null);

  // Restore cached events from sessionStorage on client mount
  useEffect(() => {
    try {
      const cached = sessionStorage.getItem("guardloop_live_events");
      if (cached) {
        setEvents(JSON.parse(cached));
      }
    } catch {}
  }, []);

  // Connect SSE event stream
  useEffect(() => {
    const es = connectSSE(
      "default-org",
      (msg) => {
        let parsed: any = msg;
        if (typeof msg === "string") {
          try {
            parsed = JSON.parse(msg);
          } catch {
            parsed = { type: "info", payload: msg };
          }
        }
        if (parsed.payload && typeof parsed.payload === "string") {
          try {
            parsed.payload = JSON.parse(parsed.payload);
          } catch {}
        }
        const eventType = parsed.type || parsed.payload?.type || "event";

        // Ignore network handshake connection events from polluting the log list
        if (eventType === "connected") {
          setStatus("connected");
          return;
        }

        const evt: SSEEvent = {
          type: eventType,
          payload: parsed.payload || parsed.data || parsed,
          timestamp: new Date().toLocaleTimeString(),
        };

        setEvents((prev) => {
          const updated = [evt, ...prev].slice(0, 100);
          try {
            sessionStorage.setItem("guardloop_live_events", JSON.stringify(updated));
          } catch {}
          return updated;
        });
      },
      () => setStatus("connected"),
      () => setStatus("disconnected")
    );
    return () => es.close();
  }, []);

  const extractEventData = (evt: SSEEvent) => {
    let data = evt.payload || evt.data || {};
    if (typeof data === "string") {
      try {
        data = JSON.parse(data);
      } catch {}
    }

    // Un-nest double wrapped payload objects from Redis PubSub broadcast_event
    if (data && typeof data === "object" && data.payload) {
      let inner = data.payload;
      if (typeof inner === "string") {
        try {
          inner = JSON.parse(inner);
        } catch {}
      }
      return {
        event_type: data.type || evt.type,
        ...inner,
      };
    }
    return data;
  };

  const renderEventBadge = (evt: SSEEvent) => {
    const data = extractEventData(evt);
    let rawType = data.event_type || evt.type || "event";

    switch (rawType) {
      case "task_created":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold bg-blue-500/10 text-blue-500 border border-blue-500/20 rounded shrink-0">
            <Zap className="w-3 h-3" /> TASK CREATED
          </span>
        );
      case "task_started":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded shrink-0">
            <Play className="w-3 h-3" /> TASK STARTED
          </span>
        );
      case "loop_checked":
        return (
          <span
            className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold rounded shrink-0 ${
              data.should_halt
                ? "bg-rose-500/10 text-rose-500 border border-rose-500/20"
                : "bg-purple-500/10 text-purple-500 border border-purple-500/20"
            }`}
          >
            <RefreshCw className={`w-3 h-3 ${data.should_halt ? "" : "animate-spin"}`} /> LOOP CHECK
          </span>
        );
      case "score_calculated":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold bg-amber-500/10 text-amber-500 border border-amber-500/20 rounded shrink-0">
            <ShieldCheck className="w-3 h-3" /> SCORE CALCULATED
          </span>
        );
      case "webhook_ingested":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold bg-cyan-500/10 text-cyan-500 border border-cyan-500/20 rounded shrink-0">
            <Terminal className="w-3 h-3" /> WEBHOOK INGESTED
          </span>
        );
      case "connected":
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded shrink-0">
            <Activity className="w-3 h-3" /> STREAM CONNECTED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold bg-muted text-muted-foreground border border-border rounded shrink-0">
            <Activity className="w-3 h-3" /> {rawType.toUpperCase()}
          </span>
        );
    }
  };

  const getAgentName = (evt: SSEEvent) => {
    const data = extractEventData(evt);
    if (data.agent_name) return data.agent_name;
    if (data.source) return `Webhook (${data.source.toUpperCase()})`;
    return "System Agent";
  };

  const formatPayload = (evt: SSEEvent) => {
    const data = extractEventData(evt);

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

  const handleCopyPayload = (i: number, data: any) => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopiedIndex(i);
    setTimeout(() => setCopiedIndex(null), 2000);
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
        <div className="divide-y divide-border max-h-[680px] overflow-auto">
          {events.length === 0 && (
            <div className="px-5 py-12 text-center text-muted text-sm">
              <Activity className="w-6 h-6 mx-auto mb-2 text-muted animate-pulse" />
              Waiting for real-time agent activity & webhooks...
            </div>
          )}
          {events.map((e, i) => {
            const data = extractEventData(e);
            const isExpanded = expandedIndex === i;
            return (
              <div key={i} className="divide-y divide-border/50 hover:bg-muted/5 transition-colors">
                <div
                  onClick={() => setExpandedIndex(isExpanded ? null : i)}
                  className="px-5 py-3 text-xs flex items-start justify-between cursor-pointer gap-4"
                >
                  <div className="flex items-start gap-3 overflow-hidden flex-1">
                    <button className="mt-0.5 text-muted-foreground hover:text-foreground">
                      {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                    </button>
                    {renderEventBadge(e)}
                    <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-indigo-300 bg-indigo-500/15 border border-indigo-500/30 px-2.5 py-0.5 rounded shrink-0">
                      <Bot className="w-3.5 h-3.5 text-indigo-400" />
                      {getAgentName(e)}
                    </span>
                    <span className="font-mono text-foreground/90 break-words leading-relaxed">
                      {formatPayload(e)}
                    </span>
                  </div>
                  <span className="text-[10px] text-muted-foreground font-mono whitespace-nowrap shrink-0 mt-0.5">
                    {e.timestamp || new Date().toLocaleTimeString()}
                  </span>
                </div>

                {/* Collapsible Full JSON Payload Drawer */}
                {isExpanded && (
                  <div className="px-5 py-3 bg-muted/10 border-t border-border space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-semibold text-muted uppercase tracking-wider">
                        Full Payload JSON ({e.type || "event"})
                      </span>
                      <div className="flex items-center gap-3">
                        <button
                          onClick={(evt) => {
                            evt.stopPropagation();
                            setModalData({
                              title: `${(e.type || "event").toUpperCase()} — ${getAgentName(e)}`,
                              data,
                            });
                          }}
                          className="flex items-center gap-1 text-[11px] font-medium text-muted-foreground hover:text-foreground transition-colors"
                        >
                          <Maximize2 className="w-3 h-3" /> Full Screen
                        </button>
                        <button
                          onClick={(evt) => {
                            evt.stopPropagation();
                            handleCopyPayload(i, data);
                          }}
                          className="flex items-center gap-1 text-[11px] font-medium text-primary hover:underline"
                        >
                          {copiedIndex === i ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-500" /> Copied JSON
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" /> Copy JSON
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                    <pre className="p-3.5 bg-muted/40 rounded border border-border text-[11px] font-mono text-foreground/90 overflow-x-auto whitespace-pre-wrap break-all leading-relaxed max-h-[600px]">
                      {JSON.stringify(data, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Full-Screen JSON Payload Inspector Modal */}
      {modalData && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 md:p-8">
          <div className="bg-card border border-border rounded-lg w-full max-w-5xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-border flex items-center justify-between bg-muted/10">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-primary" />
                <h3 className="text-sm font-semibold tracking-tight">{modalData.title}</h3>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(JSON.stringify(modalData.data, null, 2));
                    setCopiedIndex(9999);
                    setTimeout(() => setCopiedIndex(null), 2000);
                  }}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary text-xs font-medium rounded-md hover:bg-primary/20 transition-colors"
                >
                  {copiedIndex === 9999 ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-500" /> Copied Payload
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" /> Copy JSON
                    </>
                  )}
                </button>
                <button
                  onClick={() => setModalData(null)}
                  className="p-1 text-muted hover:text-foreground transition-colors rounded-md hover:bg-muted"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            <div className="p-6 flex-1 overflow-auto bg-muted/20">
              <pre className="p-4 bg-background rounded-md border border-border text-xs font-mono text-foreground leading-relaxed whitespace-pre-wrap break-all overflow-x-auto select-all">
                {JSON.stringify(modalData.data, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
