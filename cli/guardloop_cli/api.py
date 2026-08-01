"""HTTP client for GuardLoop API."""
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Iterator

from guardloop_cli.config import Config

class GuardLoopClient:
    def __init__(self, config: Config):
        self.config = config

    def _request(self, method: str, path: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        url = self.config.api_url.rstrip("/") + path
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            if query:
                url += "?" + query

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            try:
                err = json.loads(e.read().decode())
                raise GuardLoopAPIError(err.get("detail", f"HTTP {e.code}"), e.code)
            except json.JSONDecodeError:
                raise GuardLoopAPIError(f"HTTP {e.code}", e.code)
        except urllib.error.URLError as e:
            raise GuardLoopAPIError(f"Connection failed: {e.reason}")

    def get(self, path: str, params: Optional[Dict] = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, data: Dict) -> Any:
        return self._request("POST", path, data=data)

    def patch(self, path: str, data: Dict) -> Any:
        return self._request("PATCH", path, data=data)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)

    def stream_sse(self, path: str) -> Iterator[Dict]:
        import urllib.request
        url = self.config.api_url.rstrip("/") + path
        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=None) as resp:
            buffer = ""
            while True:
                chunk = resp.read(1024).decode()
                if not chunk:
                    break
                buffer += chunk
                while "\n\n" in buffer:
                    part, buffer = buffer.split("\n\n", 1)
                    for line in part.strip().split("\n"):
                        if line.startswith("data: "):
                            try:
                                yield json.loads(line[6:])
                            except json.JSONDecodeError:
                                pass

class GuardLoopAPIError(Exception):
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code
