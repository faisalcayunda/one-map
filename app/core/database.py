import asyncio
import os
import sys

from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import os
import sys

from app.core.config import settings
from app.models import Base

engine = create_async_engine(settings.DATABASE_URL, echo=True)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
