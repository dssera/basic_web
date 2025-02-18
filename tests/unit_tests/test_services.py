import pytest

from contextlib import nullcontext as does_not_raise

from app.services import BuildingService, OrganizationService, GeoUtils
from app.schemas import Organization


@pytest.mark.usefixtures("empty_buildings", "fill_buildings")
class TestBuildingService:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "latitude, longitude, r, expectation",
        [
            (-181, 181, 3, pytest.raises(ValueError)),
            (90, 180, 4, pytest.raises(ValueError)),
            (90, 180, -4, pytest.raises(ValueError)),
            (90, 180, 90, pytest.raises(ValueError)),
            ("53.9023", 27.5619, 4, pytest.raises(ValueError)),
            (53.9023, 27.5619, 5, does_not_raise()),
            (53.9023, 27.5619, 0.15, does_not_raise()),
        ]
    )
    async def test_get_buildings_with_organizations_by_coordinates(self,
                                                                   latitude: float,
                                                                   longitude: float,
                                                                   r: float,
                                                                   expectation):
        with expectation:
            result = await BuildingService().get_buildings_with_organizations_by_coordinates(
                latitude,
                longitude,
                r)
            assert isinstance(result, list)
            if result:
                first_result = result[0]
                assert "organizations" in first_result
                assert isinstance(first_result["organizations"], list)

                assert first_result["street"] == "Nezavisimosti Ave"
                assert first_result["organizations"][0]["name"] == "Org 1"


@pytest.mark.usefixtures("empty_buildings", "fill_buildings")
class TestOrganizationService:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "city, street, house, expectation",
        [
            (1, "street", "house", pytest.raises(ValueError)),
            ("Minsk", "Nezavisimosti Ave", "1", does_not_raise()),
        ]
    )
    async def test_get_organizations_by_building_address(
            self,
            city: str,
            street: str,
            house: str,
            expectation):
        with expectation:
            result = await OrganizationService().get_organizations_by_building_address(
                city,
                street,
                house)
            if result:
                organization = result[0]
                assert isinstance(organization, Organization)

                assert organization.name == "Org 1"
                assert organization.phone_numbers[0].phone_number == "123456789"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "activity, expectation",
        [
            (1, pytest.raises(ValueError)),
            # dependent by case (fix it))
            ("Eat", does_not_raise()),
        ]
    )
    async def test_get_organizations_by_activity(
            self,
            activity: str,
            expectation):
        with expectation:
            result = await OrganizationService().get_organizations_by_activity(activity)

            if result:
                organization = result[0]
                assert isinstance(organization, Organization)

                assert organization.name == "Org 1"
                assert organization.phone_numbers[0].phone_number == "123456789"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "organization_id, expectation",
        [
            ("third", pytest.raises(ValueError)),
            # dependent by case (fix it))
            (3, does_not_raise()),
        ]
    )
    async def test_get_organization_by_id(
            self,
            organization_id: int,
            expectation):
        with expectation:
            organization = await OrganizationService().get_organization_by_id(organization_id)

            if organization:
                assert isinstance(organization, Organization)

                assert organization.name == "Org 3"
                assert organization.phone_numbers[0].phone_number == "123123123"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "name, expectation",
        [
            (0, pytest.raises(ValueError)),
            ("Org 2", does_not_raise()),
        ]
    )
    async def test_get_organization_by_name(
            self,
            name: str,
            expectation):
        with expectation:
            organization = await OrganizationService().get_organization_by_name(name)

            if organization:
                assert isinstance(organization, Organization)

                assert organization.name == "Org 2"
                assert organization.phone_numbers[0].phone_number == "987654321"

    # @pytest.mark.asyncio
    # @pytest.mark.parametrize(
    #     "activity, expectation",
    #     [
    #         (0, pytest.raises(ValueError)),
    #         ("Eat", does_not_raise()),
    #     ]
    # )
    # async def test_get_organizations_by_subactivities(
    #         self,
    #         activity: str,
    #         expectation):
    #     with expectation:
    #         organizations = await OrganizationService().get_organizations_by_subactivities(activity)
    #
    #         if organizations:
    #             assert isinstance(organizations, list)
    #
    #             organization = organizations[0]
    #             assert organization.name == "Org 1"
    #             assert organization.phone_numbers[0].phone_number == "123456789"

class TestGeoUtils:
    @pytest.mark.parametrize(
        "input_point_latitude, input_point_longitude, "
        "obj_latitude, obj_longitude, radius_km, expectation",
        [
            (53.9030, 27.5620, 53.9023, 27.5619, 0.15, does_not_raise()),
            (53.9024, 27.5620, 53.9023, 27.5619, 0, pytest.raises(ValueError)),
        ]
    )
    def test_is_within_radius(
            self,
            input_point_latitude,
            input_point_longitude,
            obj_latitude,
            obj_longitude,
            radius_km,
            expectation):
        with expectation:
            result = GeoUtils.is_within_radius(input_point_latitude,
                                                               input_point_longitude,
                                                               obj_latitude,
                                                               obj_longitude,
                                                               radius_km)
            assert isinstance(result, bool)
            assert result

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "latitude, longitude, expectation",
        [
            (52.4252, 30.9754, does_not_raise()),
            (30.9754, "30.9754", pytest.raises(ValueError)),
        ]
    )
    async def test_find_city_by_coordinates(
            self,
            latitude: float,
            longitude: float,
            expectation):
        with expectation:
            result = await GeoUtils.find_city_by_coordinates(latitude, longitude)

            assert result
            assert isinstance(result, str)
            assert result == "Гомель"
