from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.db.repo import RecipeRepo
from app.services.recipes import RecipeService
from app.domain.schemas import RecipeCreate, RecipeOut, RecommendationOut

router = APIRouter(prefix="/recipes", tags=["recipes"])

def get_service(session: AsyncSession = Depends(get_session)) -> RecipeService:
    return RecipeService(RecipeRepo(session))

@router.post("", response_model=RecipeOut, status_code=201)
async def create_recipe(payload: RecipeCreate, svc: RecipeService = Depends(get_service)):
    return await svc.create_recipe(payload)

@router.get("", response_model=list[RecipeOut])
async def list_recipes(svc: RecipeService = Depends(get_service)):
    return await svc.list_recipes()

@router.delete("/{recipe_id}", status_code=204)
async def delete_recipe(recipe_id: int, svc: RecipeService = Depends(get_service)):
    ok = await svc.delete_recipe(recipe_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return None

@router.get("/recommendation", response_model=RecommendationOut)
async def recommend_recipe(svc: RecipeService = Depends(get_service)):
    rec = await svc.recommend()
    return RecommendationOut(recommended_id=rec.recommended_id, title=rec.title, reason=rec.reason)
