from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter, Security
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from starlette import status

from app.schemas import Token, User
from app.services import AuthService
from ....config import settings
from ....dependencies import get_current_active_user

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth_service = AuthService(pwd_context)
auth_service_dep = Annotated[AuthService, Depends(lambda: auth_service)]


@router.post("/token/")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        service: auth_service_dep
) -> Token:
    user = await service.authenticate_user(form_data.username, form_data.password)
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expires_data = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    print(form_data.scopes)
    permissions = [s.name for s in user.permissions]
    access_token = service.create_access_token(
        {"sub": user.username, "scopes": permissions},
        expires_delta=expires_data
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/", response_model=User)
async def read_users_me(
        current_user: Annotated[User, Security(get_current_active_user)],
):
    return current_user
