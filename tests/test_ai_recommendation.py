import pytest
import httpx
import app.services.recipes as recipes_module
from app.services import ai as ai_module

# Fake AI client for testing purposes
class FakeAIClient:
    async def recommend(self, recipes):
        if not recipes:
            return ai_module.AIRecommendation(
                recommended_id=None,
                title="No recipes yet",
                reason="Add a few recipes first.",
            )
        pick = recipes[0]  # just pick the first one
        return ai_module.AIRecommendation(
            recommended_id=pick.id,
            title=pick.title,
            reason="Mocked AI recommendation for testing.",
        )


@pytest.mark.anyio 
async def test_recommendation_is_mocked(test_app, monkeypatch):
    # Patch the AI client to use the fake one
    monkeypatch.setattr(recipes_module, "build_ai_client", lambda: FakeAIClient())

    # Create some recipes and test recommendation
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post("/recipes", json={"title": "Pizza"})
        await client.post("/recipes", json={"title": "Soup"})

        r = await client.get("/recipes/recommendation")
        assert r.status_code == 200
        data = r.json()

        assert data["recommended_id"] is not None
        assert data["title"] in {"Pizza", "Soup"}
        assert data["reason"] == "Mocked AI recommendation for testing."
