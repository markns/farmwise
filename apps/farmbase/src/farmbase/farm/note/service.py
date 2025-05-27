from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from farmbase.farm.note.models import Note, NoteCreate, NoteUpdate


async def get_note(*, db_session: AsyncSession, note_id: int) -> Optional[Note]:
    """Fetch a note by its ID."""
    result = await db_session.execute(
        select(Note)
        .where(Note.id == note_id)
        .options(
            selectinload(Note.field),
            selectinload(Note.farm),
            selectinload(Note.planting),
            selectinload(Note.created_by_contact),
        )
    )
    return result.scalars().first()


async def create_note(*, db_session: AsyncSession, note_in: NoteCreate) -> Note:
    """Create a new note."""
    note = Note(**note_in.model_dump())
    db_session.add(note)
    await db_session.commit()
    return note


async def update_note(*, db_session: AsyncSession, note: Note, note_in: NoteUpdate) -> Note:
    """Update an existing note."""
    data = note_in.model_dump(exclude_none=True)
    for field, value in data.items():
        setattr(note, field, value)
    await db_session.commit()
    return note


async def delete_note(*, db_session: AsyncSession, note_id: int) -> None:
    """Delete a note by its ID."""
    note = await get_note(db_session=db_session, note_id=note_id)
    if note:
        await db_session.delete(note)
        await db_session.commit()
