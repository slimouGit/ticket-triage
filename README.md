# Ticket Triage with Local LLMs

A clean FastAPI backend that analyzes software support tickets with a local LLM (Ollama or LM Studio), validates structured output with Pydantic, and stores results in SQLite.

This project is designed as a reference portfolio project for AI Engineering and Backend Engineering roles.

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
- Focused on backend and LLM orchestration, not frontend

## License

MIT
