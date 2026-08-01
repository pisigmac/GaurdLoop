"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { ScoreBadge } from "@/components/score-badge";
import { Plus, Play, RefreshCw, AlertCircle, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function TasksPage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState("");

  const load = async () => {
    setLoading(true);
    const r = await api.tasks.list();
    setTasks(r);
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = tasks.filter((t) =>
    filter ? t.status === filter : true
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Tasks</h1>
          <p className="text-muted text-sm mt-1">
            View and manage agent tasks across your organization.
          </p>
        </div>
        <button
          onClick={load}
          className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium border border-border rounded-md hover:bg-muted/5 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2">
        {["all", "pending", "running", "completed", "failed", "blocked"].map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s === "all" ? "" : s)}
            className={`px-3 py-1.5 text-xs font-medium rounded-md border transition-colors ${
              filter === s || (s === "all" && !filter)
                ? "bg-foreground text-background border-foreground"
                : "bg-card text-muted border-border hover:text-foreground"
            }`}
          >
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-card border border-border rounded-md overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/5">
              <th className="text-left px-5 py-3 font-medium text-muted">Name</th>
              <th className="text-left px-5 py-3 font-medium text-muted">Agent</th>
              <th className="text-left px-5 py-3 font-medium text-muted">Status</th>
              <th className="text-left px-5 py-3 font-medium text-muted">Loop</th>
              <th className="text-left px-5 py-3 font-medium text-muted">Priority</th>
              <th className="text-left px-5 py-3 font-medium text-muted">Created</th>
              <th className="text-right px-5 py-3 font-medium text-muted">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {filtered.length === 0 && (
              <tr>
                <td colSpan={7} className="px-5 py-8 text-center text-muted">
                  {loading ? "Loading..." : "No tasks match this filter."}
                </td>
              </tr>
            )}
            {filtered.map((t) => (
              <tr key={t.id} className="hover:bg-muted/5 transition-colors">
                <td className="px-5 py-3">
                  <Link href={`/tasks/${t.id}`} className="font-medium hover:text-primary transition-colors">{t.name}</Link>
                  <div className="text-xs text-muted mt-0.5">
                    {t.id.slice(0, 8)}
                  </div>
                </td>
                <td className="px-5 py-3 text-muted">{t.agent_id?.slice(0, 8) || "—"}</td>
                <td className="px-5 py-3"><StatusBadge status={t.status} /></td>
                <td className="px-5 py-3 text-muted">
                  {t.current_loop}/{t.max_loops}
                </td>
                <td className="px-5 py-3 text-muted">{t.priority}</td>
                <td className="px-5 py-3 text-muted text-xs">
                  {new Date(t.created_at).toLocaleDateString()}
                </td>
                <td className="px-5 py-3 text-right">
                  <div className="flex items-center justify-end gap-2">
                    {t.status === "pending" && (
                      <button
                        onClick={() => api.tasks.start(t.id).then(load)}
                        className="p-1.5 rounded hover:bg-primary/10 text-primary transition-colors"
                        title="Start task"
                      >
                        <Play className="w-4 h-4" />
                      </button>
                    )}
                    <button
                      onClick={() => api.tasks.score(t.id).then(load)}
                      className="p-1.5 rounded hover:bg-accent/10 text-accent transition-colors"
                      title="Calculate score"
                    >
                      <RefreshCw className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
