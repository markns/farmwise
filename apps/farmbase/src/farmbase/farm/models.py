from __future__ import annotations

import datetime
from typing import List, Optional

from pydantic import Field as PydanticField
from sqlalchemy import (
    TEXT,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.associationproxy import association_proxy  # For simpler many-to-many access if needed
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.contact.models import Contact, ContactRead
from farmbase.database.core import Base
from farmbase.farm.field.models import Field
from farmbase.models import FarmbaseBase, Pagination, PrimaryKey


class Farm(Base):
    __tablename__ = "farm"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Changed farm_id to id
    farm_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    date_registered: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)

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
        return f"<Farm(id={self.id}, farm_name='{self.farm_name}')>"  # Changed farm_id to id


class FarmContact(Base):
    __tablename__ = "farm_contact"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Changed farm_contact_id to id
    farm_id: Mapped[int] = mapped_column(ForeignKey(Farm.id), nullable=False)  # Changed Farm.farm_id to Farm.id
    contact_id: Mapped[int] = mapped_column(
        ForeignKey(Contact.id), nullable=False
    )  # Changed Contact.contact_id to Contact.id
    role: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (UniqueConstraint("farm_id", "contact_id", "role", name="uq_farm_contact_role"),)

    # Relationships
    farm: Mapped["Farm"] = relationship(back_populates="contact_associations")
    contact: Mapped["Contact"] = relationship(back_populates="farm_associations")

    def __repr__(self):
        return f"<FarmContact(id={self.id}, farm_id={self.farm_id}, contact_id={self.contact_id}, role='{self.role}')>"  # Changed farm_contact_id to id


# Pydantic models
class FarmBase(FarmbaseBase):
    """Base model for Farm data."""

    farm_name: str = PydanticField(description="The name of the farm")
    address: Optional[str] = PydanticField(default=None, description="The address of the farm")
    date_registered: Optional[datetime.datetime] = PydanticField(
        default=None, description="The date the farm was registered"
    )


class FarmCreate(FarmBase):
    """Model for creating a new Farm."""

    pass


class FarmUpdate(FarmbaseBase):
    """Model for updating an existing Farm."""

    farm_name: Optional[str] = PydanticField(default=None, description="Updated name of the farm")
    address: Optional[str] = PydanticField(default=None, description="Updated address of the farm")
    date_registered: Optional[datetime.datetime] = PydanticField(default=None, description="Updated registration date")


class FarmContactBase(FarmbaseBase):
    """Base model for FarmContact data."""

    farm_id: PrimaryKey = PydanticField(description="ID of the farm")
    contact_id: PrimaryKey = PydanticField(description="ID of the contact")
    role: str = PydanticField(description="Role of the contact in the farm")


class FarmContactCreate(FarmContactBase):
    """Model for creating a new FarmContact."""

    pass


class FarmContactUpdate(FarmbaseBase):
    """Model for updating an existing FarmContact."""

    role: Optional[str] = PydanticField(default=None, description="Updated role of the contact in the farm")


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
