"use client";

export function ScoreBadge({ score }: { score: number }) {
  let color = "bg-muted text-muted-foreground";
  let label = "—";

  if (score >= 90) {
    color = "bg-accent/10 text-accent";
    label = `${score}`;
  } else if (score >= 70) {
    color = "bg-warning/10 text-warning";
    label = `${score}`;
  } else if (score > 0) {
    color = "bg-danger/10 text-danger";
    label = `${score}`;
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${color}`}>
      {label}
    </span>
  );
}
