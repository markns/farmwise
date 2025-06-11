from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import Field, field_validator
from sqlalchemy import (
    JSON,
    Date,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base
from farmbase.enums import ContactRole, Gender
from farmbase.models import FarmbaseBase, Pagination, PrimaryKey, TimeStampMixin
from farmbase.organization.models import Organization, OrganizationRead
from farmbase.validators import must_not_be_blank

# TODO: use this pattern to add other contact types. eg. farmers
# https://docs.sqlalchemy.org/en/20/orm/queryguide/_inheritance_setup.html


class Contact(Base, TimeStampMixin):
    __tablename__ = "contact"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    preferred_form_of_address: Mapped[str] = mapped_column(String(255), nullable=True)
    gender: Mapped[Gender] = mapped_column(SqlEnum(Gender, name="gender_enum"), nullable=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    estimated_age: Mapped[int] = mapped_column(Integer, nullable=True)
    # TODO: we might want to change Contact to a hierarchy in future.
    role: Mapped[ContactRole] = mapped_column(SqlEnum(ContactRole, name="contact_role_enum"), nullable=True)
    experience: Mapped[int] = mapped_column(Integer, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    # Add JSON field for product interests
    product_interests: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Relationships
    organization_id: Mapped[int] = mapped_column(ForeignKey(Organization.id))
    organization = relationship("Organization")

    farm_associations: Mapped[list["FarmContact"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )
    notes_created: Mapped[list["Note"]] = relationship(back_populates="created_by_contact")
    harvest_loads_involved: Mapped[list["HarvestLoad"]] = relationship(back_populates="person_involved_contact")

    farms = association_proxy("farm_associations", "farm")

    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.name}')>"


class ProductInterests(FarmbaseBase):
    crops: List[str]
    livestock: List[str]
    other: List[str]


class ContactBase(FarmbaseBase):
    """Base model for Contact data."""

    preferred_form_of_address: Optional[str] = Field(
        default=None, description="Preferred form of address of the contact"
    )
    gender: Optional[Gender] = Field(default=None, description="Contact's gender")
    date_of_birth: Optional[date] = Field(default=None, description="Contact's date of birth")
    estimated_age: Optional[int] = Field(default=None, description="Contact's estimated age")
    role: Optional[ContactRole] = Field(default=None, description="Role of the contact")
    experience: Optional[int] = Field(default=None, description="Contact's work experience in years")
    email: Optional[str] = Field(default=None, description="Contact's email address")
    product_interests: Optional[ProductInterests] = Field(
        default=None, description="The crops, livestock and other farm products that the contact is interested in"
    )


class ContactBaseWrite(ContactBase): ...


class ContactCreate(ContactBaseWrite):
    name: str = Field(description="The whatsapp name of the contact")
    phone_number: str = Field(description="Contact's phone number")


class ContactPatch(ContactBaseWrite):
    """Model for updating existing Contact."""

    name: Optional[str] = Field(default=None, description="Updated name of the contact")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            return must_not_be_blank(v)
        return v


class ContactRead(ContactBase):
    """Model for reading Contact data."""

    id: PrimaryKey = Field(description="Unique identifier of the contact")
    name: str = Field(description="The WhatsApp name of the contact")
    phone_number: str = Field(description="Contact's phone number")
    organization: OrganizationRead = Field(description="The organization the contact belongs to")
    farms: List["FarmSummary"] = Field(
        default_factory=list,
        description="List of farms associated with the contact",
    )


class ContactPagination(Pagination):
    """Model for paginated list of contacts."""

    items: List[ContactRead] = Field(default_factory=list, description="List of contacts in the current page")
