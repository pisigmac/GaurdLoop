# Payments

## Stripe Integration

### Setup

1. Create Stripe account
2. Configure products and prices in Stripe Dashboard
3. Add `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` to K8s secrets

### Webhook Events Handled

| Event | Action |
|---|---|
| `invoice.paid` | Grant/renew subscription |
| `invoice.payment_failed` | Notify user, grace period |
| `customer.subscription.deleted` | Downgrade to free |
| `customer.subscription.updated` | Update plan in DB |

### Billing Logic

```python
# backend/app/services/billing.py (scaffold)
import stripe
from app.core.config import get_settings

settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_subscription(org_id: str, price_id: str) -> dict:
    # Create Stripe customer, attach payment method, subscribe
    pass

def cancel_subscription(stripe_sub_id: str) -> dict:
    return stripe.Subscription.delete(stripe_sub_id)

def handle_webhook(payload: bytes, sig: str) -> dict:
    return stripe.Webhook.construct_event(
        payload, sig, settings.STRIPE_WEBHOOK_SECRET
    )
```

### Plans

- Free: $0
- Pro: $49/user/month (Stripe price ID: `price_pro_monthly`)
- Enterprise: Custom invoicing
