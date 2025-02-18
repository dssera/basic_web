import traceback

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import BuildingRepository, ActivityRepository, OrganizationRepository, UserRepository
from app.db import AsyncSessionLocal


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._building_repository = None
        self._activity_repository = None
        self._organization_repository = None
        self._user_repository = None

    @property
    def building_repository(self):
        if self._building_repository is None:
            self._building_repository = BuildingRepository(self.session)
        return self._building_repository

    @property
    def activity_repository(self):
        if self._activity_repository is None:
            self._activity_repository = ActivityRepository(self.session)
        return self._activity_repository

    @property
    def organization_repository(self):
        if self._organization_repository is None:
            self._organization_repository = OrganizationRepository(self.session)
        return self._organization_repository

    @property
    def user_repository(self):
        if self._user_repository is None:
            self._user_repository = UserRepository(self.session)
        return self._user_repository

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        await self.session.close()


@asynccontextmanager
async def unit_of_work():
    session = AsyncSessionLocal()
    uow = UnitOfWork(session)
    try:
        yield uow
        await uow.commit()
    except Exception as e:
        await uow.rollback()
        print(f"ValidationError: {e}")
        print(traceback.format_exc())
        raise
    finally:
        await uow.close()
