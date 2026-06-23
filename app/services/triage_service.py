import json
import re

from app.llm.base import LLMClient
from app.schemas.ticket import TicketInput, TriageAnalysis


SYSTEM_PROMPT = """
You are a senior software support engineer.
Analyze support tickets and bug reports.
Return exactly one valid JSON object and no markdown.

The JSON object must have this schema:
{
  "category": "bug | feature_request | support | security | performance | data | unknown",
  "severity": "low | medium | high | critical",
  "component": "short affected component name",
  "summary": "one sentence summary",
  "reproduction_steps": ["step 1", "step 2"],
  "suspected_root_cause": "short technical hypothesis",
  "recommended_actions": ["action 1", "action 2"],
  "test_ideas": ["test idea 1", "test idea 2"],
  "confidence": 0.0
}

Severity guidance:
- critical: data loss, payment outage, authentication bypass, broad production outage
- high: production feature broken for many users or clear business impact
- medium: workaround exists or impact is limited
- low: cosmetic, documentation, minor usability issue
""".strip()


class TicketTriageService:
    """Service that turns raw ticket input into validated triage analysis."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def analyze(self, ticket: TicketInput) -> TriageAnalysis:
        user_prompt = self._build_user_prompt(ticket)
        raw_answer = self.llm_client.chat(SYSTEM_PROMPT, user_prompt)
        data = self._parse_json_object(raw_answer)
        return TriageAnalysis.model_validate(data)

    def _build_user_prompt(self, ticket: TicketInput) -> str:
        return f"""
Analyze this ticket.

Title:
{ticket.title}

Description:
{ticket.description}

Reported by:
{ticket.reported_by or "unknown"}

Environment:
{ticket.environment or "unknown"}

Logs:
{ticket.logs or "no logs provided"}
""".strip()

    def _parse_json_object(self, raw_answer: str) -> dict:
        """Parse JSON and recover if a model adds text around it."""
        raw_answer = raw_answer.strip()
        try:
            parsed = json.loads(raw_answer)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", raw_answer, flags=re.DOTALL)
        if not match:
            raise ValueError(f"LLM did not return a JSON object: {raw_answer}")

        parsed = json.loads(match.group(0))
        if not isinstance(parsed, dict):
            raise ValueError("LLM JSON response is not an object.")
        return parsed
