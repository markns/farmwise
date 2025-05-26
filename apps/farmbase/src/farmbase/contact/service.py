from typing import Optional, Sequence

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..farm.models import FarmContact
from ..organization.models import Organization
from .models import Contact, ContactCreate, ContactPatch, ContactRead


async def get(*, db_session: AsyncSession, contact_id: int) -> Contact | None:
    """Returns a contact based on the given contact id."""
    result = await db_session.execute(
        select(Contact)
        .options(
            selectinload(Contact.farm_associations).selectinload(FarmContact.farm),
        )
        .where(Contact.id == contact_id)
    )
    return result.scalar_one()


async def get_by_name(*, db_session: AsyncSession, name: str) -> Optional[Contact]:
    """Returns a contact based on the given contact name."""
    result = await db_session.execute(select(Contact).where(Contact.name == name))
    return result.scalar_one_or_none()


async def get_by_phone_number(*, db_session: AsyncSession, phone_number: str) -> Optional[Contact]:
    """Returns a contact based on the given contact phone number."""
    result = await db_session.execute(
        select(Contact)
        .options(
            selectinload(Contact.farm_associations).selectinload(FarmContact.farm),
            # TODO: don't know why this selectinload is required, whereas for get it's not.
            selectinload(Contact.organization),
        )
        .where(Contact.phone_number == phone_number)
    )
    return result.scalar_one_or_none()


async def get_by_name_or_raise(*, db_session: AsyncSession, contact_in: ContactRead) -> Contact:
    """Returns the contact specified or raises ValidationError."""
    contact = await get_by_name(db_session=db_session, name=contact_in.name)

    if not contact:
        raise ValidationError.from_exception_data(
            "ContactRead",
            [
                {
                    "loc": ("name",),
                    "msg": f"Contact '{contact_in.name}' not found.",
                    "type": "value_error.not_found",
                }
            ],
        )

    return contact


async def get_by_name_or_default(*, db_session: AsyncSession, contact_in: ContactRead) -> Contact:
    """Returns a contact based on a name or the default if not specified."""
    if contact_in:
        if contact_in.name:
            return await get_by_name_or_raise(db_session=db_session, contact_in=contact_in)
    return await get_default_or_raise(db_session=db_session)


async def get_all(*, db_session: AsyncSession) -> Sequence[Contact]:
    """Returns all contacts."""
    result = await db_session.execute(select(Contact))
    return result.scalars().all()


async def get_all_with_location(*, db_session: AsyncSession) -> Sequence[Contact]:
    """Returns all contacts."""
    result = await db_session.execute(select(Contact).where(Contact.location.is_not(None)))
    return result.scalars().all()


async def create(*, db_session: AsyncSession, contact_in: ContactCreate, organization: Organization) -> Contact:
    """Creates a contact."""

    contact = Contact(
        **contact_in.model_dump(exclude={"organization"}),
        organization_id=organization.id,
    )

    db_session.add(contact)
    await db_session.commit()
    return contact


async def patch(*, db_session: AsyncSession, contact: Contact, contact_in: ContactPatch) -> Contact:
    """Patches a contact."""
    contact_data = contact.dict()

    patch_data = contact_in.model_dump(exclude_defaults=True, exclude_unset=True)

    for field in contact_data:
        if field in patch_data and patch_data[field] is not None:
            setattr(contact, field, patch_data[field])

    await db_session.commit()
    # refresh to ensure location is reloaded from db
    await db_session.refresh(contact)
    return contact


async def delete(*, db_session: AsyncSession, contact_id: int) -> None:
    """Deletes a contact."""
    result = await db_session.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalars().first()
    if contact:
        await db_session.delete(contact)
        await db_session.commit()
