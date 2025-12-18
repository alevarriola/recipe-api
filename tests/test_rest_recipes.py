import pytest
import httpx


@pytest.mark.anyio
async def test_create_and_list_recipes(test_app):
    transport = httpx.ASGITransport(app=test_app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create
        r = await client.post("/recipes", json={"title": "Pasta", "description": "Simple pasta"})
        assert r.status_code == 201
        data = r.json()
        assert data["id"] > 0
        assert data["title"] == "Pasta"
        assert data["description"] == "Simple pasta"
        assert "created_at" in data

        # List
        r = await client.get("/recipes")
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        assert len(items) == 1
        assert items[0]["title"] == "Pasta"


@pytest.mark.anyio
async def test_delete_recipe(test_app):
    transport = httpx.ASGITransport(app=test_app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Create
        r = await client.post("/recipes", json={"title": "Salad"})
        recipe_id = r.json()["id"]

        # Delete
        r = await client.delete(f"/recipes/{recipe_id}")
        assert r.status_code == 204

        # Delete again -> 404
        r = await client.delete(f"/recipes/{recipe_id}")
        assert r.status_code == 404
