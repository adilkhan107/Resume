# Adil Khan – Animated Portfolio (FastAPI + SQLite + HTML/CSS/JS)

## Run
From the workspace root:
```
.\.venv\Scripts\python.exe -m pip install -r .\portfolio\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn --app-dir .\portfolio backend.main:app --reload
```

Or, from this `portfolio` directory:
```
pip install -r requirements.txt
uvicorn backend.main:app --reload
```
Open http://localhost:8000  (API docs: http://localhost:8000/docs)

The SQLite DB (backend/portfolio.db) is created and filled from the resume on first start.
To change content, edit the seed data in backend/database.py, delete portfolio.db, and restart.

Contact-form messages are stored in the DB; read them at /api/messages
(add authentication before deploying publicly).

## Notes
- Put your CV at `frontend/assets/resume.pdf` and a Download CV button appears automatically.
- Set `ADMIN_TOKEN` and call `/api/messages` with header `X-Token: <token>` to read messages.
- Replace each project's `link` in `backend/database.py` with its own repo URL (delete portfolio.db and restart).
# Resume
