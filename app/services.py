from geopy import Nominatim
from geopy.distance import distance

from .organization_repository import OrganizationRepository


class OrganizationService:

    # must depend on abs class actually
    def __init__(self, organization_repo: OrganizationRepository):
        self.repo = organization_repo

    def get_organizations_by_building_address(
            self,
            city: str,
            street: str,
            house: str
    ):
        return self.repo.get_organizations_by_building_address(city, street, house)

    def get_organizations_by_activity(self, activity: str):
        return self.repo.get_organizations_by_activity(activity)

    def is_within_radius(
            self,
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

    def find_city_by_coordinates(self, latitude: float, longitude: float):
        geolocator = Nominatim(user_agent="companies_app")
        location = geolocator.reverse(
            (latitude, longitude), exactly_one=True)
        if not location:
            return None
        address = location.raw['address']
        city = address.get('city', '')
        return city

    def get_by_coordinates(self, latitude: float, longitude: float, r: float):
        city = self.find_city_by_coordinates(latitude, longitude)
        print(city)
        if not city:
            return None
        buildings = self.repo.get_buildings_by_city(city)
        result_list = []
        for b in buildings:
            if self.is_within_radius(latitude, longitude, b.latitude, b.longitude, r):
                building_dict = b.model_dump()
                building_dict["organizations"] = (
                    self.repo.get_organizations_by_building_address(b.city, b.street, b.house))
                result_list.append(building_dict)
        return result_list

    def get_organization_by_id(self, organization_id: int):
        return self.repo.get_organization_by_id(organization_id)

    def get_organization_by_name(self, name: str):
        return self.repo.get_organization_by_name(name)

    def get_organizations_by_subactivities(self, activity: str):
        return self.repo.find_organizations_by_activity(activity)
