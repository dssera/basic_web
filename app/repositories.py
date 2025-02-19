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

    async def __get_all_subactivities(
            self,
            activity_name,
            depth=0,
            max_depth=2
    ) -> list[schemas.Activity]:
        """
            Get all subactivities of given activity (to include first parent activity use .get_all_subactivities())
        """
        query = (select(models.Activity)
                 .options(joinedload(models.Activity.organizations)
                          .joinedload(models.Organization.phone_numbers))
                 .filter_by(name=activity_name))
        result = await self.session.execute(query)
        activity = result.scalar()
        if not activity or depth > max_depth:
            return []
        subactivities = []
        for child in activity.children:
            subactivities.append(child)
            subactivities.extend(
                await self.__get_all_subactivities(child.name, depth + 1, max_depth)
            )
        return [schemas.Activity.model_validate(act) for
                act in subactivities]

    async def get_all_subactivities(
            self,
            activity_name,
            depth=0,
            max_depth=2
    ) -> list[schemas.Activity] | None:
        """
             Uses .__get_all_subactivities() to get all subactivities and add first parent activity
        """
        query = (select(models.Activity)
                 .options(joinedload(models.Activity.organizations)
                          .joinedload(models.Organization.phone_numbers))
                 .filter_by(name=activity_name))
        result = await self.session.execute(query)
        activity = result.scalar()
        if activity:
            subactivities = await self.__get_all_subactivities(activity_name, depth, max_depth)
            subactivities.insert(0, schemas.Activity.model_validate(activity))
            return subactivities
        else:
            return None


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

    # async def find_organizations_by_subactivities(
    #         self, activity_name, subactivities: list[schemas.Activity]
    # ) -> List[schemas.Organization]:
    #     """
    #     Takes activity and its subactivities and returns organizations that are related to these subactivities
    #     (including first parent activity)
    #
    #     :param activity_name:
    #     :param subactivities:
    #     :return:
    #     """
    #     query = (select(models.Activity)
    #              .options(joinedload(models.Activity.organizations)
    #                       .joinedload(models.Organization.phone_numbers))
    #              .filter_by(name=activity_name))
    #     result = await self.session.execute(query)
    #     all_activities = result.unique().scalars().all()
    #     all_activities = [schemas.Activity.model_validate(act) for act in all_activities]
    #     all_activities += subactivities
    #     for act in all_activities:
    #         print(f"all_all_activities({act.__class__}): ", act)
    #
    #     organizations = set()
    #     for act in all_activities:
    #         if act:
    #             for org in act.organizations:
    #                 organizations.add(org.name)
    #     print("set organizations: ", organizations)
    #     return [schemas.Organization.model_validate(org) for org in organizations]

    async def find_organizations_by_subactivities(
            self, activity_name, subactivities: list[schemas.Activity]
    ) -> List[schemas.Organization]:
        """
            Takes activity and its subactivities and returns organizations that are related to these subactivities
            (including first parent activity)
        """
        organizations = []
        for act in subactivities:
            for org in act.organizations:
                if org not in organizations:
                    organizations.append(org)
        return [schemas.Organization.model_validate(org) for org in organizations]


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, username) -> schemas.UserInDb | None:
        print(username)
        # relationships fields required
        query = (select(models.User)
                 .options(joinedload(models.User.permissions))
                 .filter_by(username=username))
        result = await self.session.execute(query)
        user = result.scalar()

        return schemas.UserInDb.model_validate(user) if user else None
        # return schemas.UserInDb(
        #     username="user",
        #     hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
        # )
