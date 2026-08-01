"""Configuration management for GuardLoop CLI."""
import json
import os
from pathlib import Path
from typing import Optional

class Config:
    def __init__(self):
        self.config_path = Path.home() / ".guardloop" / "config.json"
        self.api_url: str = ""
        self.api_key: str = ""
        self.verbose: bool = False
        self._load_defaults()

    def _load_defaults(self):
        if self.config_path.exists():
            self.load(str(self.config_path))
        # Fallback to env vars
        if not self.api_url:
            self.api_url = os.getenv("GUARDLOOP_API_URL", "http://localhost:8000")
        if not self.api_key:
            self.api_key = os.getenv("GUARDLOOP_API_KEY", "")

    def load(self, path: str):
        with open(path, "r") as f:
            data = json.load(f)
        self.api_url = data.get("api_url", self.api_url)
        self.api_key = data.get("api_key", self.api_key)
        self.verbose = data.get("verbose", self.verbose)

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump({
                "api_url": self.api_url,
                "api_key": self.api_key,
                "verbose": self.verbose,
            }, f, indent=2)
        os.chmod(self.config_path, 0o600)

    def clear(self):
        if self.config_path.exists():
            self.config_path.unlink()
        self.api_url = ""
        self.api_key = ""

    def validate(self):
        if not self.api_url:
            raise click.UsageError("API URL not configured. Run: guardloop auth login")

import click  # imported here to avoid circular issues in __init__
