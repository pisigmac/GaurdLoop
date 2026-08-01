# Claude Integration Guide

## Prompting GuardLoop from Claude

When using Claude Code or Claude Desktop with GuardLoop, use these patterns:

### 1. Task Submission

```
Submit this change to GuardLoop for scoring before merging.
Task: "Refactor auth middleware"
Agent: cursor
Dependencies: ["task-abc-123"]
```

### 2. Context Scrub Check

```
Before sending this prompt to the LLM, run GuardLoop ContextScrub
on the full context window to check for PII or secrets.
```

### 3. Score Interpretation

```
GuardLoop scored this task at 87 (human_review).
Review the security findings: 2 medium-severity issues in input validation.
Do not merge until resolved.
```

### 4. Browser Validation

```
After this UI change, trigger GuardLoop BrowserVerify
on http://localhost:3000 to check for a11y violations.
```
