# CISSP Study Companion v3.0

Installable daily companion PWA for CISSP exam prep — **Android, iPhone, and PC** from one link.

**v3 highlights:** per-device progress sync, Render persistent storage, 800+ diverse questions, spaced-repetition missed review, flagged questions, study plan automation, CSV export, April 2024 CAT timing (125–150 Q / 3 hr).

## Install on your devices

### Option A — Same Wi-Fi (fastest, no cloud)

1. Install **Python 3.11+** and **Node.js 18+**
2. Double-click **`start-app.bat`**
3. On your PC, open **http://localhost:8080**
4. On your phone (same Wi-Fi), open the **http://YOUR-PC-IP:8080** URL shown in the terminal
5. Install:
   - **Android:** Chrome → menu (⋮) → **Install app** or **Add to Home screen**
   - **iPhone/iPad:** Safari → **Share** → **Add to Home Screen**
   - **Windows PC:** Edge/Chrome → install icon in address bar → **Install**

### Option B — Share a public link (anywhere)

Deploy with Docker to any cloud host (Render, Railway, Fly.io, VPS):

```bash
docker compose up --build -d
```

On **Render**, use the included `render.yaml` — it mounts a **persistent disk** at `/data` so progress survives redeploys.

Your link becomes: `https://your-domain.com` — open on any device and install. Progress syncs across phone and PC when using the same browser profile (anonymous study ID).

For a quick tunnel while testing: use [ngrok](https://ngrok.com/) or [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/) pointing to port 8080.

### Option C — Developer mode (hot reload)

Use **`start-local.bat`** for separate frontend (5173) + backend (8001) during development.

---

## Features

- **Home / Daily Practice** — Random manager-style scenario questions
- **Missed Questions** — Review incorrect answers
- **Mock CAT Exam** — Adaptive 125–175 questions, CISSP scaled scoring (700/1000 pass)
- **Domain Test** — Focus on one of 8 domains
- **Analysis** — Pass rate and readiness per domain
- **Settings** — Newbie/fast/exam modes, study plan, exam countdown, dark/light theme
- **Offline-ready** — PWA caches the app shell; practice needs network for new sessions

## Stack

- **PWA:** Vite + vite-plugin-pwa (installable, standalone display)
- **Backend:** FastAPI + SQLite (single URL in app mode)
- **Questions:** 800+ unique scenario-based MCQs (8 stem formats, ISC2 April 2024 outline)

## Manual build + run (app mode)

```powershell
cd frontend
npm install
npm run build

cd ..\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set CORS_ALLOW_ALL=true
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Open **http://localhost:8080** and install from the browser.

## Reset progress

Delete `backend/cissp_study.db` and restart the server.

## Disclaimer

Not affiliated with ISC2. Mock CAT is a study simulation, not the official Pearson VUE exam engine.
