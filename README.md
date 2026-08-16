# Automated Meeting Minutes Generation using ASR & LLMs

Capstone project: converts meeting audio/video into structured meeting
minutes (summary, key discussions, decisions, action items with deadlines).

## Repo layout

```
src/               ML pipeline research code (owned by the ML teammate — do not edit here)
backend/           FastAPI app + API-facing ml_pipeline/ plug-in modules (owned by this track)
frontend/          React + Vite + Tailwind web app (owned by this track)
requirements.txt   Root-level ML env (Whisper, pyannote, spaCy, torch...) — unrelated to backend/
```

`backend/ml_pipeline/` is a separate, lightweight package from the root
`src/`. It currently contains mock implementations of each ML stage so the
full app works end-to-end. See `backend/ml_pipeline/README.md` for how the
real code from `src/` gets plugged in later.

## Running locally

You need two terminals — one for the backend, one for the frontend.

### 1. Backend (FastAPI)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Verify it's up: open http://127.0.0.1:8000/health — should return
`{"status":"ok","service":"meeting-minutes-backend"}`. Interactive API docs
are at http://127.0.0.1:8000/docs.

### 2. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. The dev server proxies `/api/*` requests to the
backend at `http://127.0.0.1:8000` (see `frontend/vite.config.ts`), so no
`.env` is required for local dev. The Phase 0 landing page shows a live
"backend: ok" check if both servers are running correctly.

## Project status

Currently on **Phase 0 — scaffolding**. Backend has a placeholder
`/health` endpoint only; frontend has a placeholder page proving the
Tailwind + API-proxy setup works. Real endpoints, the mocked ML pipeline,
exporters, and the full UI land in the phases that follow — see the
project plan for details.

## Manual setup notes

- No API keys or external accounts are required through Phase 3 — the ML
  pipeline is fully mocked.
- The ML teammate's environment (root `requirements.txt`) is heavyweight
  (torch, pyannote, Whisper, CUDA). The `backend/requirements.txt` env is
  intentionally separate and lightweight — you don't need the ML env to
  run or develop the web app.
