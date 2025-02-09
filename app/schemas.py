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


Activity.model_rebuild()
