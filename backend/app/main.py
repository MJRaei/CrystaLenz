import uuid
import json
import base64
from typing import Any, AsyncGenerator, Dict, Optional

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.staticfiles import StaticFiles

from google.adk.runners import InMemoryRunner, RunConfig
from google.genai.types import Content, Part

try:
    from src.agent import root_agent
except ModuleNotFoundError:
    import os as _os, sys as _sys
    _repo_root = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    if _repo_root not in _sys.path:
        _sys.path.insert(0, _repo_root)
    from src.agent import root_agent

# In-memory store for demo; replace with DB if needed
RUN_INPUTS: Dict[str, Dict[str, Any]] = {}


def _make_json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _make_json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_make_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_make_json_safe(v) for v in value]
    if isinstance(value, set):
        return [_make_json_safe(v) for v in value]
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    # Fallback: if not JSON serializable, stringify
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)


async def run_agent_stream(user_input: str, options: Optional[Dict[str, Any]] = None, *, session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
    yield {"type": "status", "payload": "starting"}
    try:
        from pathlib import Path
        import os
        project_root = str(Path(__file__).resolve().parents[2])
        prev_cwd = os.getcwd()
        os.chdir(project_root)
        try:
            runner = InMemoryRunner(agent=root_agent, app_name="CrystaLens")
            # Ensure the session exists before running (async method preferred)
            await runner.session_service.create_session(app_name="CrystaLens", user_id="web", session_id=session_id)
            message = Content(role="user", parts=[Part(text=user_input)])
            async for event in runner.run_async(user_id="web", session_id=session_id, new_message=message, run_config=RunConfig()):
                try:
                    payload_raw = event.model_dump(by_alias=True)
                except Exception:
                    payload_raw = str(event)
                payload = _make_json_safe(payload_raw)
                yield {"type": "event", "payload": payload}
        finally:
            os.chdir(prev_cwd)
        yield {"type": "done"}
    except Exception as exc:  # pragma: no cover
        yield {"type": "error", "payload": str(exc)}


async def create_run(request: Request):
    data = await request.json()
    user_input = data.get("input", "")
    options = data.get("options")
    run_id = str(uuid.uuid4())
    RUN_INPUTS[run_id] = {"input": user_input, "options": options}
    return JSONResponse({"run_id": run_id})


async def stream_run(websocket: WebSocket) -> None:
    await websocket.accept()
    run_id = websocket.path_params.get("run_id")
    if not run_id or run_id not in RUN_INPUTS:
        await websocket.send_json({"type": "error", "payload": f"Unknown run_id {run_id}"})
        await websocket.close()
        return

    req = RUN_INPUTS[run_id]
    try:
        async for event in run_agent_stream(req.get("input", ""), req.get("options"), session_id=run_id):
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()


routes = [
    Route("/api/runs", create_run, methods=["POST"]),
    WebSocketRoute("/api/runs/{run_id}/stream", stream_run),
]

app = Starlette(routes=routes)

# Serve generated artifacts (HTML/PNG) from xrd_outputs
from pathlib import Path as _Path
_outputs_dir = str(_Path(__file__).resolve().parents[2] / "xrd_outputs")
app.mount("/xrd_outputs", StaticFiles(directory=_outputs_dir), name="xrd_outputs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
