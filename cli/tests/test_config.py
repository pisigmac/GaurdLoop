import pytest
import os
import tempfile
from guardloop_cli.config import Config

class TestConfig:
    def test_default_api_url(self):
        cfg = Config()
        assert cfg.api_url == "http://localhost:8000"

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("GUARDLOOP_API_URL", "https://api.guardloop.dev")
        cfg = Config()
        assert cfg.api_url == "https://api.guardloop.dev"

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Config()
            cfg.config_path = os.path.join(tmp, "config.json")
            cfg.api_url = "https://test.guardloop.dev"
            cfg.api_key = "test-key"
            cfg.save()

            cfg2 = Config()
            cfg2.config_path = cfg.config_path
            cfg2.load(str(cfg.config_path))
            assert cfg2.api_url == "https://test.guardloop.dev"
            assert cfg2.api_key == "test-key"
