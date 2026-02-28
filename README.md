# Interview Intelligence API

This is the FastAPI backend for the Interview Intelligence Platform. It handles PDF resume ingestion, NLP evaluation utilizing OpenAI and FAISS vector search, and strict workflow state tracking using an internal asynchronous database.

## Production Tech Stack
- **Framework**: FastAPI (Async)
- **Database**: PostgreSQL (via `asyncpg` + SQLAlchemy) / SQLite (Local fallback)
- **Vector DB**: FAISS (in-memory per session)
- **AI Core**: OpenAI `gpt-4o` & `text-embedding-3-small`
- **Server**: Uvicorn

---

## Railway Deployment Instructions

This repository is pre-configured for zero-downtime deployment on Railway.

1. Connect your GitHub repository to a new Railway project.
2. Railway will automatically detect the **Procfile** and install dependencies using `requirements.txt`.
3. Provision a **PostgreSQL** database addon within your Railway project.

### Required Environment Variables

You must configure the following standard environment variables securely inside your Railway dashboard under the **Variables** tab:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | The PostgreSQL connection string provided by Railway. (e.g., `postgresql://user:pass@host/db`). *The app will automatically format this for `asyncpg`.* |
| `OPENAI_API_KEY` | Your standard OpenAI API secret key. |
| `FRONTEND_URL` | The production URL of your deployed Next.js frontend to securely configure CORS (e.g., `https://my-interview-app.vercel.app`). |
| `JWT_SECRET` | A secure, long, randomized string used to encode HTTP sessions and tokens. |

### Build Command
Railway will execute:
`pip install -r requirements.txt`

### Start Command
Railway will execute (defined in Procfile):
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## Local Development Setup

To run this backend locally:

1. Create a Python Virtual Environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install Dependencies:
```bash
pip install -r requirements.txt
```

3. Configure `.env` based on `.env.example`:
```ini
OPENAI_API_KEY=sk-your-key
JWT_SECRET=super_secret_local_key
# DATABASE_URL is optional locally; defaults to SQLite automatically.
```

4. Run the Dev Server:
```bash
uvicorn app.main:app --reload
```
