from dataclasses import dataclass
from typing import Protocol
from app.db.models import Recipe
from app.core.config import settings
import json
import httpx

# AI recommendation result
@dataclass
class AIRecommendation:
    recommended_id: int | None
    title: str
    reason: str

# AI client interface
class AIClient(Protocol):
    async def recommend(self, recipes: list[Recipe]) -> AIRecommendation: ...

# Fallback AI client if no real AI is configured
class FallbackAIClient:
    async def recommend(self, recipes: list[Recipe]) -> AIRecommendation:
        if not recipes:
            return AIRecommendation(None, "No recipes yet", "Create a few recipes first, then I can recommend one.")
        pick = recipes[0]
        return AIRecommendation(pick.id, pick.title, "Fallback: returning the most recent recipe.")

# Anthropic AI client implementation
class AnthropicAIClient:

    # Constructor with API key and optional model
    def __init__(self, api_key: str, model: str | None = None):
        self.api_key = api_key
        self.model = model or settings.anthropic_model

    # Recommend a recipe using Anthropic API
    async def recommend(self, recipes: list[Recipe]) -> AIRecommendation:
        if not recipes:
            return AIRecommendation(None, "No recipes yet", "Add some recipes and I will recommend one based on them.")

        # Prepare context with up to 25 recipes
        context = [{"id": r.id, "title": r.title, "description": r.description} for r in recipes[:25]]

        # Build the prompt
        system = (
            "You are a helpful cooking assistant. "
            "Pick ONE best recipe to recommend from the provided list. "
            "Return strict JSON with keys: recommended_id (int), title (str), reason (str)."
        )
        # Serialize context as JSON
        user = f"Recipes:\n{json.dumps(context)}"

        # Build the request payload
        payload = {
            "model": self.model,
            "max_tokens": 200,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }

        # Make the API request
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        # Send request to Anthropic API
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()

        # Parse the response, extract text content
        text = "".join(part.get("text", "") for part in data.get("content", [])).strip()
        try:
            obj = json.loads(text)
            return AIRecommendation(
                recommended_id=int(obj["recommended_id"]),
                title=str(obj["title"]),
                reason=str(obj["reason"]),
            )
        except Exception:
            # On failure, fallback to most recent recipe
            pick = recipes[0]
            return AIRecommendation(pick.id, pick.title, "AI parsing failed, fallback to most recent recipe.")

# Factory to build appropriate AI client
def build_ai_client() -> AIClient:
    if settings.anthropic_api_key:
        return AnthropicAIClient(settings.anthropic_api_key)
    return FallbackAIClient()
