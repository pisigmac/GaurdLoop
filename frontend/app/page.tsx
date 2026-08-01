"use client";

import Link from "next/link";
import { ShieldCheck, Activity, Lock, Globe, ArrowRight, Check } from "lucide-react";

const features = [
  {
    icon: Activity,
    title: "Score everything",
    desc: "0-100 confidence from tests, coverage, security, and behavior. Auto-approve above 90. Block below 70.",
  },
  {
    icon: Lock,
    title: "Scrub before sending",
    desc: "Real-time PII and secret detection on every LLM call. Microsoft Presidio + custom patterns.",
  },
  {
    icon: Globe,
    title: "Verify in the browser",
    desc: "Headless Playwright checks for a11y violations and visual regression on every UI change.",
  },
  {
    icon: ShieldCheck,
    title: "Stop broken loops",
    desc: "Detect infinite loops, context bloat, and agent drift before they burn your token budget.",
  },
];

const checks = [
  "Works with Cursor, Claude Code, Copilot",
  "Dependency-aware task scheduling",
  "Real-time SSE monitoring",
  "Webhook ingestion from GitHub, Slack, Linear",
  "Multi-tenant with Clerk auth",
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <nav className="border-b border-border">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
              <ShieldCheck className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-semibold text-sm tracking-tight">GuardLoop</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="text-sm text-muted hover:text-foreground transition-colors">
              Dashboard
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-foreground text-background text-xs font-medium rounded-md hover:bg-foreground/90 transition-colors"
            >
              Get started <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-6 pt-20 pb-16">
        <div className="max-w-2xl">
          <h1 className="text-4xl font-semibold tracking-tight leading-[1.15]">
            Don't ship what an agent wrote.
            <br />
            <span className="text-primary">Ship what GuardLoop approved.</span>
          </h1>
          <p className="mt-5 text-muted text-base leading-relaxed max-w-lg">
            Cursor has agents. Claude Code has agents. Copilot has agents.
            GuardLoop has trust. A confidence layer that scores, verifies, and gates
            AI-generated code before it reaches production.
          </p>
          <div className="mt-8 flex items-center gap-3">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-foreground text-background text-sm font-medium rounded-md hover:bg-foreground/90 transition-colors"
            >
              Open dashboard <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="https://github.com/your-org/guardloop"
              className="inline-flex items-center gap-2 px-5 py-2.5 border border-border text-sm font-medium rounded-md hover:bg-muted/5 transition-colors"
            >
              View on GitHub
            </a>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-5xl mx-auto px-6 py-16 border-t border-border">
        <h2 className="text-sm font-semibold text-muted uppercase tracking-wider mb-8">
          What GuardLoop does
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((f) => {
            const Icon = f.icon;
            return (
              <div
                key={f.title}
                className="bg-card border border-border rounded-md p-6 hover:border-primary/30 transition-colors"
              >
                <div className="w-8 h-8 rounded-md bg-primary/10 flex items-center justify-center mb-4">
                  <Icon className="w-4 h-4 text-primary" />
                </div>
                <h3 className="font-semibold text-sm">{f.title}</h3>
                <p className="mt-1.5 text-muted text-sm leading-relaxed">{f.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Checks */}
      <section className="max-w-5xl mx-auto px-6 py-16 border-t border-border">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-start">
          <div>
            <h2 className="text-2xl font-semibold tracking-tight">Built for teams that ship fast.</h2>
            <p className="mt-3 text-muted text-sm leading-relaxed">
              GuardLoop doesn't replace your agents. It certifies their output.
              Plug it into Cursor Automations, Claude Code, or any custom agent pipeline.
            </p>
          </div>
          <div className="space-y-3">
            {checks.map((c) => (
              <div key={c} className="flex items-center gap-3 text-sm">
                <div className="w-5 h-5 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
                  <Check className="w-3 h-3 text-accent" />
                </div>
                <span>{c}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border mt-16">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between text-xs text-muted">
          <span>GuardLoop v1.0.0</span>
          <span>MIT License</span>
        </div>
      </footer>
    </div>
  );
}
