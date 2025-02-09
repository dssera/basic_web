from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from app import schemas
from app.services import OrganizationService, BuildingService

router = APIRouter()

organization_service_dep = Annotated[OrganizationService, Depends()]
building_service_dep = Annotated[BuildingService, Depends()]


@router.get("/get_organizations_by_building_address",
            response_model=List[schemas.Organization])
async def get_organizations_by_building_address(
        city: str,
        street: str,
        house: str,
        service: organization_service_dep
) -> List[schemas.Organization]:
    organizations = await service.get_organizations_by_building_address(city, street, house)
    if not organizations:
        raise HTTPException(404, "No data by this query")
    return organizations


@router.get("/get_organizations_by_activity",
            response_model=List[schemas.Organization])
async def get_organizations_by_activity(
        activity: str,
        service: organization_service_dep
) -> List[schemas.Organization]:
    organizations = await service.get_organizations_by_activity(activity)
    if not organizations:
        raise HTTPException(404, "No data by this query")
    return organizations


@router.get("/get_organization_by_id",
            response_model=schemas.Organization)
async def get_organization_by_id(
        organization_id: int,
        service: organization_service_dep
) -> schemas.Organization | None:
    organization = await service.get_organization_by_id(organization_id)
    if not organization:
        raise HTTPException(404, "No data by this query")
    return organization


@router.get("/get_organization_by_name",
            response_model=schemas.Organization)
async def get_organization_by_name(
        name: str,
        service: organization_service_dep
) -> schemas.Organization | None:
    organization = await service.get_organization_by_name(name)
    if not organization:
        raise HTTPException(404, "No data by this query")
    return organization


@router.get("/get_organizations_by_coordinates",
            response_model=List[dict])
async def get_organizations_by_coordinates(
        latitude: float,
        longitude: float,
        radius: float,
        service: building_service_dep
) -> List[dict]:
    buildings_organizations_dicts: list = await service.get_by_coordinates(latitude, longitude, radius)
    if not buildings_organizations_dicts:
        raise HTTPException(404, "No data by this query")
    return buildings_organizations_dicts


@router.get("/get_organizations_by_subactivities",
            response_model=List[schemas.Organization])
async def get_organizations_by_subactivities(
        activity: str,
        service: organization_service_dep
):
    organizations = await service.get_organizations_by_subactivities(activity)
    if not organizations:
        raise HTTPException(404, "No data by this query")
    return organizations
