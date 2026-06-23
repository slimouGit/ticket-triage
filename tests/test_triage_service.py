from app.llm.base import LLMClient
from app.schemas.ticket import TicketInput
from app.services.triage_service import TicketTriageService
from pydantic import ValidationError
import pytest


class FakeLLMClient(LLMClient):
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        return """
        {
          "category": "bug",
          "severity": "high",
          "component": "checkout",
          "summary": "Checkout fails when a coupon is applied.",
          "reproduction_steps": ["Open checkout", "Enter coupon", "Click Pay"],
          "suspected_root_cause": "CouponService may not handle missing discount metadata.",
          "recommended_actions": ["Inspect CouponService", "Add null checks"],
          "test_ideas": ["Test valid coupon", "Test missing coupon metadata"],
          "confidence": 0.85
        }
        """


class WrappedJSONFakeLLMClient(LLMClient):
        def chat(self, system_prompt: str, user_prompt: str) -> str:
                return """
                Here is the analysis:
                {
                    "category": "bug",
                    "severity": "medium",
                    "component": "auth",
                    "summary": "Login intermittently fails for some users.",
                    "reproduction_steps": ["Open login", "Submit valid credentials"],
                    "suspected_root_cause": "Session token race condition.",
                    "recommended_actions": ["Inspect token creation flow"],
                    "test_ideas": ["Concurrent login test"],
                    "confidence": 0.7
                }
                End of message.
                """


class InvalidSchemaFakeLLMClient(LLMClient):
        def chat(self, system_prompt: str, user_prompt: str) -> str:
                return """
                {
                    "category": "bug",
                    "severity": "high",
                    "component": "checkout",
                    "summary": "Missing confidence field should fail validation.",
                    "reproduction_steps": ["Step 1"],
                    "suspected_root_cause": "Example validation failure",
                    "recommended_actions": ["Fix schema"],
                    "test_ideas": ["Schema validation test"]
                }
                """


def test_triage_service_returns_valid_analysis() -> None:
    service = TicketTriageService(FakeLLMClient())
    ticket = TicketInput(
        title="Checkout fails",
        description="Checkout fails when a coupon is used.",
        environment="production",
        logs="NullPointerException in CouponService",
    )

    analysis = service.analyze(ticket)

    assert analysis.category == "bug"
    assert analysis.severity == "high"
    assert analysis.component == "checkout"
    assert analysis.confidence == 0.85
    assert len(analysis.test_ideas) == 2


def test_triage_service_parses_json_wrapped_in_text() -> None:
    service = TicketTriageService(WrappedJSONFakeLLMClient())
    ticket = TicketInput(
        title="Login fails intermittently",
        description="Some users cannot log in even with valid credentials.",
    )

    analysis = service.analyze(ticket)

    assert analysis.category == "bug"
    assert analysis.component == "auth"
    assert analysis.confidence == 0.7


def test_triage_service_raises_for_invalid_schema() -> None:
    service = TicketTriageService(InvalidSchemaFakeLLMClient())
    ticket = TicketInput(
        title="Schema mismatch",
        description="The model response should fail Pydantic validation.",
    )

    with pytest.raises(ValidationError):
        service.analyze(ticket)
