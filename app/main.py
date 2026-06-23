from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import APIConnectionError, APIError, APITimeoutError, NotFoundError
from pydantic import ValidationError

from app.config import get_settings
from app.db.repository import TicketRepository
from app.llm.openai_compatible import OpenAICompatibleLLMClient
from app.schemas.ticket import TicketAnalysisResponse, TicketInput, StoredTicket
from app.services.triage_service import TicketTriageService

settings = get_settings()

llm_client = OpenAICompatibleLLMClient(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
    model=settings.llm_model,
)
triage_service = TicketTriageService(llm_client=llm_client)
repository = TicketRepository(db_path=settings.database_url)

app = FastAPI(
    title="Local LLM Ticket Triage",
    description="Analyze software tickets with a local LLM via Ollama or LM Studio.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "provider": settings.llm_provider,
        "base_url": settings.llm_base_url,
        "model": settings.llm_model,
    }


@app.post("/tickets/analyze", response_model=TicketAnalysisResponse)
def analyze_ticket(ticket: TicketInput) -> TicketAnalysisResponse:
    try:
        analysis = triage_service.analyze(ticket)
        ticket_id = repository.save(ticket, analysis)
        return TicketAnalysisResponse(ticket_id=ticket_id, analysis=analysis)
    except ValidationError as exc:
        raise HTTPException(
            status_code=502,
            detail="LLM returned an invalid analysis payload that failed schema validation.",
        ) from exc
    except NotFoundError as exc:
        raise HTTPException(
            status_code=502,
            detail="Configured LLM model was not found in the provider.",
        ) from exc
    except (APIConnectionError, APITimeoutError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not reach the LLM provider. Check base URL and local model server.",
        ) from exc
    except (APIError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider returned an error: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unexpected internal error during ticket analysis.") from exc


@app.get("/tickets", response_model=list[StoredTicket])
def list_tickets() -> list[StoredTicket]:
    return repository.list_all()


@app.get("/tickets/{ticket_id}", response_model=StoredTicket)
def get_ticket(ticket_id: int) -> StoredTicket:
    ticket = repository.get(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int) -> dict:
    deleted = repository.delete(ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"deleted": True, "ticket_id": ticket_id}
