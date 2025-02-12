import pytest

from sqlalchemy import delete

from app.models import Building, OrganizationActivity, Activity, PhoneNumber, Organization
from app.db import AsyncSessionLocal


@pytest.fixture(scope='function')
async def fill_buildings():
    async with AsyncSessionLocal() as session:
        try:
            building1 = Building(
                city="Minsk",
                street="Nezavisimosti Ave",
                house="1",
                latitude=53.9023,
                longitude=27.5619
            )
            building2 = Building(
                city="Homyel",
                street="Sovetskaya St",
                house="2",
                latitude=52.4252,
                longitude=30.9754
            )
            building3 = Building(
                city="Vitebsk",
                street="Lenina St",
                house="3",
                latitude=55.1938,
                longitude=30.2033
            )
            session.add_all((building1, building2, building3))
            await session.flush()

            organization1 = Organization(
                name="Org 1",
                building_id=building1.id
            )
            organization2 = Organization(
                name="Org 2",
                building_id=building2.id
            )
            session.add_all((organization1, organization2))
            await session.flush()

            phone_number1 = PhoneNumber(
                phone_number="123456789",
                organization_id=organization1.id
            )
            phone_number2 = PhoneNumber(
                phone_number="987654321",
                organization_id=organization2.id
            )
            session.add_all((phone_number1, phone_number2))
            await session.flush()

            activity1 = Activity(name="Eat")
            session.add(activity1)
            await session.flush()
            activity2 = Activity(name="Milk", parent_id=activity1.id)
            activity3 = Activity(name="Meat", parent_id=activity1.id)
            session.add(activity3)
            await session.flush()
            activity4 = Activity(name="Sausages", parent_id=activity3.id)
            session.add_all((activity2, activity4))
            await session.flush()

            organization_activity1 = OrganizationActivity(
                organization_id=organization1.id,
                activity_id=activity1.id
            )
            organization_activity2 = OrganizationActivity(
                organization_id=organization2.id,
                activity_id=activity2.id
            )
            session.add_all((organization_activity1, organization_activity2))

            await session.commit()
        finally:
            await session.close()



@pytest.fixture(
    scope='function'
)
async def empty_buildings():
    async with AsyncSessionLocal() as session:
        try:
            query = delete(Building)
            await session.execute(query)
            await session.commit()
        finally:
            await session.close()
