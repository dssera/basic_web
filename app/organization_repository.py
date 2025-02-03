import traceback
from typing import List

from pydantic_core import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from . import models, schemas
from app.db import SessionLocal

# should be splited into separated repos
class OrganizationRepository:
    """
        В методах создается объект сессии, что есть плохо, т к это не
        ответственность репы. Решается с помощью паттерна UoW
    """

    def __init__(self):
        # will be used later in UoW
        pass

    def get_organizations_by_building_address(
            self,
            city: str,
            street: str,
            house: str,
    ) -> List[schemas.Organization] | None:
        # мапим тут чтобы бизнес слой(services)
        # не видел сущности dao(models.Organization)
        try:
            session: Session = SessionLocal()
            try:
                organizations = (session.query(models.Organization)
                                 .join(models.Organization.building)
                                 .filter((models.Building.city == city) &
                                         (models.Building.street == street) &
                                         (models.Building.house == house))
                                 .all())
                return [schemas.Organization.model_validate(org) for
                        org in organizations]
            finally:
                session.close()
        except ValidationError as e:
            print(f"ValidationError: {e}")
            print(traceback.format_exc())

    def get_organizations_by_activity(
            self,
            activity: str
    ) -> List[schemas.Organization] | None:
        try:
            session: Session = SessionLocal()
            try:
                organizations = (session.query(models.Organization)
                                 .join(models.Organization.activities)
                                 .filter(models.Activity.name == activity))
                return [schemas.Organization.model_validate(org) for
                        org in organizations]
            finally:
                session.close()
        except ValidationError as e:
            print(f"ValidationError: {e}")
            print(traceback.format_exc())

    def get_organization_by_id(
            self,
            organization_id: int
    ) -> schemas.Organization | None:
        try:
            session: Session = SessionLocal()
            try:
                org = (session.query(models.Organization)
                       .filter(models.Organization.id == organization_id)
                       .first())
                return schemas.Organization.model_validate(org)
            finally:
                session.close()
        except ValidationError as e:
            print(f"ValidationError: {e}")
            print(traceback.format_exc())

    def get_organization_by_name(
            self,
            name: str
    ) -> schemas.Organization | None:
        try:
            session: Session = SessionLocal()
            try:
                org = (session.query(models.Organization)
                       .filter(models.Organization.name == name)
                       .first())
                return schemas.Organization.model_validate(org)
            finally:
                session.close()
        except ValidationError as e:
            print(f"ValidationError: {e}")
            print(traceback.format_exc())

    def get_buildings_by_city(
            self,
            city: str
    ):
        try:
            session: Session = SessionLocal()
            try:
                buildings = (session.query(models.Building)
                             .filter(models.Building.city == city))
                return [schemas.Building.model_validate(building) for building in buildings]
            finally:
                session.close()
        except ValidationError as e:
            print(f"ValidationError: {e}")
            print(traceback.format_exc())
        except SQLAlchemyError as e:
            print(f"SQLAlchemyError: {e}")
            print(traceback.format_exc())
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print(traceback.format_exc())

    def get_all_subactivities(
            self,
            activity_name,
            session,
            depth=0,
            max_depth=3
    ):
        activity = session.query(models.Activity).filter_by(name=activity_name).first()
        if not activity or depth > max_depth:
            return []
        subactivities = []
        for child in activity.children:
            subactivities.append(child)
            subactivities.extend(self.get_all_subactivities(child.name, session, depth + 1, max_depth))
        return subactivities

    def find_organizations_by_activity(self, activity_name):
        try:
            session = SessionLocal()
            try:
                all_activities = (self.get_all_subactivities(activity_name, session) +
                                  [session.query(models.Activity)
                                  .filter_by(name=activity_name)
                                  .first()])
                organizations = set()
                for act in all_activities:
                    if act:
                        organizations.update(act.organizations)
                session.close()
                return [schemas.Organization.model_validate(org) for org in organizations]
            finally:
                session.close()
        except ValidationError as e:
            print(f"ValidationError: {e}")
            print(traceback.format_exc())
        except SQLAlchemyError as e:
            print(f"SQLAlchemyError: {e}")
            print(traceback.format_exc())
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            print(traceback.format_exc())
