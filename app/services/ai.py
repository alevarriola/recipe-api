from dataclasses import dataclass
from typing import Protocol
from app.db.models import Recipe
from app.core.config import settings
import json
import httpx

@dataclass
class AIRecommendation:
    recommended_id: int | None
    title: str
    reason: str

class AIClient(Protocol):
    async def recommend(self, recipes: list[Recipe]) -> AIRecommendation: ...

class FallbackAIClient:
    async def recommend(self, recipes: list[Recipe]) -> AIRecommendation:
        if not recipes:
            return AIRecommendation(None, "No recipes yet", "Create a few recipes first, then I can recommend one.")
        pick = recipes[0]
        return AIRecommendation(pick.id, pick.title, "Fallback: returning the most recent recipe.")

class AnthropicAIClient:
    def __init__(self, api_key: str, model: str | None = None):
        self.api_key = api_key
        self.model = model or settings.anthropic_model

    async def recommend(self, recipes: list[Recipe]) -> AIRecommendation:
        if not recipes:
            return AIRecommendation(None, "No recipes yet", "Add some recipes and I will recommend one based on them.")

        # mandamos contexto mínimo
        context = [{"id": r.id, "title": r.title, "description": r.description} for r in recipes[:25]]

        system = (
            "You are a helpful cooking assistant. "
            "Pick ONE best recipe to recommend from the provided list. "
            "Return strict JSON with keys: recommended_id (int), title (str), reason (str)."
        )
        user = f"Recipes:\n{json.dumps(context)}"

        payload = {
            "model": self.model,
            "max_tokens": 200,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()

        # Anthropic devuelve content como lista; juntamos texto
        text = "".join(part.get("text", "") for part in data.get("content", [])).strip()
        try:
            obj = json.loads(text)
            return AIRecommendation(
                recommended_id=int(obj["recommended_id"]),
                title=str(obj["title"]),
                reason=str(obj["reason"]),
            )
        except Exception:
            # fallback si el modelo no devolvió JSON limpio
            pick = recipes[0]
            return AIRecommendation(pick.id, pick.title, "AI parsing failed, fallback to most recent recipe.")

def build_ai_client() -> AIClient:
    if settings.anthropic_api_key:
        return AnthropicAIClient(settings.anthropic_api_key)
    return FallbackAIClient()
