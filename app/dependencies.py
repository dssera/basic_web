from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

from app.config import settings

api_key_header = APIKeyHeader(name="API-key")


def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != settings.API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")
