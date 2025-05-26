from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape
from loguru import logger
from pydantic import Field as PydanticField
from pydantic import field_serializer, field_validator
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.contact.models import Contact, ContactRead
from farmbase.database.core import Base
from farmbase.enums import FarmContactRole
from farmbase.farm.field.models import Field
from farmbase.models import FarmbaseBase, Location, Pagination, PrimaryKey, TimeStampMixin

if TYPE_CHECKING:
    from farmbase.farm.field.models import FieldGroup
    from farmbase.farm.harvest.models import StorageLocation
    from farmbase.farm.note.models import Note


class Farm(Base, TimeStampMixin):
    __tablename__ = "farm"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # location: Mapped[Optional[WKBElement]] = mapped_column(
    #     Geometry(geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"), nullable=True
    # )
    location: Mapped[Optional[WKBElement]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=True
    )

    # Relationships
    fields: Mapped[list["Field"]] = relationship(back_populates="farm")
    field_groups: Mapped[list["FieldGroup"]] = relationship(back_populates="farm")
    storage_locations: Mapped[list["StorageLocation"]] = relationship(back_populates="farm")
    notes: Mapped[list["Note"]] = relationship(back_populates="farm")
    contact_associations: Mapped[list["FarmContact"]] = relationship(
        back_populates="farm", cascade="all, delete-orphan"
    )

    contacts = association_proxy("contact_associations", "contact")

    def __repr__(self):
        return f"<Farm(id={self.id}, farm_name='{self.farm_name}')>"


class FarmContact(Base):
    __tablename__ = "farm_contact"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey(Farm.id), nullable=False)
    contact_id: Mapped[int] = mapped_column(ForeignKey(Contact.id), nullable=False)
    role: Mapped[FarmContactRole] = mapped_column(
        SqlEnum(FarmContactRole, name="farm_contact_role_enum"), nullable=False
    )

    __table_args__ = (UniqueConstraint("farm_id", "contact_id", "role", name="uq_farm_contact_role"),)

    # Relationships
    farm: Mapped["Farm"] = relationship(back_populates="contact_associations")
    contact: Mapped["Contact"] = relationship(back_populates="farm_associations")

    def __repr__(self):
        return f"<FarmContact(id={self.id}, farm_id={self.farm_id}, contact_id={self.contact_id}, role='{self.role}')>"


# Pydantic models
class FarmBase(FarmbaseBase):
    """Base model for Farm data."""

    farm_name: str = PydanticField(description="The name of the farm")
    location: Optional[Location] = PydanticField(default=None, description="Location of the farm")

    @field_validator("location", mode="before")
    @classmethod
    def validate_location(cls, data: Any) -> Any:
        logger.info(f"Validating location: {type(data)} {data}")
        if isinstance(data, WKBElement):
            point = to_shape(data)
            return {"longitude": point.x, "latitude": point.y}
        # If data is already a dictionary or another compatible type, pass it through.
        return data


class FarmContactLink(FarmbaseBase):
    """Model for linking a contact when creating a farm."""

    contact_id: PrimaryKey = PydanticField(description="ID of the contact to link")
    role: FarmContactRole = PydanticField(description="Role of the contact in the farm")


class FarmWriteBase(FarmBase):
    @field_serializer("location")
    def serialize_location(self, location: Location):
        if location is None:
            return None
        return location.to_ewkt()


class FarmCreate(FarmWriteBase):
    """Model for creating a new Farm."""

    contacts: List[FarmContactLink] = PydanticField(
        default_factory=list,
        description="List of contacts to link to the farm upon creation",
    )


class FarmUpdate(FarmWriteBase):
    """Model for updating an existing Farm."""

    farm_name: Optional[str] = PydanticField(default=None, description="Updated name of the farm")
    location: Optional[Location] = PydanticField(default=None, description="Updated location of the farm")


class FarmContactBase(FarmbaseBase):
    """Base model for FarmContact data."""

    farm_id: PrimaryKey = PydanticField(description="ID of the farm")
    contact_id: PrimaryKey = PydanticField(description="ID of the contact")
    role: FarmContactRole = PydanticField(description="Role of the contact in the farm")


class FarmContactCreate(FarmContactBase):
    """Model for creating a new FarmContact."""

    pass


class FarmContactUpdate(FarmbaseBase):
    """Model for updating an existing FarmContact."""

    role: Optional[FarmContactRole] = PydanticField(default=None, description="Updated role of the contact in the farm")


class FarmContactRead(FarmContactBase):
    """Model for reading FarmContact data."""

    id: PrimaryKey = PydanticField(description="Unique identifier of the farm contact association")
    contact: ContactRead = PydanticField(description="Contact details")


class FarmRead(FarmBase):
    """Model for reading Farm data."""

    id: PrimaryKey = PydanticField(description="Unique identifier of the farm")
    contacts: Optional[List[ContactRead]] = PydanticField(
        default_factory=list, description="List of contacts associated with the farm"
    )


class FarmPagination(Pagination):
    """Model for paginated list of farms."""

    items: List[FarmRead] = PydanticField(default_factory=list, description="List of farms in the current page")


class FarmContactPagination(Pagination):
    """Model for paginated list of farm contacts."""

    items: List[FarmContactRead] = PydanticField(
        default_factory=list, description="List of farm contacts in the current page"
    )
