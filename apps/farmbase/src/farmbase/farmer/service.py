from typing import List, Optional

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import true

from .models import Farmer, FarmerCreate, FarmerPatch, FarmerRead


async def get(*, db_session: AsyncSession, farmer_id: int) -> Farmer | None:
    """Returns a farmer based on the given farmer id."""
    result = await db_session.execute(select(Farmer).where(Farmer.id == farmer_id))
    return result.scalars().first()


async def get_default(*, db_session: AsyncSession) -> Optional[Farmer]:
    """Returns the default farmer."""
    result = await db_session.execute(select(Farmer).where(Farmer.default == true()))
    return result.scalars().one_or_none()


async def get_default_or_raise(*, db_session: AsyncSession) -> Farmer:
    """Returns the default farmer or raises a ValidationError if one doesn't exist."""
    farmer = await get_default(db_session=db_session)

    if not farmer:
        raise ValidationError.from_exception_data(
            "FarmerRead",
            [
                {
                    "loc": ("farmer",),
                    "msg": "No default farmer defined.",
                    "type": "value_error.not_found",
                }
            ],
        )
    return farmer


async def get_by_name(*, db_session: AsyncSession, name: str) -> Optional[Farmer]:
    """Returns a farmer based on the given farmer name."""
    result = await db_session.execute(select(Farmer).where(Farmer.name == name))
    return result.scalars().one_or_none()


async def get_by_phone_number(*, db_session: AsyncSession, phone_number: str) -> Optional[Farmer]:
    """Returns a farmer based on the given farmer name."""
    result = await db_session.execute(select(Farmer).where(Farmer.phone_number == phone_number))
    return result.scalars().one_or_none()


async def get_by_name_or_raise(*, db_session: AsyncSession, farmer_in: FarmerRead) -> Farmer:
    """Returns the farmer specified or raises ValidationError."""
    farmer = await get_by_name(db_session=db_session, name=farmer_in.name)

    if not farmer:
        raise ValidationError.from_exception_data(
            "FarmerRead",
            [
                {
                    "loc": ("name",),
                    "msg": f"Farmer '{farmer_in.name}' not found.",
                    "type": "value_error.not_found",
                }
            ],
        )

    return farmer


async def get_by_name_or_default(*, db_session: AsyncSession, farmer_in: FarmerRead) -> Farmer:
    """Returns a farmer based on a name or the default if not specified."""
    if farmer_in:
        if farmer_in.name:
            return await get_by_name_or_raise(db_session=db_session, farmer_in=farmer_in)
    return await get_default_or_raise(db_session=db_session)


async def get_all(*, db_session: AsyncSession) -> List[Optional[Farmer]]:
    """Returns all farmers."""
    result = await db_session.execute(select(Farmer))
    return result.scalars().all()


async def create(*, db_session: AsyncSession, farmer_in: FarmerCreate) -> Farmer:
    """Creates a farmer."""
    from farmbase.organization import service as organization_service

    organization = await organization_service.get_by_slug(db_session=db_session, slug=farmer_in.organization.slug)
    farmer = Farmer(
        **farmer_in.model_dump(exclude={"organization"}),
        organization_id=organization.id,
    )

    db_session.add(farmer)
    await db_session.commit()
    return farmer


async def get_or_create(*, db_session: AsyncSession, farmer_in: FarmerCreate) -> Farmer:
    if farmer_in.id:
        stmt = select(Farmer).where(Farmer.id == farmer_in.id)
    else:
        filters = farmer_in.model_dump(exclude={"id", "organization"})
        stmt = select(Farmer).filter_by(**filters)

    result = await db_session.execute(stmt)
    instance = result.scalars().first()
    if instance:
        return instance

    return await create(db_session=db_session, farmer_in=farmer_in)


async def patch(*, db_session: AsyncSession, farmer: Farmer, farmer_in: FarmerPatch) -> Farmer:
    """Patches a farmer."""
    farmer_data = farmer.dict()

    patch_data = farmer_in.model_dump(exclude_defaults=True, exclude_unset=True)

    for field in farmer_data:
        if field in patch_data:
            setattr(farmer, field, patch_data[field])

    await db_session.commit()
    return farmer


async def delete(*, db_session: AsyncSession, farmer_id: int) -> None:
    """Deletes a farmer."""
    result = await db_session.execute(select(Farmer).where(Farmer.id == farmer_id))
    farmer = result.scalars().first()
    if farmer:
        await db_session.delete(farmer)
        await db_session.commit()
