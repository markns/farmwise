from typing import Any, List, Optional

from pydantic import Field, field_validator
from pydantic.color import Color
from slugify import slugify
from sqlalchemy import Column
from sqlalchemy.event import listen
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import TSVectorType

from farmbase.database.core import Base
from farmbase.models import FarmbaseBase, OrganizationSlug, Pagination, PrimaryKey
from farmbase.validators import must_not_be_blank


class Organization(Base):
    __table_args__ = {"schema": "farmbase_core"}
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    slug: Mapped[str]
    default: Mapped[bool]
    description: Mapped[str]
    banner_enabled: Mapped[bool] = mapped_column(nullable=True)
    banner_color: Mapped[str] = mapped_column(nullable=True)
    banner_text: Mapped[str] = mapped_column(nullable=True)

    users: Mapped[List["FarmbaseUserOrganization"]] = relationship(back_populates="organization")

    search_vector = Column(TSVectorType("name", "description", weights={"name": "A", "description": "B"}))


def generate_slug(target, value, oldvalue, initiator):
    """Creates a reasonable slug based on organization name."""
    if value and (not target.slug or value != oldvalue):
        target.slug = slugify(value, separator="_")


listen(Organization.name, "set", generate_slug)


class OrganizationBase(FarmbaseBase):
    name: str
    description: Optional[str] = Field(None, nullable=True)
    default: Optional[bool] = Field(False, nullable=True)
    banner_enabled: Optional[bool] = Field(False, nullable=True)
    banner_color: Optional[Color] = Field(None, nullable=True)
    banner_text: Optional[str] = Field(None, nullable=True)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Any):
        return must_not_be_blank(v)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(FarmbaseBase):
    description: Optional[str] = Field(None, nullable=True)
    default: Optional[bool] = Field(False, nullable=True)
    banner_enabled: Optional[bool] = Field(False, nullable=True)
    banner_color: Optional[Color] = Field(None, nullable=True)
    banner_text: Optional[str] = Field(None, nullable=True)


class OrganizationRead(OrganizationBase):
    id: PrimaryKey
    slug: Optional[OrganizationSlug]


class OrganizationPagination(Pagination):
    items: List[OrganizationRead] = []
