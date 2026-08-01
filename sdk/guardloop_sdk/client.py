"""GuardLoop SDK HTTP client."""
import json
import urllib.parse
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List, Iterator

from .exceptions import GuardLoopAPIError, GuardLoopAuthError, GuardLoopTimeoutError, GuardLoopValidationError
from .models import Task, Agent, Score, PiiScan, BrowserVerify

class GuardLoopClient:
    """Python client for the GuardLoop API.

    Usage:
        client = GuardLoopClient(api_key="gl_...", base_url="https://api.guardloop.dev")
        task = client.tasks.create(name="Refactor auth", agent_id="abc123")
        score = client.tasks.score(task.id)
        if score.blocked:
            print("Task blocked — do not merge")
    """

    def __init__(self, api_key: str, base_url: str = "https://api.guardloop.dev", timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.tasks = TaskResource(self)
        self.agents = AgentResource(self)
        self.scores = ScoreResource(self)
        self.pii = PiiResource(self)
        self.browser = BrowserResource(self)

    def _request(self, method: str, path: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Any:
        url = self.base_url + path
        if params:
            query = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v is not None)
            if query:
                url += "?" + query

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read().decode())
            except:
                body = {}
            if e.code == 401:
                raise GuardLoopAuthError(body.get("detail", "Authentication failed"))
            raise GuardLoopAPIError(body.get("detail", f"HTTP {e.code}"), e.code, body)
        except urllib.error.URLError as e:
            raise GuardLoopTimeoutError(f"Connection failed: {e.reason}")
        except TimeoutError:
            raise GuardLoopTimeoutError(f"Request timed out after {self.timeout}s")

    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        return self._request("GET", path, params=params)

    def _post(self, path: str, data: Dict) -> Any:
        return self._request("POST", path, data=data)

    def _patch(self, path: str, data: Dict) -> Any:
        return self._request("PATCH", path, data=data)

    def _delete(self, path: str) -> Any:
        return self._request("DELETE", path)

    def stream_sse(self, path: str) -> Iterator[Dict]:
        """Stream Server-Sent Events from an endpoint."""
        import urllib.request
        url = self.base_url + path
        headers = {"Authorization": f"Bearer {self.api_key}", "Accept": "text/event-stream"}
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

class TaskResource:
    def __init__(self, client: GuardLoopClient):
        self._client = client

    def create(self, name: str, description: str = "", agent_id: Optional[str] = None,
               priority: int = 5, max_loops: int = 50, parent_ids: Optional[List[str]] = None,
               context_window: Optional[Dict] = None, scheduled_at: Optional[str] = None) -> Task:
        """Create a new task."""
        data = {
            "name": name,
            "description": description,
            "agent_id": agent_id,
            "priority": priority,
            "max_loops": max_loops,
            "parent_ids": parent_ids or [],
            "context_window": context_window or {},
            "scheduled_at": scheduled_at,
        }
        result = self._client._post("/tasks", data)
        return Task.from_dict(result)

    def list(self, status: Optional[str] = None, agent_id: Optional[str] = None, limit: int = 100) -> List[Task]:
        """List tasks with optional filters."""
        params = {}
        if status:
            params["status"] = status
        if agent_id:
            params["agent_id"] = agent_id
        result = self._client._get("/tasks", params)
        return [Task.from_dict(t) for t in result[:limit]]

    def get(self, task_id: str) -> Task:
        """Get a single task by ID."""
        result = self._client._get(f"/tasks/{task_id}")
        return Task.from_dict(result)

    def update(self, task_id: str, **kwargs) -> Task:
        """Update task fields."""
        result = self._client._patch(f"/tasks/{task_id}", kwargs)
        return Task.from_dict(result)

    def start(self, task_id: str) -> Dict[str, Any]:
        """Start a task (checks dependencies first)."""
        return self._client._post(f"/tasks/{task_id}/start", {})

    def score(self, task_id: str) -> Score:
        """Calculate confidence score for a task."""
        result = self._client._post(f"/tasks/{task_id}/score", {})
        return Score.from_dict(result)

    def dependency_graph(self, task_id: str) -> Dict[str, Any]:
        """Get dependency graph visualization data."""
        return self._client._get(f"/tasks/{task_id}/dependency-graph")

    def stream(self, task_id: str) -> Iterator[Dict]:
        """Stream real-time events for a task."""
        return self._client.stream_sse(f"/tasks/{task_id}/stream")

class AgentResource:
    def __init__(self, client: GuardLoopClient):
        self._client = client

    def create(self, name: str, agent_type: str, config: Optional[Dict] = None) -> Agent:
        """Register a new agent."""
        data = {"name": name, "agent_type": agent_type, "config": config or {}}
        result = self._client._post("/agents", data)
        return Agent.from_dict(result)

    def list(self, agent_type: Optional[str] = None, status: Optional[str] = None) -> List[Agent]:
        """List registered agents."""
        params = {}
        if agent_type:
            params["agent_type"] = agent_type
        if status:
            params["status"] = status
        result = self._client._get("/agents", params)
        return [Agent.from_dict(a) for a in result]

    def get(self, agent_id: str) -> Agent:
        """Get agent details."""
        result = self._client._get(f"/agents/{agent_id}")
        return Agent.from_dict(result)

    def update(self, agent_id: str, **kwargs) -> Agent:
        """Update agent configuration."""
        result = self._client._patch(f"/agents/{agent_id}", kwargs)
        return Agent.from_dict(result)

    def delete(self, agent_id: str) -> bool:
        """Remove an agent."""
        self._client._delete(f"/agents/{agent_id}")
        return True

class ScoreResource:
    def __init__(self, client: GuardLoopClient):
        self._client = client

    def list(self, task_id: Optional[str] = None, decision: Optional[str] = None, limit: int = 100) -> List[Score]:
        """List confidence scores."""
        params = {}
        if task_id:
            params["task_id"] = task_id
        if decision:
            params["decision"] = decision
        result = self._client._get("/scores", params)
        return [Score.from_dict(s) for s in result[:limit]]

    def get(self, score_id: str) -> Score:
        """Get a single score."""
        result = self._client._get(f"/scores/{score_id}")
        return Score.from_dict(result)

    def override(self, score_id: str, decision: str, reason: str) -> Score:
        """Override a score decision."""
        data = {"decision": decision, "reason": reason}
        result = self._client._post(f"/scores/{score_id}/override", data)
        return Score.from_dict(result)

class PiiResource:
    def __init__(self, client: GuardLoopClient):
        self._client = client

    def scrub(self, task_id: str, context_text: str, strict_mode: bool = False) -> Dict[str, Any]:
        """Scan and scrub context for PII and secrets."""
        data = {
            "task_id": task_id,
            "context_text": context_text,
            "strict_mode": strict_mode,
        }
        return self._client._post("/pii/scrub", data)

    def scans(self, task_id: str) -> List[PiiScan]:
        """Get PII scan history for a task."""
        result = self._client._get(f"/pii/scans/{task_id}")
        return [PiiScan.from_dict(s) for s in result]

class BrowserResource:
    def __init__(self, client: GuardLoopClient):
        self._client = client

    def verify(self, task_id: str, url: str, viewport_width: int = 1280, viewport_height: int = 720,
               run_a11y: bool = True, run_visual_regression: bool = True) -> Dict[str, Any]:
        """Queue browser verification for a URL."""
        data = {
            "task_id": task_id,
            "url": url,
            "viewport_width": viewport_width,
            "viewport_height": viewport_height,
            "run_a11y": run_a11y,
            "run_visual_regression": run_visual_regression,
        }
        return self._client._post("/browser/verify", data)

    def list(self, task_id: str) -> List[BrowserVerify]:
        """List browser verifications for a task."""
        result = self._client._get(f"/browser/verifications/{task_id}")
        return [BrowserVerify.from_dict(v) for v in result]
