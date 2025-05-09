from typing import List, Optional

from loguru import logger
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import true

from ..organization.models import Organization
from .models import Contact, ContactCreate, ContactPatch, ContactRead


async def get(*, db_session: AsyncSession, contact_id: int) -> Contact | None:
    """Returns a contact based on the given contact id."""
    result = await db_session.execute(select(Contact).where(Contact.id == contact_id))
    return result.scalars().first()


async def get_default(*, db_session: AsyncSession) -> Optional[Contact]:
    """Returns the default contact."""
    result = await db_session.execute(select(Contact).where(Contact.default == true()))
    return result.scalars().one_or_none()


async def get_default_or_raise(*, db_session: AsyncSession) -> Contact:
    """Returns the default contact or raises a ValidationError if one doesn't exist."""
    contact = await get_default(db_session=db_session)

    if not contact:
        raise ValidationError.from_exception_data(
            "ContactRead",
            [
                {
                    "loc": ("contact",),
                    "msg": "No default contact defined.",
                    "type": "value_error.not_found",
                }
            ],
        )
    return contact


async def get_by_name(*, db_session: AsyncSession, name: str) -> Optional[Contact]:
    """Returns a contact based on the given contact name."""
    result = await db_session.execute(select(Contact).where(Contact.name == name))
    return result.scalars().one_or_none()


async def get_by_phone_number(*, db_session: AsyncSession, phone_number: str) -> Optional[Contact]:
    """Returns a contact based on the given contact name."""
    result = await db_session.execute(select(Contact).where(Contact.phone_number == phone_number))
    return result.scalars().one_or_none()


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


async def get_all(*, db_session: AsyncSession) -> List[Optional[Contact]]:
    """Returns all contacts."""
    result = await db_session.execute(select(Contact))
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


async def get_or_create(*, db_session: AsyncSession, organization: Organization, contact_in: ContactCreate) -> Contact:
    contact = await get_by_phone_number(db_session=db_session, phone_number=contact_in.phone_number)
    if contact:
        logger.debug(contact)
        return contact
        # stmt = select(Contact).where(Contact.id == contact_in.id)
    else:
        #     filters = contact_in.model_dump(exclude={"id", "organization"})
        #     stmt = select(Contact).filter_by(**filters)
        #
        # result = await db_session.execute(stmt)
        # instance = result.scalars().first()
        # if instance:
        #     return instance

        return await create(db_session=db_session, contact_in=contact_in, organization=organization)


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
