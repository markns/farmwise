from __future__ import annotations

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import CountryType

from farmbase.database.core import Base


class Region(Base):
    # TODO: move region and subregion to core schema
    __table_args__ = {"schema": "farmbase_core"}
    __tablename__ = "region"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(CountryType, nullable=False)
    boundary: Mapped[str] = mapped_column(Geometry(geometry_type="MULTIPOLYGON", srid=4326))

    # Relationships
    subregions: Mapped[list[Subregion]] = relationship(back_populates="region", cascade="all, delete")

    def __repr__(self):
        return f"<Region(id={self.id}, name={self.name}, country={self.country})>"


class Subregion(Base):
    __table_args__ = {"schema": "farmbase_core"}
    __tablename__ = "subregion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    region_id: Mapped[int] = mapped_column(ForeignKey(Region.id, ondelete="CASCADE"), nullable=False)
    boundary: Mapped[str] = mapped_column(Geometry(geometry_type="MULTIPOLYGON", srid=4326))

    # Relationships
    region: Mapped[Region] = relationship(back_populates="subregions")

    def __repr__(self):
        return f"<Subregion(id={self.id}, name={self.name}, region_id={self.region_id})>"
