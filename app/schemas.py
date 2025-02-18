from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class PhoneNumber(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone_number: str


class OrganizationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    phone_numbers: List[PhoneNumber]


class OrganizationCreate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int


class BuildingBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    city: str
    street: str
    house: str
    latitude: float
    longitude: float


class BuildingCreate(BuildingBase):
    pass


class Building(BuildingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ActivityBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    parent_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class Activity(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    children: "List[Activity]" = []
    organizations: List[Organization] = []


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    disabled: bool = False
    permissions: "List[Permission]"


class User(UserBase):
    pass


class UserInDb(UserBase):
    hashed_password: str


class Permission(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    details: str

class Token(BaseModel):
    access_token: str  # jwt token
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []


Activity.model_rebuild()
UserBase.model_rebuild()

