"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ScoreBadge } from "@/components/score-badge";
import { StatusBadge } from "@/components/status-badge";
import { DecisionBadge } from "@/components/decision-badge";
import {
  ShieldCheck,
  Users,
  Bot,
  Activity,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  TrendingUp,
  Key,
  CreditCard,
} from "lucide-react";

export default function AdminPage() {
  const [stats, setStats] = useState({
    totalOrgs: 1,
    totalUsers: 1,
    totalAgents: 0,
    totalTasks: 0,
    runningTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    blockedTasks: 0,
    avgScore: 0,
    apiKeys: 0,
    activeSubs: 0,
    revenue: 0,
  });
  const [recentTasks, setRecentTasks] = useState<any[]>([]);
  const [recentScores, setRecentScores] = useState<any[]>([]);
  const [agents, setAgents] = useState<any[]>([]);
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const [tasks, scores, agentsList] = await Promise.all([
        api.tasks.list(),
        api.scores.list(),
        api.agents.list(),
      ]);

      // Try to fetch API keys
      let keys: any[] = [];
      try {
        const resp = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api-keys`, {
          headers: { "Content-Type": "application/json" },
        });
        if (resp.ok) keys = await resp.json();
      } catch {}

      setRecentTasks(tasks.slice(0, 10));
      setRecentScores(scores.slice(0, 10));
      setAgents(agentsList);
      setApiKeys(keys);

      setStats({
        totalOrgs: 1,
        totalUsers: 1,
        totalAgents: agentsList.length,
        totalTasks: tasks.length,
        runningTasks: tasks.filter((t: any) => t.status === "running").length,
        completedTasks: tasks.filter((t: any) => t.status === "completed").length,
        failedTasks: tasks.filter((t: any) => t.status === "failed").length,
        blockedTasks: tasks.filter((t: any) => t.status === "blocked").length,
        avgScore: scores.length > 0
          ? Math.round(scores.reduce((a: number, b: any) => a + b.overall, 0) / scores.length)
          : 0,
        apiKeys: keys.length,
        activeSubs: 0,
        revenue: 0,
      });
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, []);

  const statCards = [
    { label: "Organizations", value: stats.totalOrgs, icon: ShieldCheck },
    { label: "Users", value: stats.totalUsers, icon: Users },
    { label: "Agents", value: stats.totalAgents, icon: Bot },
    { label: "Tasks", value: stats.totalTasks, icon: Activity },
    { label: "Running", value: stats.runningTasks, icon: Clock, color: "text-primary" },
    { label: "Completed", value: stats.completedTasks, icon: CheckCircle2, color: "text-accent" },
    { label: "Failed", value: stats.failedTasks, icon: XCircle, color: "text-danger" },
    { label: "Blocked", value: stats.blockedTasks, icon: AlertTriangle, color: "text-danger" },
    { label: "Avg Score", value: stats.avgScore, icon: TrendingUp, color: stats.avgScore >= 90 ? "text-accent" : stats.avgScore >= 70 ? "text-warning" : "text-danger" },
    { label: "API Keys", value: stats.apiKeys, icon: Key },
    { label: "Active Subs", value: stats.activeSubs, icon: CreditCard },
    { label: "Revenue", value: `$${stats.revenue}`, icon: CreditCard },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Admin</h1>
        <p className="text-muted text-sm mt-1">
          System overview, API keys, subscriptions, and operational metrics.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        {statCards.map((s) => (
          <div key={s.label} className="bg-card border border-border rounded-md p-4">
            <div className="flex items-center gap-2 text-muted mb-2">
              <s.icon className="w-4 h-4" />
              <span className="text-xs font-medium">{s.label}</span>
            </div>
            <div className={`text-2xl font-bold ${s.color || "text-foreground"}`}>
              {s.value}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-md">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <h2 className="text-sm font-semibold">Recent tasks</h2>
            <span className="text-xs text-muted">Last 10</span>
          </div>
          <div className="divide-y divide-border">
            {recentTasks.length === 0 && (
              <div className="px-5 py-8 text-center text-muted text-sm">No tasks yet.</div>
            )}
            {recentTasks.map((t) => (
              <div key={t.id} className="px-5 py-3 flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">{t.name}</div>
                  <div className="text-xs text-muted mt-0.5">
                    {t.agent_id ? `Agent ${t.agent_id.slice(0, 8)}` : "No agent"} · Loop {t.current_loop}/{t.max_loops}
                  </div>
                </div>
                <StatusBadge status={t.status} />
              </div>
            ))}
          </div>
        </div>

        <div className="bg-card border border-border rounded-md">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <h2 className="text-sm font-semibold">Latest scores</h2>
            <span className="text-xs text-muted">Last 10</span>
          </div>
          <div className="divide-y divide-border">
            {recentScores.length === 0 && (
              <div className="px-5 py-8 text-center text-muted text-sm">No scores yet.</div>
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-md">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <h2 className="text-sm font-semibold">Agents</h2>
            <span className="text-xs text-muted">{agents.length} total</span>
          </div>
          <div className="divide-y divide-border">
            {agents.length === 0 && (
              <div className="px-5 py-8 text-center text-muted text-sm">No agents connected.</div>
            )}
            {agents.map((a) => (
              <div key={a.id} className="px-5 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded bg-primary/10 flex items-center justify-center">
                    <Bot className="w-3.5 h-3.5 text-primary" />
                  </div>
                  <div>
                    <div className="text-sm font-medium">{a.name}</div>
                    <div className="text-xs text-muted">{a.agent_type}</div>
                  </div>
                </div>
                <span className={`text-xs font-medium ${a.status === "idle" ? "text-accent" : a.status === "running" ? "text-primary" : "text-danger"}`}>
                  {a.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-card border border-border rounded-md">
          <div className="px-5 py-4 border-b border-border flex items-center justify-between">
            <h2 className="text-sm font-semibold">API Keys</h2>
            <span className="text-xs text-muted">{apiKeys.length} total</span>
          </div>
          <div className="divide-y divide-border">
            {apiKeys.length === 0 && (
              <div className="px-5 py-8 text-center text-muted text-sm">No API keys created.</div>
            )}
            {apiKeys.map((k) => (
              <div key={k.id} className="px-5 py-3 flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium">{k.name}</div>
                  <div className="text-xs text-muted mt-0.5">
                    {k.key_prefix}**** · {k.scopes} · {k.revoked ? "Revoked" : "Active"}
                  </div>
                </div>
                <span className={`text-xs font-medium ${k.revoked ? "text-danger" : "text-accent"}`}>
                  {k.revoked ? "Revoked" : "Active"}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-card border border-border rounded-md p-5">
        <h2 className="text-sm font-semibold mb-4">System Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center gap-3 p-3 bg-muted/5 rounded-md">
            <div className="w-2 h-2 rounded-full bg-accent" />
            <div>
              <div className="text-sm font-medium">API</div>
              <div className="text-xs text-muted">Operational</div>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-muted/5 rounded-md">
            <div className="w-2 h-2 rounded-full bg-accent" />
            <div>
              <div className="text-sm font-medium">Database</div>
              <div className="text-xs text-muted">Connected</div>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-muted/5 rounded-md">
            <div className="w-2 h-2 rounded-full bg-accent" />
            <div>
              <div className="text-sm font-medium">Redis</div>
              <div className="text-xs text-muted">Connected</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
