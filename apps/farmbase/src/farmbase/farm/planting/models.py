from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import DECIMAL, TEXT, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base

# from farmbase.farm.activity.models import FarmActivity
from farmbase.farm.commodity.models import Commodity

# from farmbase.farm.field.models import Field


class Planting(Base):
    __tablename__ = "planting"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("field.id"), nullable=False)
    commodity_id: Mapped[int] = mapped_column(ForeignKey(Commodity.id), nullable=False)
    planting_year: Mapped[int] = mapped_column(Integer, nullable=False)
    acres_planted: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    planting_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)  
    harvest_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)  
    total_actual_yield: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)  
    actual_yield_per_acre: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)  
    yield_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  
    yield_data_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  
    notes: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)  
    date_recorded: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    field: Mapped["Field"] = relationship(back_populates="plantings")
    commodity: Mapped["Commodity"] = relationship(back_populates="plantings")
    farm_activities: Mapped[list["FarmActivity"]] = relationship(
        back_populates="planting", cascade="all, delete-orphan"
    )
    notes: Mapped[list["Note"]] = relationship(back_populates="planting", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Planting(id={self.id}, field_id={self.field_id}, commodity_id={self.commodity_id})>"  # Changed planting_id to id
