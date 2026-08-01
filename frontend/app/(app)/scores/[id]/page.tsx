"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { ScoreBadge } from "@/components/score-badge";
import { DecisionBadge } from "@/components/decision-badge";
import {
  ArrowLeft,
  AlertCircle,
  Activity,
  CheckCircle2,
  XCircle,
  ShieldCheck,
  FileText,
} from "lucide-react";
import Link from "next/link";

export default function ScoreDetailPage() {
  const params = useParams();
  const scoreId = params.id as string;
  const [score, setScore] = useState<any>(null);
  const [task, setTask] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const s = await api.scores.get(scoreId);
      setScore(s);
      if (s?.task_id) {
        const t = await api.tasks.get(s.task_id);
        setTask(t);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, [scoreId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Activity className="w-5 h-5 text-primary animate-spin" />
      </div>
    );
  }

  if (!score) {
    return (
      <div className="text-center py-16">
        <AlertCircle className="w-8 h-8 text-danger mx-auto mb-3" />
        <p className="text-muted text-sm">Score not found.</p>
        <Link href="/scores" className="text-primary text-sm mt-2 inline-block hover:underline">
          Back to scores
        </Link>
      </div>
    );
  }

  const dimensions = [
    {
      key: "test",
      label: "Tests",
      score: score.test_score,
      weight: score.weights?.test || 0.40,
      icon: CheckCircle2,
      details: score.test_details,
    },
    {
      key: "coverage",
      label: "Coverage",
      score: score.coverage_score,
      weight: score.weights?.coverage || 0.25,
      icon: FileText,
      details: score.coverage_details || score.test_details,
    },
    {
      key: "security",
      label: "Security",
      score: score.security_score,
      weight: score.weights?.security || 0.20,
      icon: ShieldCheck,
      details: score.security_details,
    },
    {
      key: "behavioral",
      label: "Behavior",
      score: score.behavioral_score,
      weight: score.weights?.behavioral || 0.15,
      icon: Activity,
      details: score.behavioral_details,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link href="/scores" className="inline-flex items-center gap-1 text-xs text-muted hover:text-foreground mb-2 transition-colors">
            <ArrowLeft className="w-3 h-3" /> All scores
          </Link>
          <h1 className="text-2xl font-semibold tracking-tight">Score Details</h1>
          <div className="flex items-center gap-3 mt-2">
            <ScoreBadge score={score.overall} />
            <DecisionBadge decision={score.decision} />
            <span className="text-xs text-muted">ID: {score.id}</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left — Dimensions */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-card border border-border rounded-md p-5">
            <h2 className="text-sm font-semibold mb-4">Score Breakdown</h2>
            <div className="space-y-5">
              {dimensions.map((dim) => {
                const Icon = dim.icon;
                const isWeak = dim.score < 70;
                return (
                  <div key={dim.key}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Icon className={`w-4 h-4 ${isWeak ? "text-danger" : "text-primary"}`} />
                        <span className="text-sm font-medium">{dim.label}</span>
                      </div>
                      <div className="text-sm font-medium">
                        {dim.score} <span className="text-muted text-xs">({Math.round(dim.weight * 100)}%)</span>
                      </div>
                    </div>
                    <div className="h-2 bg-muted/10 rounded-full overflow-hidden mb-2">
                      <div
                        className={`h-full rounded-full ${isWeak ? "bg-danger" : "bg-primary"}`}
                        style={{ width: `${dim.score}%` }}
                      />
                    </div>
                    {dim.details && Object.keys(dim.details).length > 0 && (
                      <div className="bg-muted/5 rounded-md p-3">
                        <pre className="text-xs text-muted overflow-auto">
                          {JSON.stringify(dim.details, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Weights */}
          <div className="bg-card border border-border rounded-md p-5">
            <h2 className="text-sm font-semibold mb-3">Weights Used</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {dimensions.map((dim) => (
                <div key={dim.key} className="text-center">
                  <div className="text-2xl font-bold">{Math.round(dim.weight * 100)}%</div>
                  <div className="text-xs text-muted mt-1">{dim.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Override */}
          {score.override_by && (
            <div className="bg-card border border-border rounded-md p-5">
              <h2 className="text-sm font-semibold mb-2">Override</h2>
              <div className="text-sm">
                <p className="text-muted">Overridden by <span className="font-medium">{score.override_by}</span></p>
                <p className="text-muted mt-1">Reason: {score.override_reason}</p>
              </div>
            </div>
          )}
        </div>

        {/* Right — Meta */}
        <div className="space-y-6">
          <div className="bg-card border border-border rounded-md p-5">
            <h2 className="text-sm font-semibold mb-4">Score Info</h2>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted text-xs">Task</span>
                <Link href={`/tasks/${score.task_id}`} className="text-primary text-xs hover:underline">
                  {score.task_id.slice(0, 8)}
                </Link>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted text-xs">Organization</span>
                <span className="text-xs">{score.org_id.slice(0, 8)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted text-xs">Created</span>
                <span className="text-xs">{score.created_at ? new Date(score.created_at).toLocaleString() : "—"}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted text-xs">Decision</span>
                <DecisionBadge decision={score.decision} />
              </div>
            </div>
          </div>

          {task && (
            <div className="bg-card border border-border rounded-md p-5">
              <h2 className="text-sm font-semibold mb-3">Task</h2>
              <div className="text-sm font-medium mb-1">{task.name}</div>
              <div className="text-xs text-muted mb-3">{task.description || "No description"}</div>
              <Link
                href={`/tasks/${task.id}`}
                className="inline-flex items-center gap-1 text-xs text-primary hover:underline"
              >
                View task <ArrowLeft className="w-3 h-3 rotate-180" />
              </Link>
            </div>
          )}

          {/* Override Form */}
          <div className="bg-card border border-border rounded-md p-5">
            <h2 className="text-sm font-semibold mb-3">Override Decision</h2>
            <p className="text-xs text-muted mb-3">
              Manually override the automated decision. Use with caution.
            </p>
            <div className="space-y-2">
              {["auto_approve", "human_review", "block"].map((decision) => (
                <button
                  key={decision}
                  onClick={() => {
                    const reason = prompt("Reason for override:");
                    if (reason) {
                      api.scores.override(score.id, { decision, reason }).then(load);
                    }
                  }}
                  className="w-full text-left px-3 py-2 text-xs font-medium border border-border rounded-md hover:bg-muted/5 transition-colors"
                >
                  Set to {decision.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
