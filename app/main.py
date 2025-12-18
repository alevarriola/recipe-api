from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.rest import router as recipes_router
from app.api.graphql import graphql_app
from app.db.session import engine
from app.db.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(title="Recipe API", lifespan=lifespan)

app.include_router(recipes_router)
app.include_router(graphql_app, prefix="/graphql")
