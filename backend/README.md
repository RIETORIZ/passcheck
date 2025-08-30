# PassCheck Backend (Flask)

## Run locally
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
# source .venv/bin/activate # macOS/Linux
pip install -r requirements.txt
python app.py
```

## Deploy to Render
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app`

Optional files if you have them:
- `common_passwords.csv`
- `knn_model.pkl`
