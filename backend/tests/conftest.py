import asyncio

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import main
from core.database import Base, get_db
from core.settings import config

TEST_URL = config.db.get_test_url()

test_engine = create_async_engine(TEST_URL, poolclass=NullPool)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSession() as session:
        yield session


@pytest.fixture(scope="session")
def client():
    main.app.dependency_overrides[get_db] = override_get_db
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def migrated_db():
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", TEST_URL)
    command.upgrade(alembic_config, "head")


@pytest.fixture(scope="session", autouse=True)
def clean_db(migrated_db):
    async def _truncate():
        async with TestSession() as s:
            tables = ", ".join(t.name for t in Base.metadata.sorted_tables)
            await s.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))
            await s.commit()

    asyncio.run(_truncate())
    yield


@pytest.fixture(autouse=True)
def no_email(monkeypatch):
    from src.core.email_message import (  # ty: ignore[unresolved-import]
        send_email_message,
    )

    monkeypatch.setattr(send_email_message, "delay", lambda *a, **k: None)
