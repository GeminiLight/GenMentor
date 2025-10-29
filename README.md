
Quick start
-----------

- Backend: FastAPI served by Uvicorn (default port 5000)
- Frontend: Streamlit app (default port 8501)
- One-liners to run both (after setup):
	- Start: `./scripts/start_all.sh`
	- Stop: `./scripts/stop_all.sh`

Prerequisites
-------------

- OS: Linux or macOS (tested on Linux)
- Python: 3.9–3.11 recommended (virtual environments strongly recommended)
- Internet connectivity for model and search APIs

Project structure
-----------------

Key folders:

- `backend/` — FastAPI app, agents, RAG, configuration, and vector store
- `frontend/` — Streamlit UI
- `scripts/` — helper scripts to start/stop services

Configure environment variables (backend)
-----------------------------------------

The backend relies on API keys for LLMs and search providers. Copy `.env.example` to `.env` and populate values:

1. Copy the template

```bash
cp backend/.env.example backend/.env
```

1. Edit `backend/.env` and fill in the keys you have. All variables are read by the backend at start time.

```ini
TOGETHER_API_KEY=...
DEEPSEEK_API_KEY=...
OPENAI_API_KEY=...

# search API keys (use the one(s) you plan to enable)
SERPER_API_KEY=...
BING_SUBSCRIPTION_KEY=...
BING_SEARCH_URL=...
BRAVE_API_KEY=...
```

Notes:

- You only need to provide the providers you actually use in your configuration (e.g., OpenAI or Together, one or more search providers).
- Keep `.env` out of version control. The `start` scripts will automatically load `backend/.env` before launching the API.

Install dependencies
--------------------

We recommend separate virtual environments for backend and frontend.

Backend
^^^^^^^^

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Frontend (Streamlit)
^^^^^^^^^^^^^^^^^^^^^

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Run manually (without scripts)
------------------------------

Backend (FastAPI + Uvicorn)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

```bash
cd backend
# Make sure backend/.env is configured; the app reads env vars on start
uvicorn main:app --port 5000 --reload
```

Once running, visit FastAPI docs at:

- <http://localhost:5000/docs>
- <http://localhost:5000/redoc>

Frontend (Streamlit)
^^^^^^^^^^^^^^^^^^^^

```bash
cd frontend
streamlit run main.py
```

Streamlit will show the local URL (default <http://localhost:8501>). If you need a specific port, pass `--server.port`, e.g. `streamlit run main.py --server.port 9005`.

Run with helper scripts (recommended)
-------------------------------------

Make scripts executable once:

```bash
chmod +x scripts/*.sh
```

Start both services in the background:

```bash
./scripts/start_all.sh
```

By default this runs:

- Backend on port `5000` (respects `BACKEND_PORT` env var if set)
- Frontend on default Streamlit port `8501` (respects `FRONTEND_PORT` env var if set)

Logs and PIDs:

- Logs: `logs/backend.log`, `logs/frontend.log`
- PID files: `pids/backend.pid`, `pids/frontend.pid`

Stop both services:

```bash
./scripts/stop_all.sh
```

Run services individually in the foreground:

```bash
# Backend (optional port argument, default 5000)
./scripts/start_backend.sh [PORT]

# Frontend (optional port argument; if omitted, Streamlit defaults to 8501)
./scripts/start_frontend.sh [PORT]
```

Configuration tips
------------------

- Backend configuration files live in `backend/config/` (`main.yaml`, `default.yaml`). The active model/search provider will determine which API keys are required.
- Vector store artifacts are written to `backend/data/vectorstore/` by the RAG components.

Troubleshooting
---------------

- Port already in use:
	- Change the port (e.g., `BACKEND_PORT=5001 ./scripts/start_all.sh`)
	- Or stop the process holding the port (`lsof -i :5000`).
- Missing API keys or 401 errors:
	- Ensure `backend/.env` contains the correct keys for the providers you enabled.
	- Restart the backend after updating `.env`.
- Streamlit won’t open:
	- Check `logs/frontend.log` for import errors.
	- Reinstall frontend deps: `pip install -r frontend/requirements.txt`.
- Backend errors on startup:
	- Check `logs/backend.log`.
	- Verify Python version and that all dependencies installed.

Contributing
------------

Issues and pull requests are welcome. Please avoid committing secrets—use `.env` locally and keep `.env.example` up to date for others.
