from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Interface for local LLM clients."""

    @abstractmethod
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Return the raw model answer as text."""
        raise NotImplementedError
