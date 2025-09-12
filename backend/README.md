# CrystaLens Backend (FastAPI)

## Development

1. Create and activate a virtualenv

```bash
python3 -m venv .venv && source .venv/bin/activate
```

2. Install deps (from project root requirements) and install the package in editable mode

```bash
pip install -r ../requirements.txt
pip install -e ..
```

3. Run server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API

- POST `/api/runs` -> `{ run_id }`
- WS `/api/runs/{run_id}/stream` -> JSON events: `status | result | error | done`

The adapter imports `root_agent` from `src/agent.py` and calls it with `{ "input": str, "options": dict }`.
