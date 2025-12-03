from datetime import date

from pydantic import Field
from sqlalchemy_filterset import Filter, OrderingField, OrderingFilter

from farmbase.database.core import BaseFilterSet
from farmbase.farm.note.models import Note
from farmbase.models import PaginationParams


class NoteFilterSet(BaseFilterSet[Note]):
    farm_id = Filter(Note.farm_id)
    field_id = Filter(Note.field_id)
    planting_id = Filter(Note.planting_id)
    ordering = OrderingFilter(
        id=OrderingField(Note.id),
        # note_date=OrderingField(Note.note_date),
    )


class NoteQueryParams(PaginationParams):
    farm_id: int | None = Field(None)
    field_id: int | None = Field(None)
    planting_id: int | None = Field(None)
    note_date: date | None = Field(None)
