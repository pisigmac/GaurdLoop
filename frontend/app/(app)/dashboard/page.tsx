"use client";

import { useEffect, useState } from "react";
import { api, connectSSE } from "@/lib/api";
import { ScoreBadge } from "@/components/score-badge";
import { StatusBadge } from "@/components/status-badge";
import { DecisionBadge } from "@/components/decision-badge";
import { TaskGraphViz } from "@/components/task-graph-viz";
import {
  Activity,
  Bot,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  TrendingUp,
  ShieldCheck,
} from "lucide-react";

export default function DashboardPage() {
  const [stats, setStats] = useState({
    total: 0,
    running: 0,
    completed: 0,
    failed: 0,
    blocked: 0,
    avgScore: 0,
  });
  const [recentTasks, setRecentTasks] = useState<any[]>([]);
  const [recentScores, setRecentScores] = useState<any[]>([]);
  const [graphData, setGraphData] = useState<any>({ nodes: [], edges: [], critical_path: [] });

  useEffect(() => {
    api.tasks.list({ status: "running" }).then((r) => {
      setStats((s) => ({ ...s, running: r.length }));
    });
    api.tasks.list().then((r) => {
      setStats((s) => ({
        ...s,
        total: r.length,
        completed: r.filter((t: any) => t.status === "completed").length,
        failed: r.filter((t: any) => t.status === "failed").length,
        blocked: r.filter((t: any) => t.status === "blocked").length,
      }));
      setRecentTasks(r.slice(0, 5));
      if (r.length > 0) {
        api.tasks.graph(r[0].id).then(setGraphData);
      }
    });
    api.scores.list().then((r) => {
      setRecentScores(r.slice(0, 5));
      if (r.length > 0) {
        const avg = Math.round(r.reduce((a: number, b: any) => a + b.overall, 0) / r.length);
        setStats((s) => ({ ...s, avgScore: avg }));
      }
    });

    const es = connectSSE("default-org", (msg) => {
      if (msg.type === "task_update") {
        api.tasks.list().then((r) => {
          setRecentTasks(r.slice(0, 5));
        });
      }
    });

    return () => es.close();
  }, []);

  const statCards = [
    { label: "Total tasks", value: stats.total, icon: Activity, color: "text-primary" },
    { label: "Running", value: stats.running, icon: Clock, color: "text-primary" },
    { label: "Completed", value: stats.completed, icon: CheckCircle2, color: "text-accent" },
    { label: "Failed", value: stats.failed, icon: XCircle, color: "text-danger" },
    { label: "Blocked", value: stats.blocked, icon: AlertTriangle, color: "text-danger" },
    { label: "Avg score", value: stats.avgScore, icon: TrendingUp, color: "text-accent" },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-muted text-sm mt-1">
          Real-time view of your agent fleet, scores, and trust signals.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {statCards.map((s) => (
          <div
            key={s.label}
            className="bg-card border border-border rounded-md p-4"
          >
            <div className="flex items-center gap-2 text-muted mb-2">
              <s.icon className="w-4 h-4" />
              <span className="text-xs font-medium">{s.label}</span>
            </div>
            <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Tasks */}
        <div className="bg-card border border-border rounded-md">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <h2 className="text-sm font-semibold">Recent tasks</h2>
            <span className="text-xs text-muted">Last 5</span>
          </div>
          <div className="divide-y divide-border">
            {recentTasks.length === 0 && (
              <div className="px-5 py-8 text-center text-muted text-sm">
                No tasks yet. Create one to get started.
              </div>
            )}
            {recentTasks.map((t) => (
              <div key={t.id} className="px-5 py-3 flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">{t.name}</div>
                  <div className="text-xs text-muted mt-0.5">
                    Loop {t.current_loop}/{t.max_loops} · {t.context_size_tokens} tokens
                  </div>
                </div>
                <StatusBadge status={t.status} />
              </div>
            ))}
          </div>
        </div>

        {/* Recent Scores */}
        <div className="bg-card border border-border rounded-md">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <h2 className="text-sm font-semibold">Latest scores</h2>
            <ShieldCheck className="w-4 h-4 text-muted" />
          </div>
          <div className="divide-y divide-border">
            {recentScores.length === 0 && (
              <div className="px-5 py-8 text-center text-muted text-sm">
                No scores calculated yet.
              </div>
            )}
            {recentScores.map((s) => (
              <div key={s.id} className="px-5 py-3 flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">Task {s.task_id.slice(0, 8)}</div>
                  <div className="text-xs text-muted mt-0.5">
                    Test {s.test_score} · Coverage {s.coverage_score} · Security {s.security_score}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <ScoreBadge score={s.overall} />
                  <DecisionBadge decision={s.decision} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Dependency Graph */}
      <div className="bg-card border border-border rounded-md">
        <div className="px-5 py-4 border-b border-border">
          <h2 className="text-sm font-semibold">Dependency graph</h2>
          <p className="text-xs text-muted mt-0.5">
            Red edges show the critical path. Blue edges are standard dependencies.
          </p>
        </div>
        <div className="p-5">
          <TaskGraphViz
            nodes={graphData.nodes || []}
            edges={graphData.edges || []}
            criticalPath={graphData.critical_path || []}
          />
        </div>
      </div>
    </div>
  );
}
