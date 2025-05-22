from __future__ import annotations

import datetime

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

from farmbase.contact.models import Contact
from farmbase.database.core import Base
from farmbase.farm.field.models import Field


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
