import pytest
from unittest.mock import patch, MagicMock
from guardloop_sdk import GuardLoopClient, GuardLoopAPIError, GuardLoopAuthError
from guardloop_sdk.models import Task, Score, Decision

class TestGuardLoopClient:
    def test_create_task(self):
        client = GuardLoopClient(api_key="test", base_url="http://test")
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": "t1", "org_id": "o1", "name": "Test", "status": "pending"}'

        with patch("urllib.request.urlopen", return_value=mock_resp):
            task = client.tasks.create(name="Test")
            assert task.name == "Test"
            assert task.status.value == "pending"

    def test_auth_error(self):
        client = GuardLoopClient(api_key="bad", base_url="http://test")
        mock_err = MagicMock()
        mock_err.read.return_value = b'{"detail": "Unauthorized"}'
        mock_err.code = 401

        with patch("urllib.request.urlopen", side_effect=GuardLoopAuthError("Unauthorized")):
            with pytest.raises(GuardLoopAuthError):
                client.tasks.list()

    def test_score_passed(self):
        score = Score.from_dict({
            "id": "s1", "task_id": "t1", "org_id": "o1",
            "overall": 95, "decision": "auto_approve",
            "test_score": 100, "coverage_score": 100,
            "security_score": 100, "behavioral_score": 100,
        })
        assert score.passed is True
        assert score.needs_review is False
        assert score.blocked is False
