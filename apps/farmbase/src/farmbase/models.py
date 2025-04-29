import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Annotated, Optional

import geoalchemy2 as ga
from geojson_pydantic import LineString, Polygon
from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.fields import Field
from pydantic.networks import AnyHttpUrl, EmailStr
from pydantic.types import SecretStr, constr
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, event, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlmodel import Field as SQLField
from sqlmodel import Relationship, SQLModel

# pydantic type that limits the range of primary keys
PrimaryKey = Annotated[int | None, Field(default=None, gt=0.0, lt=2147483647.0)]
OrganizationSlug = constr(pattern=r"^[\w]+(?:_[\w]+)*$", min_length=3)


# SQLAlchemy models...
class ProjectMixin(object):
    """Project mixin"""

    @declared_attr
    def project_id(cls):  # noqa
        return Column(Integer, ForeignKey("project.id", ondelete="CASCADE"))

    @declared_attr
    def project(cls):  # noqa
        return relationship("Project")


class TimeStampMixin(object):
    """Timestamping mixin"""

    created_at = Column(DateTime, default=datetime.utcnow)
    created_at._creation_order = 9998
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_at._creation_order = 9998

    @staticmethod
    def _updated_at(mapper, connection, target):
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._updated_at)


class ContactMixin(TimeStampMixin):
    """Contact mixin"""

    is_active = Column(Boolean, default=True)
    is_external = Column(Boolean, default=False)
    contact_type = Column(String)
    email = Column(String)
    company = Column(String)
    notes = Column(String)
    owner = Column(String)


class ResourceMixin(TimeStampMixin):
    """Resource mixin."""

    resource_type = Column(String)
    resource_id = Column(String)
    weblink = Column(String)


class EvergreenMixin(object):
    """Evergreen mixin."""

    evergreen = Column(Boolean)
    evergreen_owner = Column(String)
    evergreen_reminder_interval = Column(Integer, default=90)  # number of days
    evergreen_last_reminder_at = Column(DateTime, default=datetime.utcnow())

    @hybrid_property
    def overdue(self):
        now = datetime.utcnow()
        next_reminder = self.evergreen_last_reminder_at + timedelta(days=self.evergreen_reminder_interval)

        if now >= next_reminder:
            return True

    @overdue.expression
    def overdue(cls):
        return (
            func.date_part("day", func.now() - cls.evergreen_last_reminder_at) >= cls.evergreen_reminder_interval  # noqa
        )


class FeedbackMixin(object):
    """Feedback mixin."""

    rating = Column(String)
    feedback = Column(String)


# Pydantic models...
class FarmbaseBase(BaseModel):
    class Config:
        from_attributes = True
        validate_assignment = True
        arbitrary_types_allowed = True
        str_strip_whitespace = True

        json_encoders = {
            # custom output conversion for datetime
            datetime: lambda v: v.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if v else None,
            SecretStr: lambda v: v.get_secret_value() if v else None,
        }


class Pagination(FarmbaseBase):
    items_per_page: int
    page: int
    total: int


class PrimaryKeyModel(BaseModel):
    id: PrimaryKey


class EvergreenBase(FarmbaseBase):
    evergreen: Optional[bool] = False
    evergreen_owner: Optional[EmailStr]
    evergreen_reminder_interval: Optional[int] = 90
    evergreen_last_reminder_at: Optional[datetime] = Field(None, nullable=True)


class ResourceBase(FarmbaseBase):
    resource_type: Optional[str] = Field(None, nullable=True)
    resource_id: Optional[str] = Field(None, nullable=True)
    weblink: Optional[AnyHttpUrl] = Field(None, nullable=True)


class ContactBase(FarmbaseBase):
    email: EmailStr
    name: Optional[str] = Field(None, nullable=True)
    is_active: Optional[bool] = True
    is_external: Optional[bool] = False
    company: Optional[str] = Field(None, nullable=True)
    contact_type: Optional[str] = Field(None, nullable=True)
    notes: Optional[str] = Field(None, nullable=True)
    owner: Optional[str] = Field(None, nullable=True)


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
    owner_id: uuid.UUID = SQLField(foreign_key="user.id", nullable=False, ondelete="CASCADE")
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


# Properties to receive on item creation
class FieldCreate(FieldBase):
    boundary: LineString = SQLField(default=None, nullable=False)


# Properties to receive on item update
class FieldUpdate(FieldBase):
    name: str | None = SQLField(default=None, min_length=1, max_length=255)


class Field(FieldBase, table=True):
    id: uuid.UUID = SQLField(default_factory=uuid.uuid4, primary_key=True)
    farm_id: uuid.UUID = SQLField(foreign_key="farm.id", nullable=False)
    farm: Farm = Relationship(back_populates="fields")

    linestring: bytes = SQLField(sa_type=ga.Geometry, nullable=False)
    boundary: bytes = SQLField(
        sa_type=ga.Geometry,
        nullable=False,
    )
    area: Decimal | None = SQLField(default=None)


# Properties to return via API, id is always required
class FieldPublic(FieldBase):
    id: uuid.UUID
    farm_id: uuid.UUID

    boundary: Polygon = SQLField(default=None, nullable=False)
    area: Decimal | None = SQLField(default=None)


class FieldsPublic(SQLModel):
    data: list[FieldPublic]
    count: int
