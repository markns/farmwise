from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any, List, Optional

from geoalchemy2 import Geometry, WKBElement
from pydantic import Field as PydanticField
from pydantic import field_serializer, field_validator
from sqlalchemy import (
    TEXT,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase import validators
from farmbase.contact.models import Contact
from farmbase.database.core import Base
from farmbase.farm.field.models import Field
from farmbase.farm.planting.models import Planting
from farmbase.models import FarmbaseBase, Location, Pagination, PrimaryKey, TimeStampMixin

if TYPE_CHECKING:
    from farmbase.farm.models import Farm


class Note(Base, TimeStampMixin):
    __tablename__ = "note"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farm.id"), nullable=False)
    contact_id_created_by: Mapped[int] = mapped_column(ForeignKey("contact.id"))
    field_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Field.id), nullable=True)
    planting_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Planting.id), nullable=True)
    note_text: Mapped[str] = mapped_column(TEXT, nullable=False)
    location: Mapped[Optional[WKBElement]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, name="geometry"), nullable=True
    )
    image_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    field: Mapped[Optional["Field"]] = relationship(back_populates="notes")
    farm: Mapped["Farm"] = relationship(back_populates="notes")
    planting: Mapped[Optional["Planting"]] = relationship(back_populates="notes")
    created_by_contact: Mapped[Optional["Contact"]] = relationship(back_populates="notes_created")

    def __repr__(self):
        return f"<Note(id={self.id}, note_text={self.note_text})>"


class NoteBase(FarmbaseBase):
    field_id: Optional[int] = PydanticField(default=None, description="ID of the field where the note was made")
    farm_id: int = PydanticField(..., description="ID of the farm where the note was made")
    contact_id_created_by: Optional[PrimaryKey] = PydanticField(
        ..., description="ID of the contact who created the note"
    )
    planting_id: Optional[int] = PydanticField(default=None, description="ID of the planting associated with the note")
    note_text: str = PydanticField(..., description="Text content of the note")
    location: Optional[Location] = PydanticField(default=None, description="Location for the note")
    image_path: Optional[str] = PydanticField(default=None, description="Path to an image for the note")
    tags: Optional[str] = PydanticField(default=None, description="Tags for the note")

    @field_validator("location", mode="before")
    @classmethod
    def validate_location(cls, data: Any) -> Any:
        return validators.validate_location(data)


class NoteCreate(NoteBase):
    """Model for creating a new Note."""

    @field_serializer("location")
    def serialize_location(self, location: Location):
        if location is None:
            return None
        return location.to_ewkt()


class NoteUpdate(FarmbaseBase):
    """Model for updating an existing Note."""

    field_id: Optional[int] = PydanticField(default=None)
    farm_id: Optional[int] = PydanticField(default=None)
    planting_id: Optional[int] = PydanticField(default=None)
    note_date: Optional[date] = PydanticField(default=None)
    note_text: Optional[str] = PydanticField(default=None)
    location: Optional[Location] = PydanticField(default=None)
    image_path: Optional[str] = PydanticField(default=None)
    # contact_id_created_by: Optional[PrimaryKey] = PydanticField(default=None)
    tags: Optional[str] = PydanticField(default=None)


class NoteRead(NoteBase):
    """Model for reading Note data."""

    id: PrimaryKey = PydanticField(..., description="Unique identifier of the note")


class NotePagination(Pagination):
    """Model for paginated list of notes."""

    items: List[NoteRead] = PydanticField(default_factory=list, description="List of notes in the current page")


# Resolve forward references
NoteRead.model_rebuild()
NotePagination.model_rebuild()
