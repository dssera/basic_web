import traceback
from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.repositories import BuildingRepository, ActivityRepository, OrganizationRepository
from app.db import SessionLocal


class UnitOfWork:
    def __init__(self, session: Session):
        self.session = session
        self._building_repository = None
        self._activity_repository = None
        self._organization_repository = None

    # create repo only if need
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

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()


@contextmanager
def unit_of_work():
    session = SessionLocal()
    uow = UnitOfWork(session)
    try:
        yield uow
        uow.commit()
    except Exception as e:
        uow.rollback()
        print(f"ValidationError: {e}")
        print(traceback.format_exc())
        raise
    finally:
        uow.close()
