"""
Service layer for farms and farm contacts.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from farmbase.farm.models import Farm, FarmContact, FarmContactCreate, FarmContactUpdate, FarmCreate, FarmUpdate


async def get_farm(*, db_session: AsyncSession, farm_id: int) -> Optional[Farm]:
    """Fetch a farm by its ID."""
    result = await db_session.execute(
        select(Farm)
        .where(Farm.id == farm_id)
        .options(selectinload(Farm.contact_associations).selectinload(FarmContact.contact))
    )
    return result.scalars().first()


async def create_farm(*, db_session: AsyncSession, farm_in: FarmCreate) -> Farm:
    """Create a new farm."""
    farm = Farm(**farm_in.model_dump())
    db_session.add(farm)
    await db_session.commit()
    await db_session.refresh(farm)  # Ensure we get the ID

    # Re-query with selectinload to populate relationships
    result = await db_session.execute(
        select(Farm)
        .where(Farm.id == farm.id)
        .options(selectinload(Farm.contact_associations).selectinload(FarmContact.contact))
    )
    return result.scalar_one()


async def update_farm(*, db_session: AsyncSession, farm: Farm, farm_in: FarmUpdate) -> Farm:
    """Update an existing farm."""
    data = farm_in.model_dump(exclude_none=True)
    for field, value in data.items():
        setattr(farm, field, value)
    await db_session.commit()
    return farm


async def delete_farm(*, db_session: AsyncSession, farm_id: int) -> None:
    """Delete a farm by its ID."""
    farm = await get_farm(db_session=db_session, farm_id=farm_id)
    if farm:
        await db_session.delete(farm)
        await db_session.commit()


async def get_farm_contact(*, db_session: AsyncSession, farm_contact_id: int) -> Optional[FarmContact]:
    """Fetch a farm contact by its ID."""
    result = await db_session.execute(
        select(FarmContact).where(FarmContact.id == farm_contact_id).options(selectinload(FarmContact.contact))
    )
    return result.scalars().first()


async def create_farm_contact(*, db_session: AsyncSession, farm_contact_in: FarmContactCreate) -> FarmContact:
    """Create a new farm contact."""
    farm_contact = FarmContact(**farm_contact_in.model_dump())
    db_session.add(farm_contact)
    await db_session.commit()
    return farm_contact


async def update_farm_contact(
    *, db_session: AsyncSession, farm_contact: FarmContact, farm_contact_in: FarmContactUpdate
) -> FarmContact:
    """Update an existing farm contact."""
    data = farm_contact_in.model_dump(exclude_none=True)
    for field, value in data.items():
        setattr(farm_contact, field, value)
    await db_session.commit()
    return farm_contact


async def delete_farm_contact(*, db_session: AsyncSession, farm_contact_id: int) -> None:
    """Delete a farm contact by its ID."""
    farm_contact = await get_farm_contact(db_session=db_session, farm_contact_id=farm_contact_id)
    if farm_contact:
        await db_session.delete(farm_contact)
        await db_session.commit()
