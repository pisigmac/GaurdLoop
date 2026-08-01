"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Bot, Plus, Trash2, Edit3 } from "lucide-react";

const AGENT_TYPES = ["cursor", "claude_code", "github_copilot", "custom"];

export default function AgentsPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", agent_type: "cursor", config: "" });

  const load = async () => {
    const r = await api.agents.list();
    setAgents(r);
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    let config = {};
    try {
      config = JSON.parse(form.config || "{}");
    } catch {}
    await api.agents.create({
      name: form.name,
      agent_type: form.agent_type,
      config,
    });
    setShowForm(false);
    setForm({ name: "", agent_type: "cursor", config: "" });
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Agents</h1>
          <p className="text-muted text-sm mt-1">
            Connect Cursor, Claude Code, GitHub Copilot, or custom agents.
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-foreground text-background text-sm font-medium rounded-md hover:bg-foreground/90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add agent
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="bg-card border border-border rounded-md p-5 space-y-4"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-muted mb-1.5">Name</label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary/20"
                placeholder="Production Cursor Agent"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-muted mb-1.5">Type</label>
              <select
                value={form.agent_type}
                onChange={(e) => setForm({ ...form, agent_type: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                {AGENT_TYPES.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-muted mb-1.5">Config (JSON)</label>
              <input
                value={form.config}
                onChange={(e) => setForm({ ...form, config: e.target.value })}
                className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary/20"
                placeholder='{"api_key": "..."}'
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="submit"
              className="px-4 py-2 bg-foreground text-background text-sm font-medium rounded-md hover:bg-foreground/90 transition-colors"
            >
              Save agent
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-4 py-2 text-sm font-medium border border-border rounded-md hover:bg-muted/5 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((a) => (
          <div
            key={a.id}
            className="bg-card border border-border rounded-md p-5 hover:border-primary/30 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-md bg-primary/10 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
                <div>
                  <div className="font-medium text-sm">{a.name}</div>
                  <div className="text-xs text-muted">{a.agent_type}</div>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => api.agents.delete(a.id).then(load)}
                  className="p-1.5 rounded hover:bg-danger/10 text-danger transition-colors"
                  title="Delete"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
            <div className="mt-4 space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted">Status</span>
                <span className={`font-medium ${
                  a.status === "idle" ? "text-accent" : a.status === "running" ? "text-primary" : "text-danger"
                }`}>
                  {a.status}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted">Last seen</span>
                <span className="text-muted">
                  {a.last_seen ? new Date(a.last_seen).toLocaleDateString() : "Never"}
                </span>
              </div>
            </div>
          </div>
        ))}
        {agents.length === 0 && (
          <div className="col-span-full text-center py-12 text-muted text-sm border border-dashed border-border rounded-md">
            No agents connected yet. Add your first agent to start orchestrating.
          </div>
        )}
      </div>
    </div>
  );
}
