from typing import List

from sqlalchemy.orm import Session

from . import models, schemas


class BuildingRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_buildings_by_city(
            self,
            city: str
    ):
        buildings = (self.session.query(models.Building)
                     .filter(models.Building.city == city)
                     .all())
        return [schemas.Building.model_validate(building) for building in buildings]


class ActivityRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all_subactivities(
            self,
            activity_name,
            depth=0,
            max_depth=3
    ) -> list[schemas.Activity]:
        activity = self.session.query(models.Activity).filter_by(name=activity_name).first()
        if not activity or depth > max_depth:
            return []
        subactivities = []
        for child in activity.children:
            subactivities.append(child)
            subactivities.extend(self.get_all_subactivities(child.name, depth + 1, max_depth))
        return [schemas.Activity.model_validate(act) for
                act in subactivities]


class OrganizationRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_organizations_by_building_address(
            self,
            city: str,
            street: str,
            house: str,
    ) -> List[schemas.Organization] | None:
        # мапим тут чтобы бизнес слой(services)
        # не видел сущности dao(models.Organization)
        organizations = (self.session.query(models.Organization)
                         .join(models.Organization.building)
                         .filter((models.Building.city == city) &
                                 (models.Building.street == street) &
                                 (models.Building.house == house))
                         .all())
        return [schemas.Organization.model_validate(org) for
                org in organizations]

    def get_organizations_by_activity(
            self,
            activity: str
    ) -> List[schemas.Organization] | None:
        organizations = (self.session.query(models.Organization)
                         .join(models.Organization.activities)
                         .filter(models.Activity.name == activity)
                         .all())
        return [schemas.Organization.model_validate(org) for
                org in organizations]

    def get_organization_by_id(
            self,
            organization_id: int
    ) -> schemas.Organization | None:
        org = (self.session.query(models.Organization)
               .filter(models.Organization.id == organization_id)
               .first())
        return schemas.Organization.model_validate(org) if org else None

    def get_organization_by_name(
            self,
            name: str
    ) -> schemas.Organization | None:
        org = (self.session.query(models.Organization)
               .filter(models.Organization.name == name)
               .first())
        return schemas.Organization.model_validate(org) if org else None

    def find_organizations_by_activity(self, activity_name, subactivities: list[schemas.Activity]):
        all_activities = (subactivities +
                          [self.session.query(models.Activity)
                          .filter_by(name=activity_name)
                          .first()])
        organizations = set()
        for act in all_activities:
            if act:
                organizations.update(act.organizations)
        return [schemas.Organization.model_validate(org) for org in organizations]
