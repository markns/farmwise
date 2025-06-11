from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Commodity
from .schemas import CommodityCreate, CommodityUpdate


async def get(*, db_session: AsyncSession, commodity_id: int) -> Optional[Commodity]:
    """Returns a commodity based on the given commodity id."""
    result = await db_session.execute(select(Commodity).where(Commodity.id == commodity_id))
    return result.scalar_one_or_none()


async def get_by_name(*, db_session: AsyncSession, name: str) -> Optional[Commodity]:
    """Returns a commodity based on the given commodity name."""
    result = await db_session.execute(select(Commodity).where(Commodity.name == name))
    return result.scalar_one_or_none()


async def get_all(*, db_session: AsyncSession, limit: int = 100, offset: int = 0) -> Sequence[Commodity]:
    """Returns all commodities with pagination."""
    result = await db_session.execute(select(Commodity).limit(limit).offset(offset))
    return result.scalars().all()


async def count(*, db_session: AsyncSession) -> int:
    """Returns the total count of commodities."""
    from sqlalchemy import func

    result = await db_session.execute(select(func.count(Commodity.id)))
    return result.scalar_one()


async def create(*, db_session: AsyncSession, commodity_in: CommodityCreate) -> Commodity:
    """Creates a commodity."""
    commodity = Commodity(**commodity_in.model_dump())

    db_session.add(commodity)
    await db_session.commit()
    await db_session.refresh(commodity)

    return commodity


async def update(*, db_session: AsyncSession, commodity: Commodity, commodity_in: CommodityUpdate) -> Commodity:
    """Updates a commodity."""
    update_data = commodity_in.model_dump(exclude_unset=True, exclude_none=True)

    for field, value in update_data.items():
        setattr(commodity, field, value)

    await db_session.commit()
    await db_session.refresh(commodity)
    return commodity


async def delete(*, db_session: AsyncSession, commodity_id: int) -> None:
    """Deletes a commodity."""
    result = await db_session.execute(select(Commodity).where(Commodity.id == commodity_id))
    commodity = result.scalar_one_or_none()
    if commodity:
        await db_session.delete(commodity)
        await db_session.commit()
