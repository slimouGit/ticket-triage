from typing import Literal

from pydantic import BaseModel, Field


class TicketInput(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    reported_by: str | None = Field(default=None, max_length=100)
    environment: str | None = Field(default=None, max_length=100)
    logs: str | None = Field(default=None, max_length=4000)


class TriageAnalysis(BaseModel):
    category: Literal["bug", "feature_request", "support", "security", "performance", "data", "unknown"]
    severity: Literal["low", "medium", "high", "critical"]
    component: str
    summary: str
    reproduction_steps: list[str]
    suspected_root_cause: str
    recommended_actions: list[str]
    test_ideas: list[str]
    confidence: float = Field(..., ge=0.0, le=1.0)


class TicketAnalysisResponse(BaseModel):
    ticket_id: int
    analysis: TriageAnalysis


class StoredTicket(BaseModel):
    id: int
    title: str
    description: str
    reported_by: str | None
    environment: str | None
    logs: str | None
    analysis: TriageAnalysis
    created_at: str
