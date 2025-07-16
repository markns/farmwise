from datetime import date, timedelta
from typing import Optional, Sequence

from sqlalchemy import func, select, text
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


async def get_market_snapshot(*, db_session: AsyncSession, market_id: int) -> Sequence[MarketPrice]:
    """Returns all prices from the last month for commodities traded in the given market."""
    one_month_ago = date.today() - timedelta(days=30)

    # Get all market prices for the market within the last 3 months
    result = await db_session.execute(
        select(MarketPrice)
        .options(selectinload(MarketPrice.market), selectinload(MarketPrice.commodity))
        .where(MarketPrice.market_id == market_id)
        .where(MarketPrice.date >= one_month_ago)
        .order_by(MarketPrice.commodity_id, MarketPrice.date)
    )

    return result.scalars().all()


async def get_markets_near_location(
    *,
    db_session: AsyncSession,
    latitude: float,
    longitude: float,
    distance_km: int = 50,
    limit: int = 100,
    offset: int = 0,
    price_within_days: int | None = None,
) -> Sequence[Market]:
    """Returns markets within `distance_km` of the given latitude and longitude using PostGIS via GeoAlchemy2."""
    # Distance in metres
    distance_m = distance_km * 1000

    # Build a POINT geometry in SRID 4326 and then transform to 3857
    # Option A: using ST_MakePoint and ST_SetSRID
    point_geom = func.ST_Transform(func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326), 3857)

    # If Market.location is stored as Geometry with SRID 4326, transform it to 3857
    market_loc_3857 = func.ST_Transform(Market.location, 3857)

    # Spatial predicate: within distance
    distance_condition = func.ST_DWithin(market_loc_3857, point_geom, distance_m)

    # Ordering by actual distance
    distance_order = func.ST_Distance(market_loc_3857, point_geom)

    # 2. Subquery: latest date per market_id in market_prices
    latest_date_sq = (
        select(MarketPrice.market_id.label("mkt_id"), func.max(MarketPrice.date).label("max_date"))
        .group_by(MarketPrice.market_id)
        .subquery()
    )

    # 3. Build main query: join Market -> latest_date_sq, filter spatially…
    stmt = (
        select(Market)
        .join(latest_date_sq, Market.id == latest_date_sq.c.mkt_id)
        .where(Market.location.isnot(None))
        .where(distance_condition)
    )

    # 4. If price_within_days is given, add condition on latest date
    if price_within_days is not None:
        # Postgres: current_date - INTERVAL 'x days'
        interval_text = text(f"INTERVAL '{price_within_days} days'")
        cutoff_expr = func.current_date() - interval_text
        stmt = stmt.where(latest_date_sq.c.max_date >= cutoff_expr)

    # 5. Order, paginate
    stmt = stmt.order_by(distance_order).limit(limit).offset(offset)

    result = await db_session.execute(stmt)
    return result.scalars().all()


async def count_markets_near_location(*, db_session: AsyncSession, latitude: float, longitude: float) -> int:
    """Returns the count of markets within 50km of the given latitude and longitude."""
    # Create a point from the provided coordinates
    point_wkt = f"POINT({longitude} {latitude})"

    # Count markets within 50km
    distance_condition = text(
        f"ST_DWithin(ST_Transform(location, 3857), ST_Transform(ST_GeomFromText('{point_wkt}', 4326), 3857), 50000)"
    )

    result = await db_session.execute(
        select(func.count(Market.id)).where(Market.location.isnot(None)).where(distance_condition)
    )

    return result.scalar_one()
