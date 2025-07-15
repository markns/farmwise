from __future__ import annotations

import datetime
from typing import Optional

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import (
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import CurrencyType

from farmbase.database.core import Base


class Market(Base):
    __table_args__ = (
        UniqueConstraint("name", name="uq_market_name"),
        {"schema": "farmbase_core"},
    )
    __tablename__ = "market"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[WKBElement]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=True
    )

    market_prices: Mapped[list["MarketPrice"]] = relationship(back_populates="market")


class MarketPrice(Base):
    """
    Records the price of a specific commodity at a given market on a particular date.
    References both the Commodity and Market models.
    """

    __table_args__ = (
        UniqueConstraint("market_id", "commodity_id", "date", name="uq_market_price"),
        {"schema": "farmbase_core"},
    )
    __tablename__ = "market_price"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Foreign key to Market (replacing the old 'market' string column)
    market_id: Mapped[int] = mapped_column(ForeignKey("farmbase_core.market.id"), nullable=False)
    # Relationship to Market: each market price belongs to one market
    market: Mapped["Market"] = relationship(back_populates="market_prices")

    # Foreign key to Commodity
    commodity_id: Mapped[int] = mapped_column(ForeignKey("farmbase_core.commodity.id"), nullable=False)
    # Relationship to Commodity: each market price is for one commodity
    commodity: Mapped["Commodity"] = relationship(back_populates="market_prices")
    date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    supply_volume: Mapped[float | None] = mapped_column(Float, nullable=True)
    wholesale_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    wholesale_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    wholesale_ccy: Mapped[str | None] = mapped_column(CurrencyType, nullable=True)
    retail_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    retail_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    retail_ccy: Mapped[str | None] = mapped_column(CurrencyType, nullable=True)

    def __repr__(self):
        # Updated __repr__ to use the relationship for market name
        market_name = self.market.name if self.market else "N/A"
        commodity_name = self.commodity.name if self.commodity else "N/A"
        return (
            f"<MarketPrice(id={self.id}, market_name='{market_name}', "
            f"commodity='{commodity_name}', date={self.date}, "
            f"wholesale_price={self.wholesale_price})>"
        )
