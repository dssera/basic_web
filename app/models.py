from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship, Mapped

from app.db import Base


# back_populates on the both sides -> what will happen? (they're not consist)

# i dont understand this, so ask gpt
# Indicates the name of a relationship() on the related class that will be synchronized with this one.
# It is usually expected that the relationship() on the related class also refer to this one.
# This allows objects on both sides of each relationship() to synchronize in-Python state changes
# and also provides directives to the unit of work flush process how changes along these relationships should be persisted.

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String, nullable=False)
    street = Column(String, nullable=False)
    house = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    organizations = relationship("Organization",
                                 back_populates="building")


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String, unique=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))

    organization = relationship("Organization", back_populates="phone_numbers")


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"))

    building = relationship("Building",
                            back_populates="organizations")
    activities = relationship("Activity",
                              secondary="organization_activities",
                              back_populates="organizations")
    phone_numbers = relationship("PhoneNumber", back_populates="organization")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer,
                       ForeignKey("activities.id"),
                       nullable=True)

    children = relationship("Activity",
                            lazy="joined",
                            join_depth=3)
    organizations = relationship("Organization",
                                 secondary="organization_activities",
                                 back_populates="activities")


class OrganizationActivity(Base):
    __tablename__ = "organization_activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    activity_id = Column(Integer, ForeignKey("activities.id"))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)

    permissions = relationship("Permission",
                                 secondary="user_permissions",
                                 back_populates="users")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    details = Column(String, nullable=True)

    users = relationship("User",
                               secondary="user_permissions",
                               back_populates="permissions")


class UserPermissions(Base):
    __tablename__ = "user_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    permission_id = Column(Integer, ForeignKey("permissions.id"))