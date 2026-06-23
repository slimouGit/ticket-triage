from openai import OpenAI

from app.llm.base import LLMClient


class OpenAICompatibleLLMClient(LLMClient):
    """LLM client for Ollama and LM Studio via OpenAI-compatible endpoints."""

    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content or ""
