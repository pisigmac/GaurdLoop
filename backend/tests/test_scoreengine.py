import pytest
from app.services.scoreengine import ScoreEngine, TestResults, CoverageReport, SecurityScan, BehavioralCheck

class TestScoreEngine:
    def test_perfect_score(self):
        engine = ScoreEngine()
        result = engine.calculate(
            tests=TestResults(passed=100, failed=0, skipped=0),
            coverage=CoverageReport(line_coverage=1.0, branch_coverage=1.0, function_coverage=1.0),
            security=SecurityScan(),
            behavioral=BehavioralCheck(),
        )
        assert result["overall"] == 100
        assert result["decision"] == "auto_approve"

    def test_failed_tests_block(self):
        engine = ScoreEngine()
        result = engine.calculate(
            tests=TestResults(passed=0, failed=100, skipped=0),
            coverage=CoverageReport(),
            security=SecurityScan(),
            behavioral=BehavioralCheck(),
        )
        assert result["overall"] < 50
        assert result["decision"] == "block"

    def test_security_penalty(self):
        engine = ScoreEngine()
        result = engine.calculate(
            tests=TestResults(passed=100, failed=0),
            coverage=CoverageReport(line_coverage=1.0, branch_coverage=1.0, function_coverage=1.0),
            security=SecurityScan(critical=2, secrets_exposed=1),
            behavioral=BehavioralCheck(),
        )
        assert result["security_score"] < 50
        assert result["overall"] < 90
