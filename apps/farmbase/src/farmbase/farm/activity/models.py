from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import DECIMAL, TEXT, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base

# from farmbase.farm.field.models import Field
from farmbase.farm.harvest.models import HarvestLoad
from farmbase.farm.planting.models import Planting
from farmbase.products.models import Product


class ActivityType(Base):
    __tablename__ = "activity_type"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activity_type_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    # Relationships
    farm_activities: Mapped[list["FarmActivity"]] = relationship(back_populates="activity_type")

    def __repr__(self):
        return f"<ActivityType(id={self.id}, activity_type_name='{self.activity_type_name}')>"


class FarmActivity(Base):
    __tablename__ = "farm_activity"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[Optional[int]] = mapped_column(ForeignKey("field.id"), nullable=True)
    planting_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Planting.id), nullable=True)
    activity_type_id: Mapped[int] = mapped_column(ForeignKey(ActivityType.id), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    activity_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)
    date_logged: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    field: Mapped[Optional["Field"]] = relationship(back_populates="farm_activities")
    planting: Mapped[Optional["Planting"]] = relationship(back_populates="farm_activities")
    activity_type: Mapped["ActivityType"] = relationship(back_populates="farm_activities")
    product_associations: Mapped[list["ActivityProduct"]] = relationship(
        back_populates="farm_activity", cascade="all, delete-orphan"
    )
    harvest_loads: Mapped[list["HarvestLoad"]] = relationship(
        back_populates="farm_activity", cascade="all, delete-orphan"
    )

    products = association_proxy("product_associations", "product")

    def __repr__(self):
        return f"<FarmActivity(id={self.id}, activity_type_id={self.activity_type_id})>"


class ActivityProduct(Base):
    __tablename__ = "activity_product"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_activity_id: Mapped[int] = mapped_column(ForeignKey(FarmActivity.id), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id), nullable=False)
    quantity_applied: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
    application_rate: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
    application_rate_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cost: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)

    # Relationships
    farm_activity: Mapped["FarmActivity"] = relationship(back_populates="product_associations")
    product: Mapped["Product"] = relationship(back_populates="activity_associations")

    def __repr__(self):
        return (
            f"<ActivityProduct(id={self.id}, farm_activity_id={self.farm_activity_id}, product_id={self.product_id})>"
        )
