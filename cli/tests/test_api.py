import pytest
from unittest.mock import patch, MagicMock
from guardloop_cli.config import Config
from guardloop_cli.api import GuardLoopClient, GuardLoopAPIError

class TestGuardLoopClient:
    def test_get_success(self):
        cfg = Config()
        cfg.api_url = "http://test"
        cfg.api_key = "key"
        client = GuardLoopClient(cfg)

        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": "123"}'

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = client.get("/tasks/123")
            assert result["id"] == "123"

    def test_api_error(self):
        cfg = Config()
        cfg.api_url = "http://test"
        client = GuardLoopClient(cfg)

        mock_err = MagicMock()
        mock_err.read.return_value = b'{"detail": "Not found"}'
        mock_err.code = 404

        with patch("urllib.request.urlopen", side_effect=GuardLoopAPIError("Not found", 404)):
            with pytest.raises(GuardLoopAPIError) as exc:
                client.get("/tasks/999")
            assert exc.value.status_code == 404
