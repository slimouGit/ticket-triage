# Ticket Triage with Local LLMs

A clean FastAPI backend that analyzes software support tickets with a local LLM (Ollama or LM Studio), validates structured output with Pydantic, and stores results in SQLite.

This project is designed as a reference portfolio project for AI Engineering and Backend Engineering roles.

It includes a React frontend (`frontend/`) that can run in dev mode or be built and served by FastAPI on port 8000.

## What this project demonstrates

- Local LLM integration through OpenAI-compatible APIs
- Provider abstraction (Ollama and LM Studio)
- Structured JSON generation and validation
- Defensive JSON parsing for imperfect model output
- Service/repository architecture
- FastAPI API design and Swagger documentation
- SQLite persistence
- Automated tests with fake LLM client
- CI with GitHub Actions

## Tech stack

- Python 3.11+
- FastAPI
- Pydantic v2
- OpenAI Python SDK (for OpenAI-compatible local servers)
- SQLite
- Pytest
- React + TypeScript
- Vite

## Architecture

```text
Client (Swagger / script)
          |
          v
FastAPI endpoints (app/main.py)
          |
          v
TicketTriageService (app/services/triage_service.py)
          |
          +--> LLMClient interface (app/llm/base.py)
          |        |
          |        +--> OpenAICompatibleLLMClient (app/llm/openai_compatible.py)
          |                |
          |                +--> Ollama or LM Studio
          |
          +--> TicketRepository (app/db/repository.py)
                   |
                   +--> SQLite
```

## Project structure

```text
ticket-triage/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db/
│   │   └── repository.py
│   ├── llm/
│   │   ├── base.py
│   │   └── openai_compatible.py
│   ├── schemas/
│   │   └── ticket.py
│   └── services/
│       └── triage_service.py
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── examples/
│   └── sample_ticket.json
├── tests/
│   └── test_triage_service.py
├── .github/workflows/
│   └── tests.yml
├── .env.example
├── requirements.txt
├── LICENSE
└── README.md
```

## Quickstart

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

### 3. Configure environment

Copy `.env.example` to `.env` and set your provider values.

Example for Ollama:

```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=llama3.2:latest
LLM_API_KEY=ollama
DATABASE_URL=tickets.db
```

Example for LM Studio:

```env
LLM_PROVIDER=lmstudio
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=local-model
LLM_API_KEY=lm-studio
DATABASE_URL=tickets.db
```

### 4. Ensure your local model is available

Ollama example:

```bash
ollama pull llama3.2:latest
ollama list
```

### 5. Run the API

```bash
python -m uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Frontend usage

You have two ways to run the frontend.

### Option A: Dev mode (Vite + backend API)

Terminal 1 (backend):

```bash
python -m uvicorn app.main:app --reload
```

Terminal 2 (frontend):

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

### Option B: Single URL on port 8000 (recommended for demo/deploy)

Build frontend assets:

```bash
cd frontend
npm run build
cd ..
```

Then run FastAPI:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI serves files from `frontend/dist` (including SPA fallback routes).

## Build and deploy

Use this checklist to deploy on a server or VPS.

### 1. Clone and install backend

```bash
git clone https://github.com/slimouGit/ticket-triage.git
cd ticket-triage
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Set `.env` values for your LLM provider (`LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY`).

### 3. Build frontend

```bash
cd frontend
npm ci
npm run build
cd ..
```

### 4. Run app (API + frontend)

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. Verify deployment

- Frontend: `GET /`
- API health: `GET /health`
- API docs: `GET /docs`

### 6. Keep it running

Use a process manager (for example systemd, PM2, supervisor, or Docker) so the app restarts after failures and reboot.

## API overview

- `GET /health`: service and model config sanity check
- `POST /tickets/analyze`: analyze and persist one ticket
- `GET /tickets`: list stored analyses
- `GET /tickets/{ticket_id}`: fetch one stored ticket
- `DELETE /tickets/{ticket_id}`: delete a stored ticket

## Add a new ticket (PowerShell)

```powershell
$body = Get-Content .\examples\sample_ticket.json -Raw
Invoke-RestMethod -Uri http://127.0.0.1:8000/tickets/analyze -Method Post -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 8
```

## Testing

Run all tests:

```bash
pytest -q
```

Tests do not require a running local LLM provider because they use fake LLM clients.

## CI

A GitHub Actions workflow runs tests on push and pull requests:

- `.github/workflows/tests.yml`

## Common troubleshooting

### Error: model not found

If `/tickets/analyze` returns an error like model not found:

1. Check available models with `ollama list`
2. Update `LLM_MODEL` in `.env` to a model that exists locally
3. Restart the API server

### Error: provider not reachable

1. Verify Ollama or LM Studio server is running
2. Verify `LLM_BASE_URL` in `.env`
3. Check `GET /health`

## Limitations

- No auth and RBAC
- No external ticket integrations
- No background job queue
- SQLite only
- Frontend is intentionally lightweight and focused on demo workflows

## License

MIT
