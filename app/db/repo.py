from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Recipe

# Recipe repository
class RecipeRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    # Create a new recipe
    async def create(self, title: str, description: str | None) -> Recipe:
        recipe = Recipe(title=title, description=description)
        self.session.add(recipe)
        await self.session.commit()
        await self.session.refresh(recipe)
        return recipe

    # List all recipes
    async def list_all(self) -> list[Recipe]:
        res = await self.session.execute(
            select(Recipe).order_by(Recipe.created_at.desc())
        )
        return list(res.scalars().all())

    # Delete a recipe by ID
    async def delete(self, recipe_id: int) -> bool:
        res = await self.session.execute(
            delete(Recipe).where(Recipe.id == recipe_id)
        )
        await self.session.commit()
        return (res.rowcount or 0) > 0
