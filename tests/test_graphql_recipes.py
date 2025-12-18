import pytest
import httpx
import app.services.recipes as recipes_module
from app.services import ai as ai_module


def gql(query: str, variables: dict | None = None) -> dict:
    payload = {"query": query}
    if variables is not None:
        payload["variables"] = variables
    return payload

# Fake AI client for testing purposes
class FakeAIClient:
    async def recommend(self, recipes):
        if not recipes:
            return ai_module.AIRecommendation(
                recommended_id=None,
                title="No recipes yet",
                reason="Add a few recipes first.",
            )
        pick = recipes[0]
        return ai_module.AIRecommendation(
            recommended_id=pick.id,
            title=pick.title,
            reason="Mocked AI recommendation for GraphQL testing.",
        )

# Tests for GraphQL API
@pytest.mark.anyio
async def test_graphql_create_and_list(test_app):
    transport = httpx.ASGITransport(app=test_app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create via mutation
        q = """
        mutation CreateRecipe($title: String!, $description: String) {
          createRecipe(title: $title, description: $description) {
            id
            title
            description
            createdAt
          }
        }
        """
        r = await client.post(
            "/graphql",
            json=gql(q, {"title": "Burger", "description": "Juicy burger"}),
        )
        assert r.status_code == 200
        body = r.json()
        assert "errors" not in body
        created = body["data"]["createRecipe"]
        assert int(created["id"]) > 0
        assert created["title"] == "Burger"
        assert created["description"] == "Juicy burger"
        assert created["createdAt"]

        # List via query
        q = """
        query {
          recipes {
            id
            title
            description
            createdAt
          }
        }
        """
        r = await client.post("/graphql", json=gql(q))
        assert r.status_code == 200
        body = r.json()
        assert "errors" not in body
        items = body["data"]["recipes"]
        assert isinstance(items, list)
        assert len(items) == 1
        assert items[0]["title"] == "Burger"


@pytest.mark.anyio
async def test_graphql_delete_recipe(test_app):
    transport = httpx.ASGITransport(app=test_app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create first
        create_q = """
        mutation {
          createRecipe(title: "Tacos", description: "Street tacos") {
            id
          }
        }
        """
        r = await client.post("/graphql", json=gql(create_q))
        recipe_id = int(r.json()["data"]["createRecipe"]["id"])

        # Delete
        delete_q = """
        mutation DeleteRecipe($id: Int!) {
          deleteRecipe(recipeId: $id)
        }
        """
        r = await client.post("/graphql", json=gql(delete_q, {"id": recipe_id}))
        assert r.status_code == 200
        body = r.json()
        assert "errors" not in body
        assert body["data"]["deleteRecipe"] is True

        # Delete again, false
        r = await client.post("/graphql", json=gql(delete_q, {"id": recipe_id}))
        assert r.status_code == 200
        body = r.json()
        assert "errors" not in body
        assert body["data"]["deleteRecipe"] is False


@pytest.mark.anyio
async def test_graphql_recommendation_is_mocked(test_app, monkeypatch):
    # Patch where RecipeService uses it
    monkeypatch.setattr(recipes_module, "build_ai_client", lambda: FakeAIClient())

    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create some recipes
        await client.post("/recipes", json={"title": "Pizza"})
        await client.post("/recipes", json={"title": "Soup"})

        q = """
        query {
          recommendRecipe {
            recommendedId
            title
            reason
          }
        }
        """
        r = await client.post("/graphql", json=gql(q))
        assert r.status_code == 200
        body = r.json()
        assert "errors" not in body

        rec = body["data"]["recommendRecipe"]
        assert rec["recommendedId"] is not None
        assert rec["title"] in {"Pizza", "Soup"}
        assert rec["reason"] == "Mocked AI recommendation for GraphQL testing."
