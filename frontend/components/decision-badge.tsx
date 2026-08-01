"use client";

const styles: Record<string, string> = {
  auto_approve: "bg-accent/10 text-accent",
  human_review: "bg-warning/10 text-warning",
  block: "bg-danger/10 text-danger",
  pending: "bg-muted/10 text-muted",
};

export function DecisionBadge({ decision }: { decision: string }) {
  const cls = styles[decision] || styles.pending;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${cls}`}>
      {decision.replace("_", " ")}
    </span>
  );
}
