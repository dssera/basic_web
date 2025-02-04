from geopy import Nominatim
from geopy.distance import distance

from .repositories import OrganizationRepository, BuildingRepository, ActivityRepository


class BuildingService:
    def __init__(self,
                 building_repo: BuildingRepository,
                 organization_repo: OrganizationRepository):
        self.building_repo = building_repo
        self.organization_repo = organization_repo

    def get_by_coordinates(self, latitude: float, longitude: float, r: float):
        # shitty method name btw: get_buildings_with_organizations_by_coordinates
        city = GeoUtils.find_city_by_coordinates(latitude, longitude)
        if not city:
            return None
        buildings = self.building_repo.get_buildings_by_city(city)
        result_list = []
        for b in buildings:
            if GeoUtils.is_within_radius(latitude, longitude, b.latitude, b.longitude, r):
                building_dict = b.model_dump()
                building_dict["organizations"] = (
                    self.organization_repo.get_organizations_by_building_address(b.city, b.street, b.house))
                result_list.append(building_dict)
        return result_list


class OrganizationService:

    def __init__(self, organization_repo: OrganizationRepository,
                 activity_repo: ActivityRepository):
        self.organization_repo = organization_repo
        self.activity_repo = activity_repo

    def get_organizations_by_building_address(
            self,
            city: str,
            street: str,
            house: str
    ):
        return self.organization_repo.get_organizations_by_building_address(city, street, house)

    def get_organizations_by_activity(self, activity: str):
        return self.organization_repo.get_organizations_by_activity(activity)

    def get_organization_by_id(self, organization_id: int):
        return self.organization_repo.get_organization_by_id(organization_id)

    def get_organization_by_name(self, name: str):
        return self.organization_repo.get_organization_by_name(name)

    def get_organizations_by_subactivities(self, activity: str):
        subactivities = self.activity_repo.get_all_subactivities(activity)
        return self.organization_repo.find_organizations_by_activity(activity, subactivities)


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
    def find_city_by_coordinates(latitude: float, longitude: float):
        geolocator = Nominatim(user_agent="companies_app")
        location = geolocator.reverse(
            (latitude, longitude), exactly_one=True)
        if not location:
            return None
        address = location.raw['address']
        city = address.get('city', '')
        return city
