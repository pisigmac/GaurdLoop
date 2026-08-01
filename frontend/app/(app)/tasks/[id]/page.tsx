"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { StatusBadge } from "@/components/status-badge";
import { ScoreBadge } from "@/components/score-badge";
import { DecisionBadge } from "@/components/decision-badge";
import { TaskGraphViz } from "@/components/task-graph-viz";
import {
  ArrowLeft,
  Play,
  RefreshCw,
  AlertCircle,
  Clock,
  Bot,
  Layers,
  FileText,
  Activity,
} from "lucide-react";
import Link from "next/link";

export default function TaskDetailPage() {
  const params = useParams();
  const taskId = params.id as string;
  const [task, setTask] = useState<any>(null);
  const [scores, setScores] = useState<any[]>([]);
  const [piiScans, setPiiScans] = useState<any[]>([]);
  const [browserVerifies, setBrowserVerifies] = useState<any[]>([]);
  const [graphData, setGraphData] = useState<any>({ nodes: [], edges: [], critical_path: [] });
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const t = await api.tasks.get(taskId);
      setTask(t);

      const s = await api.scores.list({ task_id: taskId });
      setScores(s);

      const p = await api.pii.scans(taskId);
      setPiiScans(p);

      const b = await api.browser.list(taskId);
      setBrowserVerifies(b);

      const g = await api.tasks.graph(taskId);
      setGraphData(g);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, [taskId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Activity className="w-5 h-5 text-primary animate-spin" />
      </div>
    );
  }

  if (!task) {
    return (
      <div className="text-center py-16">
        <AlertCircle className="w-8 h-8 text-danger mx-auto mb-3" />
        <p className="text-muted text-sm">Task not found.</p>
        <Link href="/tasks" className="text-primary text-sm mt-2 inline-block hover:underline">
          Back to tasks
        </Link>
      </div>
    );
  }

  const latestScore = scores[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link href="/tasks" className="inline-flex items-center gap-1 text-xs text-muted hover:text-foreground mb-2 transition-colors">
            <ArrowLeft className="w-3 h-3" /> All tasks
          </Link>
          <h1 className="text-2xl font-semibold tracking-tight">{task.name}</h1>
          <div className="flex items-center gap-3 mt-2">
            <StatusBadge status={task.status} />
            <span className="text-xs text-muted">ID: {task.id}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {task.status === "pending" && (
            <button
              onClick={() => api.tasks.start(task.id).then(load)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-foreground text-background text-xs font-medium rounded-md hover:bg-foreground/90 transition-colors"
            >
              <Play className="w-3.5 h-3.5" /> Start
            </button>
          )}
          <button
            onClick={() => api.tasks.score(task.id).then(load)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 border border-border text-xs font-medium rounded-md hover:bg-muted/5 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Score
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column — Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Overview */}
          <div className="bg-card border border-border rounded-md p-5">
            <h2 className="text-sm font-semibold mb-4">Overview</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-xs text-muted mb-1">Status</div>
                <StatusBadge status={task.status} />
              </div>
              <div>
                <div className="text-xs text-muted mb-1">Priority</div>
                <div className="text-sm font-medium">{task.priority}/10</div>
              </div>
              <div>
                <div className="text-xs text-muted mb-1">Loop</div>
                <div className="text-sm font-medium">{task.current_loop}/{task.max_loops}</div>
              </div>
              <div>
                <div className="text-xs text-muted mb-1">Context</div>
                <div className="text-sm font-medium">{task.context_size_tokens} tokens</div>
              </div>
            </div>
            {task.description && (
              <div className="mt-4 pt-4 border-t border-border">
                <div className="text-xs text-muted mb-1">Description</div>
                <p className="text-sm">{task.description}</p>
              </div>
            )}
            {task.error_log && (
              <div className="mt-4 pt-4 border-t border-border">
                <div className="text-xs text-danger mb-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> Error
                </div>
                <p className="text-sm text-danger">{task.error_log}</p>
              </div>
            )}
          </div>

          {/* Output */}
          {task.output && Object.keys(task.output).length > 0 && (
            <div className="bg-card border border-border rounded-md p-5">
              <h2 className="text-sm font-semibold mb-3">Output</h2>
              <pre className="text-xs bg-muted/5 p-3 rounded-md overflow-auto max-h-64">
                {JSON.stringify(task.output, null, 2)}
              </pre>
            </div>
          )}

          {/* Dependency Graph */}
          <div className="bg-card border border-border rounded-md p-5">
            <h2 className="text-sm font-semibold mb-3">Dependency Graph</h2>
            <TaskGraphViz
              nodes={graphData.nodes || []}
              edges={graphData.edges || []}
              criticalPath={graphData.critical_path || []}
            />
          </div>

          {/* Scores */}
          <div className="bg-card border border-border rounded-md">
            <div className="px-5 py-4 border-b border-border flex items-center justify-between">
              <h2 className="text-sm font-semibold">Score History</h2>
              <span className="text-xs text-muted">{scores.length} scores</span>
            </div>
            <div className="divide-y divide-border">
              {scores.length === 0 && (
                <div className="px-5 py-8 text-center text-muted text-sm">
                  No scores calculated yet.
                </div>
              )}
              {scores.map((s) => (
                <div key={s.id} className="px-5 py-3 flex items-center justify-between">
                  <div>
                    <div className="text-xs text-muted">{new Date(s.created_at).toLocaleString()}</div>
                    <div className="flex items-center gap-3 mt-1 text-xs">
                      <span>Test {s.test_score}</span>
                      <span>Coverage {s.coverage_score}</span>
                      <span>Security {s.security_score}</span>
                      <span>Behavior {s.behavioral_score}</span>
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

          {/* PII Scans */}
          <div className="bg-card border border-border rounded-md">
            <div className="px-5 py-4 border-b border-border flex items-center justify-between">
              <h2 className="text-sm font-semibold">PII Scans</h2>
              <span className="text-xs text-muted">{piiScans.length} scans</span>
            </div>
            <div className="divide-y divide-border">
              {piiScans.length === 0 && (
                <div className="px-5 py-8 text-center text-muted text-sm">
                  No PII scans yet.
                </div>
              )}
              {piiScans.map((p) => (
                <div key={p.id} className="px-5 py-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted">{new Date(p.created_at).toLocaleString()}</span>
                    <span className={`text-xs font-medium ${p.blocked ? "text-danger" : "text-accent"}`}>
                      {p.blocked ? "Blocked" : "Clean"}
                    </span>
                  </div>
                  <div className="text-xs text-muted mt-1">
                    {p.findings.length} PII findings · {p.secrets_found.length} secrets
                  </div>
                  {p.block_reason && (
                    <p className="text-xs text-danger mt-1">{p.block_reason}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Browser Verifications */}
          <div className="bg-card border border-border rounded-md">
            <div className="px-5 py-4 border-b border-border flex items-center justify-between">
              <h2 className="text-sm font-semibold">Browser Verifications</h2>
              <span className="text-xs text-muted">{browserVerifies.length} runs</span>
            </div>
            <div className="divide-y divide-border">
              {browserVerifies.length === 0 && (
                <div className="px-5 py-8 text-center text-muted text-sm">
                  No browser verifications yet.
                </div>
              )}
              {browserVerifies.map((b) => (
                <div key={b.id} className="px-5 py-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted">{b.url}</span>
                    <span className={`text-xs font-medium ${b.passed ? "text-accent" : "text-danger"}`}>
                      {b.passed ? "Passed" : "Failed"}
                    </span>
                  </div>
                  <div className="text-xs text-muted mt-1">
                    {b.a11y_violations.length} a11y issues · {b.viewport.width}x{b.viewport.height}
                  </div>
                  {b.failure_reason && (
                    <p className="text-xs text-danger mt-1">{b.failure_reason}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right column — Timeline + Meta */}
        <div className="space-y-6">
          {/* Meta */}
          <div className="bg-card border border-border rounded-md p-5">
            <h2 className="text-sm font-semibold mb-4">Metadata</h2>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted text-xs">Agent</span>
                <span className="font-medium text-xs">{task.agent_id ? task.agent_id.slice(0, 8) : "—"}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted text-xs">Organization</span>
                <span className="font-medium text-xs">{task.org_id.slice(0, 8)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted text-xs">Created</span>
                <span className="text-xs">{task.created_at ? new Date(task.created_at).toLocaleString() : "—"}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted text-xs">Started</span>
                <span className="text-xs">{task.started_at ? new Date(task.started_at).toLocaleString() : "—"}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted text-xs">Completed</span>
                <span className="text-xs">{task.completed_at ? new Date(task.completed_at).toLocaleString() : "—"}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted text-xs">Dependencies</span>
                <span className="text-xs">{task.parent_ids?.length || 0} parent(s)</span>
              </div>
            </div>
          </div>

          {/* Latest Score */}
          {latestScore && (
            <div className="bg-card border border-border rounded-md p-5">
              <h2 className="text-sm font-semibold mb-4">Latest Score</h2>
              <div className="flex items-center justify-between mb-4">
                <ScoreBadge score={latestScore.overall} />
                <DecisionBadge decision={latestScore.decision} />
              </div>
              <div className="space-y-2">
                {[
                  { label: "Tests", score: latestScore.test_score, weight: latestScore.weights?.test },
                  { label: "Coverage", score: latestScore.coverage_score, weight: latestScore.weights?.coverage },
                  { label: "Security", score: latestScore.security_score, weight: latestScore.weights?.security },
                  { label: "Behavior", score: latestScore.behavioral_score, weight: latestScore.weights?.behavioral },
                ].map((dim) => (
                  <div key={dim.label}>
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-muted">{dim.label}</span>
                      <span className="font-medium">{dim.score} ({Math.round((dim.weight || 0) * 100)}%)</span>
                    </div>
                    <div className="h-1.5 bg-muted/10 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full"
                        style={{ width: `${dim.score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
