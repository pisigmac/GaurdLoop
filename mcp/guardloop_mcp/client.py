"""Internal HTTP client for the MCP server."""
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

class GuardLoopMCPClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, data: Optional[Dict] = None) -> Any:
        url = self.base_url + path
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())

    def score_task(self, task_id: str) -> Dict:
        return self._request("POST", f"/tasks/{task_id}/score")

    def scrub_context(self, task_id: str, context_text: str, strict_mode: bool = False) -> Dict:
        return self._request("POST", "/pii/scrub", {
            "task_id": task_id,
            "context_text": context_text,
            "strict_mode": strict_mode,
        })

    def verify_browser(self, task_id: str, url: str, viewport_width: int = 1280, viewport_height: int = 720) -> Dict:
        return self._request("POST", "/browser/verify", {
            "task_id": task_id,
            "url": url,
            "viewport_width": viewport_width,
            "viewport_height": viewport_height,
        })

    def get_task(self, task_id: str) -> Dict:
        return self._request("GET", f"/tasks/{task_id}")

    def list_agents(self, agent_type: Optional[str] = None) -> List[Dict]:
        params = {}
        if agent_type:
            params["agent_type"] = agent_type
        url = "/agents"
        if params:
            url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
        return self._request("GET", url)

    def create_task(self, name: str, description: str = "", agent_id: Optional[str] = None,
                    priority: int = 5, max_loops: int = 50, parent_ids: Optional[List[str]] = None) -> Dict:
        return self._request("POST", "/tasks", {
            "name": name,
            "description": description,
            "agent_id": agent_id,
            "priority": priority,
            "max_loops": max_loops,
            "parent_ids": parent_ids or [],
        })

    def override_score(self, score_id: str, decision: str, reason: str) -> Dict:
        return self._request("POST", f"/scores/{score_id}/override", {
            "decision": decision,
            "reason": reason,
        })
