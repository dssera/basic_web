from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

from app.repositories import OrganizationRepository, BuildingRepository, ActivityRepository
from app.services import OrganizationService, BuildingService

from app.config import API_SECRET_KEY

api_key_header = APIKeyHeader(name="API-key")


def organization_service():
    return OrganizationService(OrganizationRepository(), ActivityRepository())

def building_service():
    return BuildingService(BuildingRepository(), OrganizationRepository())


def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
