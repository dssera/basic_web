from typing import List

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas


class BuildingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_buildings_by_city(
            self,
            city: str
    ):
        query = (select(models.Building)
                 .filter(models.Building.city == city))
        result = await self.session.execute(query)
        buildings = result.scalars().all()

        return [schemas.Building.model_validate(building) for building in buildings]


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_subactivities(
            self,
            activity_name,
            depth=0,
            max_depth=3
    ) -> list[schemas.Activity]:
        query = select(models.Activity).filter_by(name=activity_name)
        result = await self.session.execute(query)
        activity = result.scalar()
        if not activity or depth > max_depth:
            return []
        subactivities = []
        for child in activity.children:
            subactivities.append(child)
            subactivities.extend(
                await self.get_all_subactivities(child.name, depth + 1, max_depth)
            )
        return [schemas.Activity.model_validate(act) for
                act in subactivities]


class OrganizationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_organizations_by_building_address(
            self,
            city: str,
            street: str,
            house: str,
    ) -> List[schemas.Organization] | None:
        query = (select(models.Organization)
                 .options(joinedload(models.Organization.phone_numbers))
                 .options(joinedload(models.Organization.building))
                 .filter((models.Building.city == city) &
                         (models.Building.street == street) &
                         (models.Building.house == house)))
        result = (await self.session.execute(query)).unique()
        organizations = result.scalars().all()
        return [schemas.Organization.model_validate(org) for
                org in organizations]

    async def get_organizations_by_activity(
            self,
            activity: str
    ) -> List[schemas.Organization] | None:
        query = (
            select(models.Organization)
            .options(joinedload(models.Organization.activities))
            .options(joinedload(models.Organization.phone_numbers))
            .filter(models.Activity.name == activity)
        )
        result = (await self.session.execute(query)).unique()
        organizations = result.scalars().all()
        return [schemas.Organization.model_validate(org) for
                org in organizations]

    async def get_organization_by_id(
            self,
            organization_id: int
    ) -> schemas.Organization | None:
        query = (
            select(models.Organization)
            .options(joinedload(models.Organization.phone_numbers))
            .options(joinedload(models.Organization.building))
            .filter(models.Organization.id == organization_id)
        )
        result = await self.session.execute(query)
        organization = result.unique().scalars().first()

        return schemas.Organization.model_validate(organization) if organization else None

    async def get_organization_by_name(
            self,
            name: str
    ) -> schemas.Organization | None:
        query = (select(models.Organization)
                 .options(joinedload(models.Organization.phone_numbers))
                 .filter(models.Organization.name == name))
        result = await self.session.execute(query)
        org = result.scalar()
        return schemas.Organization.model_validate(org) if org else None

    async def find_organizations_by_activity(self, activity_name, subactivities: list[schemas.Activity]):
        query = select().filter_by(name=activity_name)
        result = await self.session.execute(query)
        all_activities = result.scalars().all()
        all_activities += subactivities
        organizations = set()
        for act in all_activities:
            if act:
                organizations.update(act.organizations)
        return [schemas.Organization.model_validate(org) for org in organizations]
