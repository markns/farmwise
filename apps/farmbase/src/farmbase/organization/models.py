from typing import List, Optional

from pydantic import Field
from pydantic.color import Color
from slugify import slugify
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.event import listen
from sqlalchemy_utils import TSVectorType

from farmbase.database.core import Base
from farmbase.models import FarmbaseBase, NameStr, OrganizationSlug, Pagination, PrimaryKey


class Organization(Base):
    __table_args__ = {"schema": "farmbase_core"}

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    slug = Column(String)
    default = Column(Boolean)
    description = Column(String)
    banner_enabled = Column(Boolean)
    banner_color = Column(String)
    banner_text = Column(String)

    search_vector = Column(TSVectorType("name", "description", weights={"name": "A", "description": "B"}))


def generate_slug(target, value, oldvalue, initiator):
    """Creates a reasonable slug based on organization name."""
    if value and (not target.slug or value != oldvalue):
        target.slug = slugify(value, separator="_")


listen(Organization.name, "set", generate_slug)


class OrganizationBase(FarmbaseBase):
    id: Optional[PrimaryKey]
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    default: Optional[bool] = Field(False, nullable=True)
    banner_enabled: Optional[bool] = Field(False, nullable=True)
    banner_color: Optional[Color] = Field(None, nullable=True)
    banner_text: Optional[NameStr] = Field(None, nullable=True)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(FarmbaseBase):
    id: Optional[PrimaryKey]
    description: Optional[str] = Field(None, nullable=True)
    default: Optional[bool] = Field(False, nullable=True)
    banner_enabled: Optional[bool] = Field(False, nullable=True)
    banner_color: Optional[Color] = Field(None, nullable=True)
    banner_text: Optional[NameStr] = Field(None, nullable=True)


class OrganizationRead(OrganizationBase):
    id: Optional[PrimaryKey]
    slug: Optional[OrganizationSlug]


class OrganizationPagination(Pagination):
    items: List[OrganizationRead] = []
