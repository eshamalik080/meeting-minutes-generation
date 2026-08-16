# Deployment

Backend on **Render** (free tier), frontend on **Vercel** (free tier). Both
support deploying a subdirectory of a monorepo directly from GitHub, so no
repo restructuring is needed — `backend/` and `frontend/` deploy as two
separate services from this one repo.

This needs two of your own accounts (Render, Vercel) and a few minutes of
clicking through their dashboards — that part can't be automated from here.
Everything below is the exact path to follow.

## Prerequisites

- This repo pushed to GitHub — already done (`origin` is
  `eshamalik080/meeting-minutes-generation`, `main` branch up to date
  through Phase 6).
- A [Render](https://render.com) account (sign up with GitHub — free, no
  card required for the free tier).
- A [Vercel](https://vercel.com) account (sign up with GitHub — free).

## Step 1 — Deploy the backend (Render)

1. Go to the Render dashboard → **New +** → **Blueprint**.
2. Connect your GitHub account if you haven't, then select this repo.
3. Render detects `render.yaml` at the repo root and shows one service:
   `meeting-minutes-backend`. Click **Apply**.
4. Render builds and deploys `backend/` (this is what `rootDir: backend`
   in `render.yaml` does — it does not touch `frontend/` or `src/`).
   First deploy takes a few minutes.
5. Once live, copy the service URL from the Render dashboard — it looks
   like `https://meeting-minutes-backend-xxxx.onrender.com`.
6. Verify it: open `<that URL>/health` in a browser. You should see
   `{"status":"ok","service":"meeting-minutes-backend"}`. Also check
   `<that URL>/docs` for the Swagger UI.

**Free tier caveat:** the service spins down after 15 minutes of no
traffic and takes ~30–50s to wake up on the next request. Fine for a demo
or viva; just expect the first request after idle time to be slow.

## Step 2 — Deploy the frontend (Vercel)

1. Go to the Vercel dashboard → **Add New** → **Project**.
2. Import this same GitHub repo.
3. In the import screen, set **Root Directory** to `frontend`. Vercel
   auto-detects the Vite framework preset — leave build/output settings
   as detected.
4. Under **Environment Variables**, add:
   - `VITE_API_BASE_URL` = the Render URL from Step 1 (no trailing
     slash), e.g. `https://meeting-minutes-backend-xxxx.onrender.com`
5. Click **Deploy**. Takes about a minute.
6. Copy the resulting URL, e.g. `https://meeting-minutes-generation.vercel.app`.

`frontend/vercel.json` (already in the repo) rewrites all paths to
`index.html`, so client-side routes like `/app/<job-id>` work on direct
load and page refresh, not just in-app navigation.

## Step 3 — Connect them (CORS)

The backend currently only allows `localhost` origins. Point it at your
real frontend URL:

1. Render dashboard → `meeting-minutes-backend` → **Environment**.
2. Edit `CORS_ORIGINS` to include your Vercel URL, comma-separated with
   the existing localhost entries so local dev keeps working:
   ```
   http://localhost:5173,http://127.0.0.1:5173,https://meeting-minutes-generation.vercel.app
   ```
3. Save — Render automatically redeploys with the new value (~1 minute).

## Step 4 — Test the live app

Open your Vercel URL and run the full flow: upload a small mp3/wav,
watch it process, check all four result tabs, download JSON/HTML/PDF.
If the backend was idle, the first request will be slow (see the cold
start caveat above) — that's expected, not a bug.

## Known limitations of this deployment (by design, not oversights)

- **In-memory job store**: job history is lost on every backend
  restart/redeploy (same limitation as local dev — see `app/jobs.py`).
  Fine for a demo; would need Redis or a DB for anything longer-lived.
- **Ephemeral disk**: uploaded files and generated exports live on
  Render's local disk, which is wiped on redeploy. Since the whole
  pipeline is mocked and runs in seconds, this doesn't affect the demo —
  just don't expect old export links to survive a redeploy.
- **50MB upload cap** on the deployed instance (`MAX_UPLOAD_MB=50` in
  `render.yaml`), lower than local dev's 500MB default, to stay
  comfortably inside Render free-tier request limits.

## Redeploying after future changes

Both Render and Vercel auto-deploy on every push to `main` by default
(configurable in each dashboard) — once connected, `git push` is enough;
no manual redeploy step needed for either service.
