from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class OrganizationBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    phone_numbers: Optional[str] = None
    building_id: int


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
    id: int
    organizations: List[Organization] = []

    class Config:
        orm_mode = True


class ActivityBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    parent_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class Activity(ActivityBase):
    id: int
    children: "List[Activity]" = []
    organizations: List[Organization] = []

    class Config:
        orm_mode = True


Activity.model_rebuild()
