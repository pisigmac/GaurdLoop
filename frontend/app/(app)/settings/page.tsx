"use client";
import { useState } from "react";

export default function SettingsPage() {
  const [thresholds, setThresholds] = useState({ auto: 90, review: 70, block: 50 });
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-muted text-sm mt-1">Configure scoring thresholds and org preferences.</p>
      </div>
      <div className="bg-card border border-border rounded-md p-5 max-w-xl space-y-4">
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-muted mb-1.5">Auto-approve threshold</label>
            <input type="number" value={thresholds.auto} onChange={e => setThresholds({...thresholds, auto: Number(e.target.value)})}
              className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background" />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted mb-1.5">Human review threshold</label>
            <input type="number" value={thresholds.review} onChange={e => setThresholds({...thresholds, review: Number(e.target.value)})}
              className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background" />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted mb-1.5">Block threshold</label>
            <input type="number" value={thresholds.block} onChange={e => setThresholds({...thresholds, block: Number(e.target.value)})}
              className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background" />
          </div>
        </div>
        <button className="px-4 py-2 bg-foreground text-background text-sm font-medium rounded-md hover:bg-foreground/90">
          Save changes
        </button>
      </div>
    </div>
  );
}
