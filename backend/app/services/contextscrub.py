"""
ContextScrub: Real-time PII and secret detection/redaction before LLM calls.
Uses Microsoft Presidio + custom regex for secrets.
"""
import re
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ScrubResult:
    scrubbed_text: str
    findings: List[Dict]
    secrets_found: List[Dict]
    blocked: bool
    block_reason: Optional[str]

class ContextScrub:
    SECRET_PATTERNS = {
        "AWS_ACCESS_KEY": re.compile(r"AKIA[0-9A-Z]{16}"),
        "AWS_SECRET_KEY": re.compile(r"[0-9a-zA-Z/+]{40}"),
        "GITHUB_TOKEN": re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}"),
        "SLACK_TOKEN": re.compile(r"xox[baprs]-[0-9a-zA-Z-]+"),
        "STRIPE_KEY": re.compile(r"sk_(live|test)_[0-9a-zA-Z]{24,}"),
        "PRIVATE_KEY": re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
        "API_KEY_GENERIC": re.compile(r"""(?i)(api[_-]?key|apikey)\s*[:=]\s*['"]?[a-z0-9]{16,}['"]?"""),
        "PASSWORD": re.compile(r"""(?i)(password|passwd|pwd)\s*[:=]\s*['"]?[^\s'"]+['"]?"""),
        "DATABASE_URL": re.compile(r"(?i)(postgres|mysql|mongodb)://[^:]+:[^@]+@"),
        "JWT_TOKEN": re.compile(r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"),
    }

    PII_ENTITY_TYPES = [
        "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD",
        "US_SSN", "US_PASSPORT", "IBAN", "CRYPTO", "IP_ADDRESS",
        "LOCATION", "DATE_TIME", "NRP"
    ]

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.block_threshold = 0.85 if strict_mode else 0.70
        self._presidio_available = self._init_presidio()

    def _init_presidio(self) -> bool:
        try:
            from presidio_analyzer import AnalyzerEngine
            self._analyzer = AnalyzerEngine()
            return True
        except ImportError:
            self._analyzer = None
            return False

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def scan_secrets(self, text: str) -> List[Dict]:
        findings = []
        for secret_type, pattern in self.SECRET_PATTERNS.items():
            for match in pattern.finditer(text):
                findings.append({
                    "type": secret_type,
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.95,
                    "matched": text[match.start():match.end()],
                    "replacement": f"[{secret_type}_REDACTED]",
                })
        return findings

    def scan_pii(self, text: str) -> List[Dict]:
        findings = []
        if self._presidio_available:
            try:
                results = self._analyzer.analyze(
                    text=text,
                    language="en",
                    entities=self.PII_ENTITY_TYPES,
                )
                for r in results:
                    findings.append({
                        "type": r.entity_type,
                        "start": r.start,
                        "end": r.end,
                        "confidence": r.score,
                        "matched": text[r.start:r.end],
                        "replacement": f"[{r.entity_type}_REDACTED]",
                    })
            except Exception:
                pass

        # Fallback regex for basic PII
        email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        for match in email_pattern.finditer(text):
            findings.append({
                "type": "EMAIL_ADDRESS",
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.90,
                "matched": text[match.start():match.end()],
                "replacement": "[EMAIL_REDACTED]",
            })

        return findings

    def scrub(self, text: str, entity_types: Optional[List[str]] = None) -> ScrubResult:
        raw_hash = self._hash(text)

        # Scan
        secret_findings = self.scan_secrets(text)
        pii_findings = self.scan_pii(text)
        all_findings = secret_findings + pii_findings

        # Sort by position (reverse) for replacement
        all_findings.sort(key=lambda x: x["start"], reverse=True)

        scrubbed = text
        for finding in all_findings:
            scrubbed = (
                scrubbed[:finding["start"]] +
                finding["replacement"] +
                scrubbed[finding["end"]:]
            )

        scrubbed_hash = self._hash(scrubbed)

        # Block decision
        blocked = False
        block_reason = None

        if self.strict_mode and len(secret_findings) > 0:
            blocked = True
            block_reason = f"Strict mode: {len(secret_findings)} secrets found and blocked."
        elif len(secret_findings) >= 3:
            blocked = True
            block_reason = f"Too many secrets ({len(secret_findings)}) in context."
        elif any(f["confidence"] > self.block_threshold for f in pii_findings):
            high_conf = [f for f in pii_findings if f["confidence"] > self.block_threshold]
            blocked = True
            block_reason = f"High-confidence PII detected: {', '.join(set(f['type'] for f in high_conf))}."

        return ScrubResult(
            scrubbed_text=scrubbed,
            findings=pii_findings,
            secrets_found=secret_findings,
            blocked=blocked,
            block_reason=block_reason,
        )
