from datetime import datetime
from pydantic import BaseModel, Field

# Schema for creating a new recipe
class RecipeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None

# Schema for outputting a recipe
class RecipeOut(BaseModel):
    id: int
    title: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

# Schema for AI recommendation output
class RecommendationOut(BaseModel):
    recommended_id: int | None
    title: str
    reason: str
