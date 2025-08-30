# PassCheck — Full Stack (Flask API + React UI)

## Structure
- `backend/` — Flask API (Render-friendly)
- `ui/` — React (Vite) frontend

## Deploy Quick
1) Push this repo to GitHub.
2) **Backend (Render):** New Web Service → Build: `pip install -r requirements.txt` → Start: `gunicorn app:app`.
3) **Frontend (Netlify/Vercel):**
   - Set env var `VITE_API_BASE` to your Render URL (or add `.env` in repo).
   - Build: `npm run build` → Publish `dist/`.

## Local Dev
- Backend:
  ```bash
  cd backend
  python -m venv .venv && . .venv/Scripts/activate  # on Windows
  pip install -r requirements.txt
  python app.py
  ```
- UI:
  ```bash
  cd ui
  npm install
  npm run dev
  ```
