"""
Bootstrap script — creates all tables directly via SQLAlchemy metadata.
Use this instead of `alembic upgrade head` for the initial setup.
After running, Alembic is stamped at head so future migrations work normally.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import create_async_engine
import app.models  # noqa: F401 — registers all models on Base.metadata
from app.database import Base
from app.config import settings


async def create_schema():
    engine = create_async_engine(settings.async_database_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("\nAll tables created successfully.")


if __name__ == "__main__":
    asyncio.run(create_schema())
