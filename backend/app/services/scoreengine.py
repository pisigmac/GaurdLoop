"""
ScoreEngine: 0-100 confidence score based on tests, coverage, security, and behavior.
"""
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class ScoreWeights:
    test: float = 0.40
    coverage: float = 0.25
    security: float = 0.20
    behavioral: float = 0.15

@dataclass
class TestResults:
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_ms: int = 0
    flaky_detected: bool = False

    @property
    def pass_rate(self) -> float:
        total = self.passed + self.failed + self.skipped
        if total == 0:
            return 0.0
        return self.passed / total

@dataclass
class CoverageReport:
    line_coverage: float = 0.0
    branch_coverage: float = 0.0
    function_coverage: float = 0.0

    @property
    def composite(self) -> float:
        return (self.line_coverage + self.branch_coverage + self.function_coverage) / 3

@dataclass
class SecurityScan:
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    secrets_exposed: int = 0

    @property
    def score(self) -> float:
        # Penalize critical/high heavily
        penalty = (self.critical * 25 + self.high * 10 + self.medium * 3 + self.low * 1)
        base = 100.0
        raw = base - penalty - (self.secrets_exposed * 15)
        return max(0.0, min(100.0, raw))

@dataclass
class BehavioralCheck:
    no_infinite_loops: bool = True
    no_context_bloat: bool = True
    no_agent_drift: bool = True
    browser_passed: bool = True

    @property
    def score(self) -> float:
        checks = [self.no_infinite_loops, self.no_context_bloat, self.no_agent_drift, self.browser_passed]
        passed = sum(checks)
        return (passed / len(checks)) * 100

class ScoreEngine:
    def __init__(self, weights: Optional[ScoreWeights] = None):
        self.weights = weights or ScoreWeights()

    def calculate(
        self,
        tests: TestResults,
        coverage: CoverageReport,
        security: SecurityScan,
        behavioral: BehavioralCheck,
    ) -> Dict:
        test_score = tests.pass_rate * 100
        coverage_score = coverage.composite * 100
        security_score = security.score
        behavioral_score = behavioral.score

        overall = round(
            test_score * self.weights.test +
            coverage_score * self.weights.coverage +
            security_score * self.weights.security +
            behavioral_score * self.weights.behavioral
        )

        overall = max(0, min(100, overall))

        # Decision logic
        if overall >= 90:
            decision = "auto_approve"
        elif overall >= 70:
            decision = "human_review"
        elif overall >= 50:
            decision = "block"
        else:
            decision = "block"

        return {
            "overall": overall,
            "test_score": round(test_score, 2),
            "coverage_score": round(coverage_score, 2),
            "security_score": round(security_score, 2),
            "behavioral_score": round(behavioral_score, 2),
            "weights": {
                "test": self.weights.test,
                "coverage": self.weights.coverage,
                "security": self.weights.security,
                "behavioral": self.weights.behavioral,
            },
            "decision": decision,
            "details": {
                "tests": {
                    "passed": tests.passed,
                    "failed": tests.failed,
                    "skipped": tests.skipped,
                    "flaky_detected": tests.flaky_detected,
                    "duration_ms": tests.duration_ms,
                },
                "coverage": {
                    "line": round(coverage.line_coverage * 100, 2),
                    "branch": round(coverage.branch_coverage * 100, 2),
                    "function": round(coverage.function_coverage * 100, 2),
                },
                "security": {
                    "critical": security.critical,
                    "high": security.high,
                    "medium": security.medium,
                    "low": security.low,
                    "secrets_exposed": security.secrets_exposed,
                },
                "behavioral": {
                    "no_infinite_loops": behavioral.no_infinite_loops,
                    "no_context_bloat": behavioral.no_context_bloat,
                    "no_agent_drift": behavioral.no_agent_drift,
                    "browser_passed": behavioral.browser_passed,
                }
            }
        }
