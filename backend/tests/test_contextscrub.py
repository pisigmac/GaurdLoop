import pytest
from app.services.contextscrub import ContextScrub

class TestContextScrub:
    def test_email_redaction(self):
        scrubber = ContextScrub()
        text = "Contact me at john@example.com for details."
        result = scrubber.scrub(text)
        assert "john@example.com" not in result.scrubbed_text
        assert "[EMAIL_REDACTED]" in result.scrubbed_text
        assert not result.blocked

    def test_secret_blocking(self):
        scrubber = ContextScrub(strict_mode=True)
        text = "AWS key: AKIAIOSFODNN7EXAMPLE and token: ghP_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        result = scrubber.scrub(text)
        assert result.blocked
        assert "AWS_ACCESS_KEY" in [s["type"] for s in result.secrets_found]

    def test_no_pii_passes(self):
        scrubber = ContextScrub()
        text = "This is a clean code snippet with no personal data."
        result = scrubber.scrub(text)
        assert not result.blocked
        assert len(result.findings) == 0
