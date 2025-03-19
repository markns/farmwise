import uuid
from decimal import Decimal
from typing import Any

from geoalchemy2 import Geometry, WKBElement
from geojson_pydantic import Polygon, Feature
from pydantic import EmailStr, ConfigDict
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field as SQLField
from sqlmodel import Relationship, SQLModel
import geoalchemy2 as ga


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = SQLField(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = SQLField(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = SQLField(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = SQLField(max_length=255)
    password: str = SQLField(min_length=8, max_length=40)
    full_name: str | None = SQLField(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = SQLField(default=None, max_length=255)  # type: ignore
    password: str | None = SQLField(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = SQLField(default=None, max_length=255)
    email: EmailStr | None = SQLField(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = SQLField(min_length=8, max_length=40)
    new_password: str = SQLField(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = SQLField(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    farms: list["Farm"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = SQLField(min_length=1, max_length=255)
    description: str | None = SQLField(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = SQLField(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = SQLField(default_factory=uuid.uuid4, primary_key=True)
    title: str = SQLField(max_length=255)
    owner_id: uuid.UUID = SQLField(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = SQLField(min_length=8, max_length=40)

# --------------------------------------------------
# FARM & OWNERSHIP MODELS
# --------------------------------------------------

class FarmBase(SQLModel):
    name: str = SQLField(max_length=255)
    location: str | None = SQLField(default=None, max_length=255)



# Properties to receive on item creation
class FarmCreate(FarmBase):
    pass

# Properties to receive on item update
class FarmUpdate(FarmBase):
    name: str | None = SQLField(default=None, min_length=1, max_length=255)

class Farm(FarmBase, table=True):
    id: uuid.UUID = SQLField(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = SQLField(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: User | None = Relationship(back_populates="farms")
    fields: list["Field"] = Relationship(back_populates="farm")

# Properties to return via API, id is always required
class FarmPublic(FarmBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class FarmsPublic(SQLModel):
    data: list[FarmPublic]
    count: int

# --------------------------------------------------
# Field MANAGEMENT (CROP FARMING)
# --------------------------------------------------

class FieldBase(SQLModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    name: str = SQLField(max_length=255)
    area: Decimal | None = SQLField(default=None)  # Area in hectares
    soil_type: str | None = SQLField(default=None, max_length=100)
    # geometry: WKBElement | None = SQLField(
    #     Geometry(geometry_type="POINT", srid=4326, spatial_index=True)
    # )
    # geometry: Geometry | None = SQLField(sa_column=Column(Geometry('POLYGON')))


# Properties to receive on item creation
class FieldCreate(FieldBase):
    feature: Feature = SQLField(default=None, nullable=False)

# Properties to receive on item update
class FieldUpdate(FieldBase):
    name: str | None = SQLField(default=None, min_length=1, max_length=255)


class Field(FieldBase, table=True):
    id: uuid.UUID = SQLField(default_factory=uuid.uuid4, primary_key=True)
    farm_id: uuid.UUID = SQLField(foreign_key="farm.id", nullable=False)
    farm: Farm = Relationship(back_populates="fields")

    geometry: bytes = SQLField(
        sa_type=ga.Geometry,
        nullable=False,
    )
    properties: dict | None = SQLField(
        default=None,
        sa_type=JSONB,
        nullable=True,
    )


# Properties to return via API, id is always required
class FieldPublic(FieldBase):
    id: uuid.UUID
    farm_id: uuid.UUID

    feature: Feature = SQLField(default=None, nullable=False)

class FieldsPublic(SQLModel):
    data: list[FieldPublic]
    count: int
