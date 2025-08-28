# PassCheck Oracle — Flask Web App (ready to deploy)

This bundle contains a Flask app serving your existing PassCheck UI and endpoints.

## Structure
- app.py
- templates/PasscheckUI.html
- static/images/*.png (placeholders for backgrounds)
- common_passwords.csv
- knn_model.pkl
- requirements.txt
- Procfile

## Local run
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
# App runs at http://127.0.0.1:5000
```

## Render.com deploy (recommended)
1. Push these files to a new GitHub repo.
2. In Render: **New +** → **Web Service** → connect the repo.
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn app:app`
5. Select a free instance type → **Create Web Service**.
6. After deploy, open the provided public URL.

## Replit deploy (alternative)
1. Create a new Repl (Python).
2. Upload all bundle files.
3. Add a **Run** command: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Click **Run**; use the public URL.

## Embed in Wix/Framer
- Use the public URL in an **Embed** block, or link with a "View Project" button.
