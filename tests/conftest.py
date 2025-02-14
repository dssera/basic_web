"""
    fixtures for the whole project.
    DON'T SAVE TESTS HERE - only fixtures
"""
import asyncio

import pytest
import pytest_asyncio

from sqlalchemy.sql.ddl import DropTable

from app.config import settings
from app.db import AsyncSessionLocal, Base, async_engine


# @pytest_asyncio.fixture(scope="class", autouse=True)
# def event_loop_instance(request):
#     """ Add the event_loop as an attribute to the unittest style test class. """
#     request.cls.event_loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield
#     request.cls.event_loop.close()

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    assert settings.MODE == "TEST"
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(DropTable(table, if_exists=True))
            await session.commit()

        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # yield
        #
        # async with session.begin():
        #     for table in reversed(Base.metadata.sorted_tables):
        #         await session.execute(DropTable(table, if_exists=True))
        #     await session.commit()
