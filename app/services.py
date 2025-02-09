from geopy import Nominatim
from geopy.adapters import AioHTTPAdapter
from geopy.distance import distance

from .uow import unit_of_work


class BuildingService:

    async def get_by_coordinates(self, latitude: float, longitude: float, r: float):
        # shitty method name btw: get_buildings_with_organizations_by_coordinates
        async with unit_of_work() as uow:
            city = await GeoUtils.find_city_by_coordinates(latitude, longitude)
            if not city:
                return None
            buildings = await uow.building_repository.get_buildings_by_city(city)
            result_list = []
            for b in buildings:
                if GeoUtils.is_within_radius(latitude, longitude, b.latitude, b.longitude, r):
                    building_dict = b.model_dump()
                    building_dict["organizations"] = (
                        await uow.organization_repository.get_organizations_by_building_address(b.city, b.street,
                                                                                                b.house))
                    result_list.append(building_dict)
            return result_list


class OrganizationService:

    async def get_organizations_by_building_address(
            self,
            city: str,
            street: str,
            house: str
    ):
        async with unit_of_work() as uow:
            return await uow.organization_repository.get_organizations_by_building_address(city, street, house)

    async def get_organizations_by_activity(self, activity: str):
        async with unit_of_work() as uow:
            return await uow.organization_repository.get_organizations_by_activity(activity)

    async def get_organization_by_id(self, organization_id: int):
        async with unit_of_work() as uow:
            return await uow.organization_repository.get_organization_by_id(organization_id)

    async def get_organization_by_name(self, name: str):
        async with unit_of_work() as uow:
            return await uow.organization_repository.get_organization_by_name(name)

    async def get_organizations_by_subactivities(self, activity: str):
        async with unit_of_work() as uow:
            subactivities = await uow.activity_repository.get_all_subactivities(activity)
            return await uow.organization_repository.find_organizations_by_activity(activity, subactivities)


class GeoUtils:

    @staticmethod
    def is_within_radius(
            input_point_latitude,
            input_point_longitude,
            obj_latitude,
            obj_longitude,
            radius_km
    ):
        # calculate the distance between the input central point and the obj coordinates
        distance_km = distance((input_point_latitude, input_point_longitude),
                               (obj_latitude, obj_longitude)).km
        return distance_km <= radius_km

    @staticmethod
    async def find_city_by_coordinates(latitude: float, longitude: float):
        async with Nominatim(user_agent="companies_app",
                             adapter_factory=AioHTTPAdapter) as geolocator:
            location = await geolocator.reverse(
                (latitude, longitude), exactly_one=True)
            if not location:
                return None
            address = location.raw['address']
            city = address.get('city', '')
            return city
