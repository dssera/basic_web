from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import SecurityScopes, OAuth2PasswordBearer
from fastapi.security import APIKeyHeader
import jwt
from passlib.exc import InvalidTokenError
from pydantic import ValidationError
from starlette import status

from .schemas import User, TokenData
from .uow import unit_of_work
from config import settings

api_key_header = APIKeyHeader(name="API-key")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    # scopes={"me": "Read information about the current user.", "items": "Read items."}
)


def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != settings.API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")


async def get_current_user(
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    async with unit_of_work() as uow:
        user = await uow.user_repository.get_user(token_data.username)
    if not user:
        raise credentials_exception
    # iterate through required scopes, and check if user has all of them
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user.")
    return current_user


def get_basic_user(
        basic_user: Annotated[User, Security(get_current_active_user, scopes=["basic_user"])]
):
    return basic_user


def get_advanced_user(
        advanced_user: Annotated[User, Security(get_current_active_user, scopes=["advanced_user"])]
):
    return advanced_user
