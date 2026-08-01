"""Email service for GuardLoop.

Supports Postmark, Resend, or SMTP backends.
Templates are Jinja2-based for flexibility.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from dataclasses import dataclass
from jinja2 import Environment, BaseLoader

from app.core.config import get_settings

settings = get_settings()

@dataclass
class EmailMessage:
    to: str
    subject: str
    html_body: str
    text_body: Optional[str] = None
    from_email: Optional[str] = None
    reply_to: Optional[str] = None

class EmailBackend:
    """Abstract email backend."""
    async def send(self, message: EmailMessage) -> bool:
        raise NotImplementedError

class PostmarkBackend(EmailBackend):
    """Postmark transactional email backend."""
    async def send(self, message: EmailMessage) -> bool:
        import httpx

        api_key = os.getenv("POSTMARK_API_KEY")
        if not api_key:
            raise ValueError("POSTMARK_API_KEY not set")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.postmarkapp.com/email",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "X-Postmark-Server-Token": api_key,
                },
                json={
                    "From": message.from_email or os.getenv("FROM_EMAIL", "noreply@guardloop.dev"),
                    "To": message.to,
                    "Subject": message.subject,
                    "HtmlBody": message.html_body,
                    "TextBody": message.text_body or "",
                    "ReplyTo": message.reply_to,
                },
            )
            resp.raise_for_status()
        return True

class ResendBackend(EmailBackend):
    """Resend transactional email backend."""
    async def send(self, message: EmailMessage) -> bool:
        import httpx

        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            raise ValueError("RESEND_API_KEY not set")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": message.from_email or os.getenv("FROM_EMAIL", "GuardLoop <noreply@guardloop.dev>"),
                    "to": [message.to],
                    "subject": message.subject,
                    "html": message.html_body,
                    "text": message.text_body,
                    "reply_to": message.reply_to,
                },
            )
            resp.raise_for_status()
        return True

class SMTPBackend(EmailBackend):
    """SMTP email backend for self-hosted or development."""
    async def send(self, message: EmailMessage) -> bool:
        smtp_host = os.getenv("SMTP_HOST", "localhost")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_pass = os.getenv("SMTP_PASSWORD", "")
        smtp_tls = os.getenv("SMTP_TLS", "true").lower() == "true"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = message.subject
        msg["From"] = message.from_email or os.getenv("FROM_EMAIL", "noreply@guardloop.dev")
        msg["To"] = message.to

        if message.reply_to:
            msg["Reply-To"] = message.reply_to

        if message.text_body:
            msg.attach(MIMEText(message.text_body, "plain"))
        msg.attach(MIMEText(message.html_body, "html"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_tls:
                server.starttls()
            if smtp_user:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        return True

class ConsoleBackend(EmailBackend):
    """Print emails to console for development."""
    async def send(self, message: EmailMessage) -> bool:
        print(f"\n{'='*60}")
        print(f"EMAIL: {message.subject}")
        print(f"TO: {message.to}")
        print(f"FROM: {message.from_email}")
        print(f"{'='*60}")
        print(message.html_body[:500] + "..." if len(message.html_body) > 500 else message.html_body)
        print(f"{'='*60}\n")
        return True

def get_backend() -> EmailBackend:
    """Get configured email backend."""
    backend = os.getenv("EMAIL_BACKEND", "console")

    if backend == "postmark":
        return PostmarkBackend()
    elif backend == "resend":
        return ResendBackend()
    elif backend == "smtp":
        return SMTPBackend()
    else:
        return ConsoleBackend()

class EmailService:
    """Email service with Jinja2 templates."""

    def __init__(self):
        self.backend = get_backend()
        self.jinja = Environment(loader=BaseLoader())
        self._load_templates()

    def _load_templates(self):
        """Load email templates."""
        self.templates = {
            "welcome": self._welcome_template(),
            "score_alert": self._score_alert_template(),
            "weekly_digest": self._weekly_digest_template(),
            "billing_invoice": self._billing_invoice_template(),
            "task_blocked": self._task_blocked_template(),
        }

    def _welcome_template(self):
        return {
            "subject": "Welcome to GuardLoop",
            "html": """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Inter, system-ui, sans-serif; background: #F5F0EB; padding: 40px 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: #FFFFFF; border: 1px solid #E5E5E5; border-radius: 6px; padding: 40px;">
    <h1 style="font-size: 24px; font-weight: 600; color: #1A1A1A; margin: 0 0 20px;">Welcome to GuardLoop</h1>
    <p style="font-size: 16px; color: #737373; line-height: 1.6; margin: 0 0 20px;">
      Your organization <strong>{{ org_name }}</strong> is ready to start verifying AI agent output.
    </p>
    <div style="background: #F5F0EB; border-radius: 6px; padding: 20px; margin: 20px 0;">
      <p style="font-size: 14px; color: #1A1A1A; margin: 0 0 10px;"><strong>Next steps:</strong></p>
      <ol style="font-size: 14px; color: #737373; margin: 0; padding-left: 20px;">
        <li>Connect your first agent (Cursor, Claude Code, etc.)</li>
        <li>Create a task and watch it get scored</li>
        <li>Configure scoring thresholds in Settings</li>
      </ol>
    </div>
    <a href="{{ dashboard_url }}" style="display: inline-block; background: #1A1A1A; color: #FFFFFF; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-size: 14px; font-weight: 500;">Open Dashboard</a>
    <p style="font-size: 12px; color: #737373; margin: 30px 0 0;">GuardLoop v1.0.0</p>
  </div>
</body>
</html>
""",
            "text": "Welcome to GuardLoop! Your organization {{ org_name }} is ready. Open your dashboard: {{ dashboard_url }}"
        }

    def _score_alert_template(self):
        return {
            "subject": "Task blocked — score {{ score }}/100",
            "html": """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Inter, system-ui, sans-serif; background: #F5F0EB; padding: 40px 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: #FFFFFF; border: 1px solid #E5E5E5; border-radius: 6px; padding: 40px;">
    <h1 style="font-size: 24px; font-weight: 600; color: #DC2626; margin: 0 0 20px;">Task Blocked</h1>
    <p style="font-size: 16px; color: #737373; line-height: 1.6; margin: 0 0 20px;">
      Task <strong>{{ task_name }}</strong> was blocked with a score of <strong>{{ score }}/100</strong>.
    </p>
    <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 6px; padding: 20px; margin: 20px 0;">
      <p style="font-size: 14px; color: #DC2626; margin: 0 0 10px;"><strong>Decision: {{ decision }}</strong></p>
      <p style="font-size: 14px; color: #737373; margin: 0;">{{ reason }}</p>
    </div>
    <a href="{{ task_url }}" style="display: inline-block; background: #1A1A1A; color: #FFFFFF; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-size: 14px; font-weight: 500;">View Task</a>
  </div>
</body>
</html>
""",
            "text": "Task blocked: {{ task_name }} scored {{ score }}/100. Decision: {{ decision }}. {{ reason }}"
        }

    def _weekly_digest_template(self):
        return {
            "subject": "Your GuardLoop weekly summary",
            "html": """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Inter, system-ui, sans-serif; background: #F5F0EB; padding: 40px 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: #FFFFFF; border: 1px solid #E5E5E5; border-radius: 6px; padding: 40px;">
    <h1 style="font-size: 24px; font-weight: 600; color: #1A1A1A; margin: 0 0 20px;">Weekly Summary</h1>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
      <div style="background: #F5F0EB; border-radius: 6px; padding: 20px; text-align: center;">
        <div style="font-size: 32px; font-weight: 600; color: #1A1A1A;">{{ tasks_completed }}</div>
        <div style="font-size: 12px; color: #737373; margin-top: 5px;">Tasks Completed</div>
      </div>
      <div style="background: #F5F0EB; border-radius: 6px; padding: 20px; text-align: center;">
        <div style="font-size: 32px; font-weight: 600; color: #1A1A1A;">{{ avg_score }}</div>
        <div style="font-size: 12px; color: #737373; margin-top: 5px;">Avg Score</div>
      </div>
    </div>
    <div style="margin: 20px 0;">
      <p style="font-size: 14px; color: #737373; margin: 0 0 10px;"><strong>Blocked tasks:</strong> {{ blocked_count }}</p>
      <p style="font-size: 14px; color: #737373; margin: 0 0 10px;"><strong>PII scans run:</strong> {{ pii_scans }}</p>
    </div>
    <a href="{{ dashboard_url }}" style="display: inline-block; background: #1A1A1A; color: #FFFFFF; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-size: 14px; font-weight: 500;">View Dashboard</a>
  </div>
</body>
</html>
""",
            "text": "Weekly Summary: {{ tasks_completed }} tasks completed, avg score {{ avg_score }}, {{ blocked_count }} blocked, {{ pii_scans }} PII scans."
        }

    def _billing_invoice_template(self):
        return {
            "subject": "Invoice from GuardLoop",
            "html": """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Inter, system-ui, sans-serif; background: #F5F0EB; padding: 40px 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: #FFFFFF; border: 1px solid #E5E5E5; border-radius: 6px; padding: 40px;">
    <h1 style="font-size: 24px; font-weight: 600; color: #1A1A1A; margin: 0 0 20px;">Invoice</h1>
    <p style="font-size: 16px; color: #737373; line-height: 1.6; margin: 0 0 20px;">
      Thank you for using GuardLoop. Your invoice is ready.
    </p>
    <div style="background: #F5F0EB; border-radius: 6px; padding: 20px; margin: 20px 0;">
      <p style="font-size: 14px; color: #1A1A1A; margin: 0 0 5px;"><strong>Amount:</strong> ${{ amount }}</p>
      <p style="font-size: 14px; color: #1A1A1A; margin: 0 0 5px;"><strong>Period:</strong> {{ period }}</p>
      <p style="font-size: 14px; color: #1A1A1A; margin: 0;"><strong>Status:</strong> {{ status }}</p>
    </div>
    <a href="{{ invoice_url }}" style="display: inline-block; background: #1A1A1A; color: #FFFFFF; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-size: 14px; font-weight: 500;">View Invoice</a>
  </div>
</body>
</html>
""",
            "text": "Invoice from GuardLoop. Amount: ${{ amount }}, Period: {{ period }}, Status: {{ status }}."
        }

    def _task_blocked_template(self):
        return {
            "subject": "Task blocked — {{ task_name }}",
            "html": """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Inter, system-ui, sans-serif; background: #F5F0EB; padding: 40px 20px;">
  <div style="max-width: 600px; margin: 0 auto; background: #FFFFFF; border: 1px solid #E5E5E5; border-radius: 6px; padding: 40px;">
    <h1 style="font-size: 24px; font-weight: 600; color: #DC2626; margin: 0 0 20px;">Task Blocked</h1>
    <p style="font-size: 16px; color: #737373; line-height: 1.6; margin: 0 0 20px;">
      Task <strong>{{ task_name }}</strong> was blocked by GuardLoop.
    </p>
    <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 6px; padding: 20px; margin: 20px 0;">
      <p style="font-size: 14px; color: #DC2626; margin: 0;"><strong>Reason:</strong> {{ block_reason }}</p>
    </div>
    <a href="{{ task_url }}" style="display: inline-block; background: #1A1A1A; color: #FFFFFF; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-size: 14px; font-weight: 500;">Investigate</a>
  </div>
</body>
</html>
""",
            "text": "Task blocked: {{ task_name }}. Reason: {{ block_reason }}."
        }

    async def send_template(self, template_name: str, to: str, context: Dict[str, Any]) -> bool:
        """Send an email using a template."""
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Unknown template: {template_name}")

        html_template = self.jinja.from_string(template["html"])
        text_template = self.jinja.from_string(template["text"])

        message = EmailMessage(
            to=to,
            subject=template["subject"],
            html_body=html_template.render(**context),
            text_body=text_template.render(**context),
        )

        return await self.backend.send(message)

    async def send_welcome(self, to: str, org_name: str, dashboard_url: str) -> bool:
        return await self.send_template("welcome", to, {
            "org_name": org_name,
            "dashboard_url": dashboard_url,
        })

    async def send_score_alert(self, to: str, task_name: str, score: int, 
                               decision: str, reason: str, task_url: str) -> bool:
        return await self.send_template("score_alert", to, {
            "task_name": task_name,
            "score": score,
            "decision": decision,
            "reason": reason,
            "task_url": task_url,
        })

    async def send_weekly_digest(self, to: str, tasks_completed: int, avg_score: int,
                                  blocked_count: int, pii_scans: int, dashboard_url: str) -> bool:
        return await self.send_template("weekly_digest", to, {
            "tasks_completed": tasks_completed,
            "avg_score": avg_score,
            "blocked_count": blocked_count,
            "pii_scans": pii_scans,
            "dashboard_url": dashboard_url,
        })

    async def send_billing_invoice(self, to: str, amount: str, period: str,
                                    status: str, invoice_url: str) -> bool:
        return await self.send_template("billing_invoice", to, {
            "amount": amount,
            "period": period,
            "status": status,
            "invoice_url": invoice_url,
        })

    async def send_task_blocked(self, to: str, task_name: str, block_reason: str, task_url: str) -> bool:
        return await self.send_template("task_blocked", to, {
            "task_name": task_name,
            "block_reason": block_reason,
            "task_url": task_url,
        })

# Global instance
email_service = EmailService()
