from app.db.repo import RecipeRepo
from app.domain.schemas import RecipeCreate
from app.services.ai import AIClient, build_ai_client, AIRecommendation

class RecipeService:
    def __init__(self, repo: RecipeRepo, ai: AIClient | None = None):
        self.repo = repo
        self.ai = ai or build_ai_client()

    async def create_recipe(self, data: RecipeCreate):
        return await self.repo.create(title=data.title, description=data.description)

    async def list_recipes(self):
        return await self.repo.list_all()

    async def delete_recipe(self, recipe_id: int) -> bool:
        return await self.repo.delete(recipe_id)

    async def recommend(self):
        recipes = await self.repo.list_all()
        return await self.ai.recommend(recipes)

