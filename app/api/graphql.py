import strawberry
from strawberry.fastapi import GraphQLRouter

from app.db.repo import RecipeRepo
from app.services.recipes import RecipeService
from app.domain.schemas import RecipeCreate
from app.db.session import SessionLocal


@strawberry.type
class RecipeGQL:
    id: int
    title: str
    description: str | None
    created_at: str = strawberry.field(name="createdAt")


@strawberry.type
class RecommendationGQL:
    recommended_id: int | None = strawberry.field(name="recommendedId")
    title: str
    reason: str


async def with_service(fn):
    async with SessionLocal() as session:
        svc = RecipeService(RecipeRepo(session))
        return await fn(svc)


@strawberry.type
class Query:
    @strawberry.field
    async def recipes(self) -> list[RecipeGQL]:
        async def run(svc: RecipeService):
            items = await svc.list_recipes()
            return [
                RecipeGQL(
                    id=r.id,
                    title=r.title,
                    description=r.description,
                    created_at=r.created_at.isoformat(),
                )
                for r in items
            ]
        return await with_service(run)

    @strawberry.field(name="recommendRecipe")
    async def recommend_recipe(self) -> RecommendationGQL:
        async def run(svc: RecipeService):
            rec = await svc.recommend()
            return RecommendationGQL(
                recommended_id=rec.recommended_id,
                title=rec.title,
                reason=rec.reason,
            )
        return await with_service(run)


@strawberry.type
class Mutation:
    @strawberry.mutation(name="createRecipe")
    async def create_recipe(self, title: str, description: str | None = None) -> RecipeGQL:
        async def run(svc: RecipeService):
            r = await svc.create_recipe(RecipeCreate(title=title, description=description))
            return RecipeGQL(
                id=r.id,
                title=r.title,
                description=r.description,
                created_at=r.created_at.isoformat(),
            )
        return await with_service(run)

    @strawberry.mutation(name="deleteRecipe")
    async def delete_recipe(self, recipe_id: int) -> bool:
        async def run(svc: RecipeService):
            return await svc.delete_recipe(recipe_id)
        return await with_service(run)


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)