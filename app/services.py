from typing import List, Dict

from geopy import Nominatim
from geopy.adapters import AioHTTPAdapter
from geopy.distance import distance

from . import schemas
from .uow import unit_of_work


class BuildingService:

    async def get_buildings_with_organizations_by_coordinates(
            self,
            latitude: float,
            longitude: float,
            r: float
    ) -> List[Dict]:
        GeoUtils.validate_coordinates(latitude, longitude, r)
        async with unit_of_work() as uow:
            city = await GeoUtils.find_city_by_coordinates(latitude, longitude)
            if not city:
                raise ValueError(f"No city found for coordinates: {latitude}, {longitude}")

            buildings = await uow.building_repository.get_buildings_by_city(city)
            buildings_with_their_organizations = []

            for b in buildings:
                if GeoUtils.is_within_radius(latitude, longitude, b.latitude, b.longitude, r):
                    building_dict = b.model_dump()
                    building_dict["organizations"] = (
                        await uow.organization_repository.get_organizations_by_building_address(
                            b.city, b.street, b.house)
                    )
                    buildings_with_their_organizations.append(building_dict)
            return buildings_with_their_organizations


class OrganizationService:

    async def get_organizations_by_building_address(
            self,
            city: str,
            street: str,
            house: str
    ) -> List[schemas.Organization]:
        self.validate_address(city, street, house)
        async with unit_of_work() as uow:
            return await uow.organization_repository.get_organizations_by_building_address(city, street, house)

    async def get_organizations_by_activity(
            self,
            activity: str
    ) -> List[schemas.Organization]:
        self.validate_activity(activity)
        async with unit_of_work() as uow:
            return await uow.organization_repository.get_organizations_by_activity(activity)

    async def get_organization_by_id(
            self,
            organization_id: int
    ) -> schemas.Organization:
        self.validate_id(organization_id)
        async with unit_of_work() as uow:
            return await uow.organization_repository.get_organization_by_id(organization_id)

    async def get_organization_by_name(
            self,
            name: str
    ) -> schemas.Organization:
        self.validate_name(name)
        async with unit_of_work() as uow:
            return await uow.organization_repository.get_organization_by_name(name)

    async def get_organizations_by_subactivities(
            self,
            activity: str
    ) -> List[schemas.Organization]:
        self.validate_activity(activity)
        async with unit_of_work() as uow:
            subactivities = await uow.activity_repository.get_all_subactivities(activity)
            return await uow.organization_repository.find_organizations_by_activity(activity, subactivities)

    @staticmethod
    def validate_address(city: str, street: str, house: str):
        if not all(isinstance(arg, str) and arg for arg in [city, street, house]):
            raise ValueError("Invalid address. City, street, and house must be non-empty strings.")

    @staticmethod
    def validate_activity(activity: str):
        if not isinstance(activity, str) or not activity:
            raise ValueError("Invalid activity. Activity must be a non-empty string.")

    @staticmethod
    def validate_id(organization_id: int):
        if not isinstance(organization_id, int) or organization_id <= 0:
            raise ValueError("Invalid organization ID. ID must be a positive integer.")

    @staticmethod
    def validate_name(name: str):
        if not isinstance(name, str) or not name:
            raise ValueError("Invalid organization name. Name must be a non-empty string.")


class GeoUtils:

    @classmethod
    def is_within_radius(
            cls,
            input_point_latitude,
            input_point_longitude,
            obj_latitude,
            obj_longitude,
            radius_km
    ):
        cls.validate_coordinates(input_point_latitude, input_point_longitude, radius_km)
        cls.validate_coordinates(obj_latitude, obj_longitude, radius_km)

        # calculate the distance between the input central point and the obj coordinates
        distance_km = distance((input_point_latitude, input_point_longitude),
                               (obj_latitude, obj_longitude)).km
        return distance_km <= radius_km

    @classmethod
    async def find_city_by_coordinates(cls, latitude: float, longitude: float):
        cls.validate_coordinates(latitude, longitude)

        async with Nominatim(user_agent="companies_app",
                             adapter_factory=AioHTTPAdapter) as geolocator:
            location = await geolocator.reverse(
                (latitude, longitude), exactly_one=True)
            if not location:
                return None
            address = location.raw['address']
            city = address.get('city', '')
            return city

    @staticmethod
    def validate_coordinates(
            latitude: float,
            longitude: float,
            r: float = None
    ):
        if not isinstance(latitude, (float, int)) or not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude value: {latitude}. Latitude must be between -90 and 90.")
        if not isinstance(longitude, (float, int)) or not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude value: {longitude}. Longitude must be between -180 and 180.")
        if r is not None and (not isinstance(r, (float, int)) or not (0.05 <= r <= 15)):
            raise ValueError(f"Invalid radius value: {r}. Radius must be between 0.05 km and 15 km.")
