from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db() -> Iterator[Session]:
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # Без `with`, чтобы lifespan не создавал файл todo.db
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def make_user(client: TestClient) -> Callable[..., dict[str, str]]:
    """Регистрирует пользователя и возвращает заголовки авторизации."""

    def _make(username: str = "alice", password: str = "secret123") -> dict[str, str]:
        r = client.post("/auth/register", json={"username": username, "password": password})
        assert r.status_code == 201, r.text
        r = client.post("/auth/login", data={"username": username, "password": password})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    return _make


@pytest.fixture
def auth(make_user: Callable[..., dict[str, str]]) -> dict[str, str]:
    return make_user()
