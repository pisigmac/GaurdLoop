"use client";
import { useState } from "react";
import { ShieldCheck, Plus, Trash2, CheckCircle2, Lock, Eye } from "lucide-react";

interface PiiRule {
  id: string;
  name: string;
  category: "secret" | "pii" | "financial" | "health";
  pattern_type: "regex" | "presidio";
  pattern: string;
  replacement_mask: string;
  action: "redact" | "block" | "warn";
  is_active: boolean;
}

const DEFAULT_PII_RULES: PiiRule[] = [
  {
    id: "rule-1",
    name: "Stripe Secret Key",
    category: "secret",
    pattern_type: "regex",
    pattern: "sk_live_[0-9a-zA-Z]{24,}",
    replacement_mask: "[REDACTED_STRIPE_KEY]",
    action: "block",
    is_active: true,
  },
  {
    id: "rule-2",
    name: "AWS Access Key ID",
    category: "secret",
    pattern_type: "regex",
    pattern: "AKIA[0-9A-Z]{16}",
    replacement_mask: "[REDACTED_AWS_KEY]",
    action: "block",
    is_active: true,
  },
  {
    id: "rule-3",
    name: "Social Security Number (SSN)",
    category: "pii",
    pattern_type: "regex",
    pattern: "\\b\\d{3}-\\d{2}-\\d{4}\\b",
    replacement_mask: "[REDACTED_SSN]",
    action: "redact",
    is_active: true,
  },
  {
    id: "rule-4",
    name: "Credit Card Number",
    category: "financial",
    pattern_type: "presidio",
    pattern: "CREDIT_CARD",
    replacement_mask: "[REDACTED_CREDIT_CARD]",
    action: "redact",
    is_active: true,
  },
];

export default function SettingsPage() {
  const [thresholds, setThresholds] = useState({ auto: 90, review: 70, block: 50 });
  const [piiRules, setPiiRules] = useState<PiiRule[]>(DEFAULT_PII_RULES);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newRule, setNewRule] = useState<Partial<PiiRule>>({
    name: "",
    category: "secret",
    pattern_type: "regex",
    pattern: "",
    replacement_mask: "[REDACTED_SECRET]",
    action: "redact",
    is_active: true,
  });

  const toggleRule = (id: string) => {
    setPiiRules((prev) =>
      prev.map((r) => (r.id === id ? { ...r, is_active: !r.is_active } : r))
    );
  };

  const deleteRule = (id: string) => {
    setPiiRules((prev) => prev.filter((r) => r.id !== id));
  };

  const handleAddRule = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRule.name || !newRule.pattern) return;

    const rule: PiiRule = {
      id: `rule-${Date.now()}`,
      name: newRule.name,
      category: newRule.category || "secret",
      pattern_type: newRule.pattern_type || "regex",
      pattern: newRule.pattern,
      replacement_mask: newRule.replacement_mask || "[REDACTED_DATA]",
      action: newRule.action || "redact",
      is_active: true,
    };

    setPiiRules((prev) => [rule, ...prev]);
    setNewRule({
      name: "",
      category: "secret",
      pattern_type: "regex",
      pattern: "",
      replacement_mask: "[REDACTED_SECRET]",
      action: "redact",
      is_active: true,
    });
    setShowAddForm(false);
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings & Governance</h1>
        <p className="text-muted text-sm mt-1">Configure scoring thresholds, security gates, and dynamic PII rules.</p>
      </div>

      {/* Scoring Thresholds Card */}
      <div className="bg-card border border-border rounded-md p-5 max-w-2xl space-y-4">
        <h2 className="text-sm font-semibold flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-500" />
          Confidence Gate Thresholds
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div>
            <label className="block text-xs font-medium text-muted mb-1.5">Auto-approve Threshold (≥)</label>
            <input
              type="number"
              value={thresholds.auto}
              onChange={(e) => setThresholds({ ...thresholds, auto: Number(e.target.value) })}
              className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted mb-1.5">Human Review Threshold (70-89)</label>
            <input
              type="number"
              value={thresholds.review}
              onChange={(e) => setThresholds({ ...thresholds, review: Number(e.target.value) })}
              className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted mb-1.5">Block Threshold (&lt; 70)</label>
            <input
              type="number"
              value={thresholds.block}
              onChange={(e) => setThresholds({ ...thresholds, block: Number(e.target.value) })}
              className="w-full px-3 py-2 text-sm border border-border rounded-md bg-background"
            />
          </div>
        </div>
      </div>

      {/* Dynamic PII & Secret Rules Manager */}
      <div className="bg-card border border-border rounded-md max-w-4xl overflow-hidden">
        <div className="px-5 py-4 border-b border-border flex items-center justify-between bg-muted/5">
          <div>
            <h2 className="text-sm font-semibold flex items-center gap-2">
              <Lock className="w-4 h-4 text-primary" />
              Dynamic PII & Secret Detection Rules (ContextScrub)
            </h2>
            <p className="text-xs text-muted mt-0.5">
              Real-time in-memory sanitization rules enforced before prompts reach LLMs.
            </p>
          </div>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-primary-foreground text-xs font-medium rounded-md hover:bg-primary/90 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            Add Rule
          </button>
        </div>

        {/* Add Rule Form Modal/Dropdown */}
        {showAddForm && (
          <form onSubmit={handleAddRule} className="p-5 border-b border-border bg-muted/10 space-y-4">
            <h3 className="text-xs font-semibold text-foreground uppercase tracking-wider">New Detection Rule</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-muted mb-1">Rule Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Corporate Employee ID"
                  value={newRule.name}
                  onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
                  className="w-full px-3 py-2 text-xs border border-border rounded-md bg-background"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-muted mb-1">Category</label>
                <select
                  value={newRule.category}
                  onChange={(e) => setNewRule({ ...newRule, category: e.target.value as any })}
                  className="w-full px-3 py-2 text-xs border border-border rounded-md bg-background"
                >
                  <option value="secret">Secret / Credential</option>
                  <option value="pii">PII / Personal Info</option>
                  <option value="financial">Financial Data</option>
                  <option value="health">Health Data (PHI)</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-muted mb-1">Regex Pattern / Entity</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. EMP-[0-9]{6}"
                  value={newRule.pattern}
                  onChange={(e) => setNewRule({ ...newRule, pattern: e.target.value })}
                  className="w-full px-3 py-2 text-xs border border-border rounded-md bg-background font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-muted mb-1">Replacement Mask</label>
                <input
                  type="text"
                  required
                  placeholder="[REDACTED_ID]"
                  value={newRule.replacement_mask}
                  onChange={(e) => setNewRule({ ...newRule, replacement_mask: e.target.value })}
                  className="w-full px-3 py-2 text-xs border border-border rounded-md bg-background font-mono"
                />
              </div>
            </div>
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-3 py-1.5 text-xs text-muted hover:text-foreground"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-1.5 bg-primary text-primary-foreground text-xs font-medium rounded-md hover:bg-primary/90"
              >
                Save PII Rule
              </button>
            </div>
          </form>
        )}

        {/* Rules Table */}
        <div className="divide-y divide-border overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-muted/5 border-b border-border text-muted">
                <th className="px-5 py-3 font-medium">Rule Name</th>
                <th className="px-5 py-3 font-medium">Category</th>
                <th className="px-5 py-3 font-medium">Pattern / Regex</th>
                <th className="px-5 py-3 font-medium">Action</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium text-right">Manage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {piiRules.map((rule) => (
                <tr key={rule.id} className="hover:bg-muted/5 transition-colors">
                  <td className="px-5 py-3.5 font-semibold text-foreground">{rule.name}</td>
                  <td className="px-5 py-3.5 uppercase font-mono text-[10px] text-muted">{rule.category}</td>
                  <td className="px-5 py-3.5 font-mono text-muted-foreground truncate max-w-[200px]" title={rule.pattern}>
                    {rule.pattern}
                  </td>
                  <td className="px-5 py-3.5">
                    <span
                      className={`px-2 py-0.5 text-[10px] uppercase font-semibold rounded ${
                        rule.action === "block"
                          ? "bg-rose-500/10 text-rose-500 border border-rose-500/20"
                          : "bg-amber-500/10 text-amber-500 border border-amber-500/20"
                      }`}
                    >
                      {rule.action}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <button
                      onClick={() => toggleRule(rule.id)}
                      className={`px-2 py-0.5 text-[10px] font-semibold rounded-full transition-colors ${
                        rule.is_active
                          ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                          : "bg-muted text-muted-foreground border border-border"
                      }`}
                    >
                      {rule.is_active ? "Active" : "Disabled"}
                    </button>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <button
                      onClick={() => deleteRule(rule.id)}
                      className="p-1 text-muted hover:text-rose-500 transition-colors"
                      title="Delete Rule"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
