from datetime import datetime
from typing import Any, List, Optional

from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape
from pydantic import Field, field_serializer, field_validator
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base
from farmbase.models import FarmbaseBase, Location, Pagination, PrimaryKey, TimeStampMixin
from farmbase.organization.models import Organization, OrganizationRead
from farmbase.validators import must_not_be_blank

# TODO: use this pattern to add other contact types. eg. farmers
# https://docs.sqlalchemy.org/en/20/orm/queryguide/_inheritance_setup.html

#
# class Contact(Base):
#     __tablename__ = "contact"
#     __repr_attrs__ = ["name", "phone_number"]
#
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column()
#
#     # TODO: use PhoneNumber libraries for sqlalchemy and pydantic
#     phone_number: Mapped[str] = mapped_column(unique=True)
#     # _phone_number = Column(Unicode(20))
#     # country_code: Mapped[str] = mapped_column()
#     # phone_number = orm.composite(SQLPhoneNumber, _phone_number, country_code)
#
#     organization_id: Mapped[int] = mapped_column(ForeignKey(Organization.id))
#     organization = relationship("Organization")
#
#     location: Mapped[Optional[WKBElement]] = mapped_column(
#         Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=True
#     )


class Contact(Base, TimeStampMixin):
    __tablename__ = "contact"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    location: Mapped[Optional[WKBElement]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"), nullable=True
    )

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


class ContactBase(FarmbaseBase):
    """Base model for Contact data."""

    name: str = Field(description="The full name of the contact")
    location: Optional[Location] = Field(default=None, description="Contact's geographical location")


    @field_validator("location", mode="before")
    @classmethod
    def validate_location(cls, data: Any) -> Any:
        if isinstance(data, WKBElement):
            point = to_shape(data)
            return {"longitude": point.x, "latitude": point.y}
        # If data is already a dictionary or another compatible type, pass it through.
        return data


class ContactBaseWrite(ContactBase):
    @field_serializer("location")
    def serialize_location(self, location: Location):
        if location is None:
            return None
        return location.to_ewkt()


class ContactCreate(ContactBaseWrite):
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
    phone_number: str = Field(description="Contact's phone number")
    organization: OrganizationRead = Field(description="The organization the contact belongs to")
    created_at: datetime = Field(description="Timestamp when the contact was created")
    updated_at: datetime = Field(description="Timestamp when the contact was last updated")


class ContactPagination(Pagination):
    """Model for paginated list of contacts."""

    items: List[ContactRead] = Field(default_factory=list, description="List of contacts in the current page")
