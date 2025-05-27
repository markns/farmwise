from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette import status

from farmbase.database.core import DbSession
from farmbase.models import PrimaryKey

from . import service
from .filterset import NoteFilterSet, NoteQueryParams
from .models import Note, NoteCreate, NotePagination, NoteRead, NoteUpdate

router = APIRouter()


@router.get("", response_model=NotePagination)
async def list_notes(
    db_session: DbSession,
    query_params: Annotated[NoteQueryParams, Query()],
):
    """List notes."""
    stmt = select(Note).options(
        selectinload(Note.field),
        selectinload(Note.farm),
        selectinload(Note.planting),
        selectinload(Note.created_by_contact),
    )
    filter_set = NoteFilterSet(db_session, stmt)
    params_d = query_params.model_dump(exclude_none=True)
    total = await filter_set.count(params_d)
    notes = await filter_set.filter(params_d)
    return NotePagination(
        items=notes,
        items_per_page=query_params.items_per_page,
        page=query_params.page,
        total=total,
    )


@router.post("", response_model=NoteRead)
async def create_note(
    db_session: DbSession,
    note_in: NoteCreate,
):
    """Create a new note."""
    return await service.create_note(db_session=db_session, note_in=note_in)


@router.get("/{note_id}", response_model=NoteRead)
async def get_note(
    db_session: DbSession,
    note_id: PrimaryKey,
):
    """Get a note by ID."""
    note = await service.get_note(db_session=db_session, note_id=note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Note not found."}],
        )
    return note


@router.put("/{note_id}", response_model=NoteRead)
async def update_note(
    db_session: DbSession,
    note_id: PrimaryKey,
    note_in: NoteUpdate,
):
    """Update an existing note."""
    note = await service.get_note(db_session=db_session, note_id=note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Note not found."}],
        )
    return await service.update_note(db_session=db_session, note=note, note_in=note_in)


@router.delete("/{note_id}", response_model=None)
async def delete_note(
    db_session: DbSession,
    note_id: PrimaryKey,
):
    """Delete a note by ID."""
    note = await service.get_note(db_session=db_session, note_id=note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Note not found."}],
        )
    await service.delete_note(db_session=db_session, note_id=note_id)
