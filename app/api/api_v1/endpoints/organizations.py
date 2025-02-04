# ·	список организаций, которые находятся в заданном радиусе/прямоугольной области относительно указанной точки на карте. список зданий
# ·	искать организации по виду деятельности. Например, поиск по виду деятельности «Еда», которая находится на первом уровне дерева, и чтобы нашлись все организации, которые относятся к видам деятельности, лежащим внутри. Т.е. в результатах поиска должны отобразиться организации с видом деятельности Еда, Мясная продукция, Молочная продукция.
# ·	ограничить уровень вложенности деятельностей 3 уровням. В бд можно сколько угодно, но возвращаться всегд будут максимум 3 уровня
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship

from app import services, schemas
from app.dependencies import organization_service
from app.services import OrganizationService, BuildingService

router = APIRouter()

organization_service_dep = Annotated[OrganizationService, Depends(organization_service)]
building_service_dep = Annotated[BuildingService, Depends(organization_service)]


@router.get("/get_organizations_by_building_address",
            response_model=List[schemas.Organization])
def get_organizations_by_building_address(
        city: str,
        street: str,
        house: str,
        service: organization_service_dep
) -> List[schemas.Organization]:
    organizations = service.get_organizations_by_building_address(city, street, house)
    if not organizations:
        raise HTTPException(404, "No data by this query")
    return organizations


@router.get("/get_organizations_by_activity",
            response_model=List[schemas.Organization])
def get_organizations_by_activity(
        activity: str,
        service: organization_service_dep
) -> List[schemas.Organization]:
    organizations = service.get_organizations_by_activity(activity)
    if not organizations:
        raise HTTPException(404, "No data by this query")
    return organizations


@router.get("/get_organization_by_id",
            response_model=schemas.Organization)
def get_organization_by_id(
        organization_id: int,
        service: organization_service_dep
) -> schemas.Organization | None:
    organization = service.get_organization_by_id(organization_id)
    if not organization:
        raise HTTPException(404, "No data by this query")
    return organization


@router.get("/get_organization_by_name",
            response_model=schemas.Organization)
def get_organization_by_name(
        name: str,
        service: organization_service_dep
) -> schemas.Organization | None:
    organization = service.get_organization_by_name(name)
    if not organization:
        raise HTTPException(404, "No data by this query")
    return organization


@router.get("/get_organizations_by_coordinates",
            response_model=List[dict])
def get_organizations_by_coordinates(
        latitude: float,
        longitude: float,
        radius: float,
        service: building_service_dep
) -> List[dict]:
    buildings_organizations_dicts: list = service.get_by_coordinates(latitude, longitude, radius)
    if not buildings_organizations_dicts:
        raise HTTPException(404, "No data by this query")
    return buildings_organizations_dicts


@router.get("/get_organizations_by_subactivities",
            response_model=List[schemas.Organization])
def get_organizations_by_subactivities(
        activity: str,
        service: organization_service_dep
):
    organizations = service.get_organizations_by_subactivities(activity)
    if not organizations:
        raise HTTPException(404, "No data by this query")
    return organizations
