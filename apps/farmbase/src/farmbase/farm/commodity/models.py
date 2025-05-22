from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base

# from farmbase.farm.planting.models import Planting


class Commodity(Base):
    __tablename__ = "commodity"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Changed commodity_id to id
    commodity_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Relationships
    plantings: Mapped[list["Planting"]] = relationship(back_populates="commodity")

    def __repr__(self):
        return f"<Commodity(id={self.id}, commodity_name='{self.commodity_name}')>"  # Changed commodity_id to id
