"use client";

const styles: Record<string, string> = {
  pending: "bg-muted/10 text-muted",
  queued: "bg-primary/10 text-primary",
  running: "bg-primary/10 text-primary animate-pulse",
  completed: "bg-accent/10 text-accent",
  failed: "bg-danger/10 text-danger",
  blocked: "bg-danger/10 text-danger",
};

export function StatusBadge({ status }: { status: string }) {
  const cls = styles[status] || styles.pending;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}
