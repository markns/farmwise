from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import DECIMAL, TEXT, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base

# from farmbase.farm.activity.models import FarmActivity
# from farmbase.farm.models import Farm


class StorageLocation(Base):
    __tablename__ = "storage_location"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farm.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    capacity: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)
    capacity_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location_address: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)

    # Relationships
    farm: Mapped["Farm"] = relationship(back_populates="storage_locations")
    harvest_loads_destination: Mapped[list["HarvestLoad"]] = relationship(back_populates="destination_storage_location")

    def __repr__(self):
        return f"<StorageLocation(id={self.id}, name='{self.name}')>"


class HarvestLoad(Base):
    __tablename__ = "harvest_load"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_activity_id: Mapped[int] = mapped_column(ForeignKey("farm_activity.id"), nullable=False)
    load_timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    quantity: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    moisture_content: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)
    ticket_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    destination_storage_location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(StorageLocation.id), nullable=True
    )
    destination_buyer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_id_person_involved: Mapped[Optional[int]] = mapped_column(ForeignKey("contact.id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "(destination_storage_location_id IS NOT NULL OR destination_buyer IS NOT NULL)",
            name="chk_harvest_load_destination",
        ),
    )

    # Relationships
    farm_activity: Mapped["FarmActivity"] = relationship(back_populates="harvest_loads")
    destination_storage_location: Mapped[Optional["StorageLocation"]] = relationship(
        back_populates="harvest_loads_destination"
    )
    person_involved_contact: Mapped[Optional["Contact"]] = relationship(back_populates="harvest_loads_involved")

    def __repr__(self):
        return f"<HarvestLoad(id={self.id}, farm_activity_id={self.farm_activity_id})>"
