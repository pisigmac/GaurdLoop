"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ScoreBadge } from "@/components/score-badge";
import Link from "next/link";
import { DecisionBadge } from "@/components/decision-badge";

export default function ScoresPage() {
  const [scores, setScores] = useState<any[]>([]);
  useEffect(() => { api.scores.list().then(setScores); }, []);
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Scores</h1>
        <p className="text-muted text-sm mt-1">Confidence scores and gate decisions across all tasks.</p>
      </div>
      <div className="bg-card border border-border rounded-md overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/5">
              <th className="text-left px-5 py-3 font-medium text-muted">Task</th>
              <th className="text-left px-5 py-3 font-medium text-muted">Overall</th>
              <th className="text-left px-5 py-3 font-medium text-muted">Tests</th>
              <th className="text-left px-5 py-3 font-medium text-muted">Coverage</th>
              <th className="text-left px-5 py-3 font-medium text-muted">Security</th>
              <th className="text-left px-5 py-3 font-medium text-muted">Behavior</th>
              <th className="text-left px-5 py-3 font-medium text-muted">Decision</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {scores.map((s) => (
              <tr key={s.id} className="hover:bg-muted/5">
                <td className="px-5 py-3 font-medium"><Link href={`/scores/${s.id}`} className="hover:text-primary transition-colors">{s.task_id.slice(0, 8)}</Link></td>
                <td className="px-5 py-3"><ScoreBadge score={s.overall} /></td>
                <td className="px-5 py-3 text-muted">{s.test_score}</td>
                <td className="px-5 py-3 text-muted">{s.coverage_score}</td>
                <td className="px-5 py-3 text-muted">{s.security_score}</td>
                <td className="px-5 py-3 text-muted">{s.behavioral_score}</td>
                <td className="px-5 py-3"><DecisionBadge decision={s.decision} /></td>
              </tr>
            ))}
            {scores.length === 0 && (
              <tr><td colSpan={7} className="px-5 py-8 text-center text-muted">No scores yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
