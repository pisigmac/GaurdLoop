# Feature Flags

## Flags

| Flag | Default | Description |
|---|---|---|
| `browser_verify` | true | Enable Playwright browser checks |
| `pii_scrub_strict` | false | Block on any PII finding |
| `auto_approve` | true | Allow auto-approve gate |
| `score_override` | true | Allow manual score override |
| `sse_streaming` | true | Enable live event streaming |
| `multi_agent` | true | Support multiple agent types |
| `webhook_retry` | true | Auto-retry failed webhooks |
| `new_adapter_api` | false | New adapter v2 interface |

## Implementation

Use LaunchDarkly or Unleash for production. For now, store in `organizations.settings` JSONB.

```python
# Check flag
if org.settings.get("feature_flags", {}).get("browser_verify", True):
    await run_browser_verify(task)
```
