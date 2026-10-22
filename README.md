# Human-Like-Memory-AI-Model

An AI memory architecture designed to make intelligent systems remember, forget, and evolve like humans.

## Project layout

```
backend/app/   FastAPI app, memory pipeline, belief graph, PostgreSQL stores, Groq LLM layer
frontend/      React + Vite chat dashboard
```

## Setup

### 1. Backend

Requires Python 3.12 and a PostgreSQL database.

```bash
python -m venv venv
# Windows: venv\Scripts\activate      macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # then fill in GROQ_API_KEY and DATABASE_URL
```

Run from the project root (the folder that contains `backend/`):

```bash
uvicorn backend.app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs  -  health check: http://127.0.0.1:8000/health

Optional environment variable: `CORS_ORIGINS` (comma separated) to allow extra frontend origins.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` if the backend is not at `http://127.0.0.1:8000`.

## Tests

Tests are runnable scripts. Run them from the project root, for example:

```bash
python -m backend.app.memory.test_decision_engine
```

Tests under `storage/postgres/` and the full-lifecycle tests need a working `DATABASE_URL`;
`llm/test_groq.py` needs a valid `GROQ_API_KEY`.
