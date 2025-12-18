import pytest
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.main import app
from app.db.models import Base
from app.db.session import get_session
import app.api.graphql as graphql_module
import app.db.session as db_session_module

# Fixture to create a test database engine
@pytest.fixture
async def test_engine(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()

# Fixture to create a session maker for tests
@pytest.fixture
def session_maker(test_engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


# Fixture to create a test FastAPI app with overridden dependencies
@pytest.fixture
def test_app(session_maker, monkeypatch):
    async def override_get_session():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    # Patch the session maker in the db session and graphql modules
    monkeypatch.setattr(db_session_module, "SessionLocal", session_maker)
    monkeypatch.setattr(graphql_module, "SessionLocal", session_maker)

    try:
        yield app
    finally:
        app.dependency_overrides.clear()
