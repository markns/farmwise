# from __future__ import annotations

import datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import TEXT, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base
from farmbase.farm.field.models import Field
from farmbase.farm.models import Farm
from farmbase.farm.planting.models import Planting


class Note(Base):
    __tablename__ = "note"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Field.id), nullable=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey(Farm.id), nullable=False)
    planting_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Planting.id), nullable=True)
    note_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    note_text: Mapped[str] = mapped_column(TEXT, nullable=False)
    location_coordinates: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"), nullable=True
    )
    image_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    contact_id_created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("contact.id"), nullable=True)
    date_created: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    tags: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    field: Mapped[Optional["Field"]] = relationship(back_populates="notes")
    farm: Mapped["Farm"] = relationship(back_populates="notes")
    planting: Mapped[Optional["Planting"]] = relationship(back_populates="notes")
    created_by_contact: Mapped[Optional["Contact"]] = relationship(back_populates="notes_created")

    def __repr__(self):
        return f"<Note(id={self.id}, note_date={self.note_date})>"
