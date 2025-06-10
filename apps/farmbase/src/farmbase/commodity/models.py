from __future__ import annotations

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base
from farmbase.enums import Gender


class Commodity(Base):
    __table_args__ = (
        UniqueConstraint("name", "classification", "grade", "sex", name="uq_commodity_details"),
        {"schema": "farmbase_core"},
    )
    __tablename__ = "commodity"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    classification: Mapped[str | None] = mapped_column(String(100), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sex: Mapped[Gender | None] = mapped_column(SqlEnum(Gender, name="gender_enum"), nullable=True)

    # Relationships
    plantings: Mapped[list["Planting"]] = relationship(back_populates="commodity")
    market_prices: Mapped[list["MarketPrice"]] = relationship(back_populates="commodity")  # Add this relationship

    def __repr__(self):
        return f"<Commodity(id={self.id}, name='{self.name}')>"
