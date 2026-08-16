# Automated Meeting Minutes Generation using ASR & LLMs

Capstone project: converts meeting audio/video into structured meeting
minutes (summary, key discussions, decisions, action items with deadlines).

## Repo layout

```
src/               ML pipeline research code (owned by the ML teammate — do not edit here)
backend/           FastAPI app + API-facing ml_pipeline/ plug-in modules (owned by this track)
frontend/          React + Vite + Tailwind web app (owned by this track)
requirements.txt   Root-level ML env (Whisper, pyannote, spaCy, torch...) — unrelated to backend/
render.yaml        Render Blueprint — deploys backend/ only (see DEPLOYMENT.md)
DEPLOYMENT.md       Step-by-step guide to deploying both services for free
ML_INTEGRATION.md   Handoff guide for plugging src/ into backend/ml_pipeline/
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
`.env` is required for local dev.

### Try the full flow

Click **Get Started**, drag in any small mp3/mp4/wav/m4a file (content
doesn't matter — the ML pipeline is mocked, see below), and watch it move
through the animated processing steps into a full results dashboard with
Summary / Transcript / Decisions / Action Items tabs and JSON/HTML/PDF
downloads.

## How the pieces fit together

1. Frontend uploads a file → `POST /upload` → backend streams it to disk,
   creates a job, returns immediately (`app/api.py`).
2. A background task runs `ml_pipeline/pipeline.py`'s `run_pipeline()`:
   preprocess → transcribe → diarize → merge → extract → assemble into a
   validated `MeetingMinutes` object (`app/schemas.py`).
3. Frontend polls `GET /status/{job_id}` for progress, then
   `GET /result/{job_id}` once complete.
4. `GET /export/{job_id}?format=json|html|pdf` generates (and caches) a
   downloadable file in any of the three formats.

Every ML stage (`preprocess_audio`, `transcribe`, `diarize`,
`extract_minutes`) currently runs a **mock implementation** returning a
consistent fake meeting, so the whole app works end-to-end today. See
[`ML_INTEGRATION.md`](ML_INTEGRATION.md) for exactly how the ML
teammate's real code from `src/` drops in later.

## Deploying

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for the full step-by-step guide —
backend on Render, frontend on Vercel, both free tier, both auto-deploying
from this repo via `render.yaml` and `frontend/vercel.json`.

## Manual setup notes

- No API keys or external accounts are required to run or develop this
  locally — the ML pipeline is fully mocked.
- Deploying (optional) needs a free Render account and a free Vercel
  account — see `DEPLOYMENT.md`.
- The ML teammate's environment (root `requirements.txt`) is heavyweight
  (torch, pyannote, Whisper, CUDA). The `backend/requirements.txt` env is
  intentionally separate and lightweight — you don't need the ML env to
  run or develop the web app.
