from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Market, MarketPrice
from .schemas import MarketCreate, MarketPriceCreate, MarketPriceUpdate, MarketUpdate


# Market service functions
async def get_market(*, db_session: AsyncSession, market_id: int) -> Optional[Market]:
    """Returns a market based on the given market id."""
    result = await db_session.execute(select(Market).where(Market.id == market_id))
    return result.scalar_one_or_none()


async def get_market_by_name(*, db_session: AsyncSession, name: str) -> Optional[Market]:
    """Returns a market based on the given market name."""
    result = await db_session.execute(select(Market).where(Market.name == name))
    return result.scalar_one_or_none()


async def get_all_markets(*, db_session: AsyncSession, limit: int = 100, offset: int = 0) -> Sequence[Market]:
    """Returns all markets with pagination."""
    result = await db_session.execute(select(Market).limit(limit).offset(offset))
    return result.scalars().all()


async def count_markets(*, db_session: AsyncSession) -> int:
    """Returns the total count of markets."""
    from sqlalchemy import func

    result = await db_session.execute(select(func.count(Market.id)))
    return result.scalar_one()


async def create_market(*, db_session: AsyncSession, market_in: MarketCreate) -> Market:
    """Creates a market."""
    market = Market(**market_in.model_dump())

    db_session.add(market)
    await db_session.commit()
    await db_session.refresh(market)

    return market


async def update_market(*, db_session: AsyncSession, market: Market, market_in: MarketUpdate) -> Market:
    """Updates a market."""
    update_data = market_in.model_dump(exclude_unset=True, exclude_none=True)

    for field, value in update_data.items():
        setattr(market, field, value)

    await db_session.commit()
    await db_session.refresh(market)
    return market


async def delete_market(*, db_session: AsyncSession, market_id: int) -> None:
    """Deletes a market."""
    result = await db_session.execute(select(Market).where(Market.id == market_id))
    market = result.scalar_one_or_none()
    if market:
        await db_session.delete(market)
        await db_session.commit()


# MarketPrice service functions
async def get_market_price(*, db_session: AsyncSession, market_price_id: int) -> Optional[MarketPrice]:
    """Returns a market price based on the given market price id."""
    result = await db_session.execute(
        select(MarketPrice)
        .options(selectinload(MarketPrice.market), selectinload(MarketPrice.commodity))
        .where(MarketPrice.id == market_price_id)
    )
    return result.scalar_one_or_none()


async def get_all_market_prices(
    *, db_session: AsyncSession, limit: int = 100, offset: int = 0
) -> Sequence[MarketPrice]:
    """Returns all market prices with pagination."""
    result = await db_session.execute(
        select(MarketPrice)
        .options(selectinload(MarketPrice.market), selectinload(MarketPrice.commodity))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_market_prices_by_market(
    *, db_session: AsyncSession, market_id: int, limit: int = 100, offset: int = 0
) -> Sequence[MarketPrice]:
    """Returns market prices for a specific market."""
    result = await db_session.execute(
        select(MarketPrice)
        .options(selectinload(MarketPrice.market), selectinload(MarketPrice.commodity))
        .where(MarketPrice.market_id == market_id)
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_market_prices_by_commodity(
    *, db_session: AsyncSession, commodity_id: int, limit: int = 100, offset: int = 0
) -> Sequence[MarketPrice]:
    """Returns market prices for a specific commodity."""
    result = await db_session.execute(
        select(MarketPrice)
        .options(selectinload(MarketPrice.market), selectinload(MarketPrice.commodity))
        .where(MarketPrice.commodity_id == commodity_id)
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def count_market_prices(*, db_session: AsyncSession) -> int:
    """Returns the total count of market prices."""
    from sqlalchemy import func

    result = await db_session.execute(select(func.count(MarketPrice.id)))
    return result.scalar_one()


async def create_market_price(*, db_session: AsyncSession, market_price_in: MarketPriceCreate) -> MarketPrice:
    """Creates a market price."""
    market_price = MarketPrice(**market_price_in.model_dump())

    db_session.add(market_price)
    await db_session.commit()
    await db_session.refresh(market_price)

    return await get_market_price(db_session=db_session, market_price_id=market_price.id)


async def update_market_price(
    *, db_session: AsyncSession, market_price: MarketPrice, market_price_in: MarketPriceUpdate
) -> MarketPrice:
    """Updates a market price."""
    update_data = market_price_in.model_dump(exclude_unset=True, exclude_none=True)

    for field, value in update_data.items():
        setattr(market_price, field, value)

    await db_session.commit()
    await db_session.refresh(market_price)
    return market_price


async def delete_market_price(*, db_session: AsyncSession, market_price_id: int) -> None:
    """Deletes a market price."""
    result = await db_session.execute(select(MarketPrice).where(MarketPrice.id == market_price_id))
    market_price = result.scalar_one_or_none()
    if market_price:
        await db_session.delete(market_price)
        await db_session.commit()
