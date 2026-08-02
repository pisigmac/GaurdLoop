"use client";

import dynamic from "next/dynamic";
import { Activity } from "lucide-react";

const LiveMonitorContent = dynamic(
  () => import("@/components/live-monitor-content"),
  {
    ssr: false,
    loading: () => (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Live Monitor</h1>
          <p className="text-muted text-sm mt-1">Real-time SSE event stream across all AI agent tasks & webhooks.</p>
        </div>
        <div className="bg-card border border-border rounded-md p-12 text-center text-muted text-sm">
          <Activity className="w-6 h-6 mx-auto mb-2 text-muted animate-pulse" />
          Loading Live Monitor...
        </div>
      </div>
    ),
  }
);

export default function MonitorPage() {
  return <LiveMonitorContent />;
}
