"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { Globe, Loader2 } from "lucide-react";

export default function BrowserPage() {
  const [form, setForm] = useState({ task_id: "", url: "", viewport_width: 1280, viewport_height: 720 });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const r = await api.browser.verify(form);
    setResult(r);
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Browser Verify</h1>
        <p className="text-muted text-sm mt-1">Run headless Playwright checks against agent-generated UI.</p>
      </div>
      <form onSubmit={handleSubmit} className="bg-card border border-border rounded-md p-5 space-y-4 max-w-2xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-muted mb-1.5">Task ID</label>
            <input value={form.task_id} onChange={e => setForm({...form, task_id: e.target.value})}
              className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background" required />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted mb-1.5">URL</label>
            <input value={form.url} onChange={e => setForm({...form, url: e.target.value})}
              className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background" required />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted mb-1.5">Width</label>
            <input type="number" value={form.viewport_width} onChange={e => setForm({...form, viewport_width: Number(e.target.value)})}
              className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background" />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted mb-1.5">Height</label>
            <input type="number" value={form.viewport_height} onChange={e => setForm({...form, viewport_height: Number(e.target.value)})}
              className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background" />
          </div>
        </div>
        <button type="submit" disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-foreground text-background text-sm font-medium rounded-md hover:bg-foreground/90 disabled:opacity-50">
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Globe className="w-4 h-4" />}
          Run verification
        </button>
      </form>
      {result && (
        <div className="bg-card border border-border rounded-md p-5">
          <div className="text-sm font-medium mb-2">Result</div>
          <pre className="text-xs bg-muted/5 p-3 rounded-md overflow-auto">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
