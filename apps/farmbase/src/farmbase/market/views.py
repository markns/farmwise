from typing import Annotated

from fastapi import APIRouter, Query

from farmbase.database.core import DbSession
from farmbase.models import PrimaryKey

from ..exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from .schemas import (
    CommodityPriceSnapshot,
    MarketCreate,
    MarketPagination,
    MarketPriceCreate,
    MarketPricePagination,
    MarketPriceRead,
    MarketPriceUpdate,
    MarketRead,
    MarketSnapshotRead,
    MarketUpdate,
)
from .service import (
    count_market_prices,
    create_market,
    create_market_price,
    delete_market,
    delete_market_price,
    get_all_market_prices,
    get_all_markets,
    get_market,
    get_market_by_name,
    get_market_price,
    get_market_prices_by_commodity,
    get_market_prices_by_market,
    get_market_snapshot,
    get_markets_near_location,
    update_market,
    update_market_price,
)

router = APIRouter()
price_router = APIRouter()

def _to_market_price_read(market_price) -> MarketPriceRead:
    """Convert MarketPrice ORM object to MarketPriceRead schema."""
    return MarketPriceRead(
        id=market_price.id,
        price_date=market_price.date,
        supply_volume=market_price.supply_volume,
        wholesale_price=market_price.wholesale_price,
        wholesale_unit=market_price.wholesale_unit,
        wholesale_ccy=str(market_price.wholesale_ccy) if market_price.wholesale_ccy else None,
        retail_price=market_price.retail_price,
        retail_unit=market_price.retail_unit,
        retail_ccy=str(market_price.retail_ccy) if market_price.retail_ccy else None,
        market=MarketRead.model_validate(market_price.market),
        commodity=market_price.commodity,
    )


# Market endpoints
@router.get("", response_model=MarketPagination)
async def get_markets(
    db_session: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    items_per_page: Annotated[int, Query(ge=1, le=100)] = 50,
    latitude: Annotated[float, Query(ge=-90, le=90)] = None,
    longitude: Annotated[float, Query(ge=-180, le=180)] = None,
    price_within_days: int | None = None,
):
    """Get all markets with pagination. Optionally filter by location within 50km of given lat/lon
    and with prices within a given recency"""
    offset = (page - 1) * items_per_page

    if latitude is not None and longitude is not None:
        markets = await get_markets_near_location(
            db_session=db_session,
            latitude=latitude,
            longitude=longitude,
            limit=items_per_page,
            offset=offset,
            price_within_days=price_within_days,
        )
    else:
        markets = await get_all_markets(db_session=db_session, limit=items_per_page, offset=offset)

    return MarketPagination(
        items=[MarketRead.model_validate(market) for market in markets],
        items_per_page=items_per_page,
        page=page,
        total=len(markets),
    )


@router.post("", response_model=MarketRead)
async def create_market_endpoint(
    db_session: DbSession,
    market_in: MarketCreate,
):
    """Create a new market."""
    existing = await get_market_by_name(db_session=db_session, name=market_in.name)
    if existing:
        raise EntityAlreadyExistsError(message="A market with this name already exists.")

    market = await create_market(db_session=db_session, market_in=market_in)
    return MarketRead.model_validate(market)


@router.get("/{market_id}", response_model=MarketRead)
async def get_market_endpoint(
    db_session: DbSession,
    market_id: PrimaryKey,
):
    """Get a market by ID."""
    market = await get_market(db_session=db_session, market_id=market_id)
    if not market:
        raise EntityDoesNotExistError(message="Market not found.")

    return MarketRead.model_validate(market)


@router.put("/{market_id}", response_model=MarketRead)
async def update_market_endpoint(
    db_session: DbSession,
    market_id: PrimaryKey,
    market_in: MarketUpdate,
):
    """Update an existing market."""
    market = await get_market(db_session=db_session, market_id=market_id)
    if not market:
        raise EntityDoesNotExistError(message="Market not found.")

    market = await update_market(db_session=db_session, market=market, market_in=market_in)
    return MarketRead.model_validate(market)


@router.delete("/{market_id}")
async def delete_market_endpoint(
    db_session: DbSession,
    market_id: PrimaryKey,
):
    """Delete a market."""
    market = await get_market(db_session=db_session, market_id=market_id)
    if not market:
        raise EntityDoesNotExistError(message="Market not found.")

    await delete_market(db_session=db_session, market_id=market_id)
    return {"message": "Market deleted successfully"}


@router.get("/{market_id}/snapshot", response_model=MarketSnapshotRead)
async def get_market_snapshot_endpoint(
    db_session: DbSession,
    market_id: PrimaryKey,
):
    """Get market snapshot with latest prices (3 months) for each commodity traded in this market."""
    market = await get_market(db_session=db_session, market_id=market_id)
    if not market:
        raise EntityDoesNotExistError(message="Market not found.")

    market_prices = await get_market_snapshot(db_session=db_session, market_id=market_id)

    # Group prices by commodity
    from collections import defaultdict

    grouped_prices = defaultdict(list)
    for price in market_prices:
        grouped_prices[price.commodity_id].append(price)

    # Create commodity snapshots
    commodity_snapshots = []
    for commodity_id, prices in grouped_prices.items():
        # Sort prices by date
        prices.sort(key=lambda p: p.date or "")

        # Extract the commodity (all prices have the same commodity)
        commodity = prices[0].commodity

        # Get consistent units and currency from the first non-null entry
        retail_unit = None
        retail_ccy = None

        for price in prices:
            if not retail_unit and price.retail_unit:
                retail_unit = price.retail_unit
            if not retail_ccy and price.retail_ccy:
                retail_ccy = str(price.retail_ccy)

        commodity_snapshot = CommodityPriceSnapshot(
            commodity=commodity,
            price_date=[price.date for price in prices],
            supply_volume=[price.supply_volume for price in prices],
            retail_price=[price.retail_price for price in prices],
            retail_unit=retail_unit,
            retail_ccy=retail_ccy,
        )
        commodity_snapshots.append(commodity_snapshot)

    return MarketSnapshotRead(
        market=MarketRead.model_validate(market),
        latest_prices=commodity_snapshots,
    )


# Market price endpoints
@price_router.get("", response_model=MarketPricePagination)
async def get_market_prices(
    db_session: DbSession,
    market_id: Annotated[int, Query()] = None,
    commodity_id: Annotated[int, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    items_per_page: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """Get market prices with optional filtering by market or commodity."""
    offset = (page - 1) * items_per_page

    if not market_id and not commodity_id:
        raise Exception("One of market_id and commodity_id must be set")
    if market_id:
        market_prices = await get_market_prices_by_market(
            db_session=db_session, market_id=market_id, limit=items_per_page, offset=offset
        )
    elif commodity_id:
        market_prices = await get_market_prices_by_commodity(
            db_session=db_session, commodity_id=commodity_id, limit=items_per_page, offset=offset
        )

    total = await count_market_prices(db_session=db_session)

    return MarketPricePagination(
        items=[_to_market_price_read(price) for price in market_prices],
        items_per_page=items_per_page,
        page=page,
        total=total,
    )

#
# @router.post("/prices", response_model=MarketPriceRead)
# async def create_market_price_endpoint(
#     db_session: DbSession,
#     market_price_in: MarketPriceCreate,
# ):
#     """Create a new market price."""
#     # Verify market exists
#     market = await get_market(db_session=db_session, market_id=market_price_in.market_id)
#     if not market:
#         raise EntityDoesNotExistError(message="Market not found.")
#
#     # Verify commodity exists
#     from ..commodity.service import get as get_commodity
#
#     commodity = await get_commodity(db_session=db_session, commodity_id=market_price_in.commodity_id)
#     if not commodity:
#         raise EntityDoesNotExistError(message="Commodity not found.")
#
#     market_price = await create_market_price(db_session=db_session, market_price_in=market_price_in)
#     return _to_market_price_read(market_price)


# @router.get("/prices/{market_price_id}", response_model=MarketPriceRead)
# async def get_market_price_endpoint(
#     db_session: DbSession,
#     market_price_id: PrimaryKey,
# ):
#     """Get a market price by ID."""
#     market_price = await get_market_price(db_session=db_session, market_price_id=market_price_id)
#     if not market_price:
#         raise EntityDoesNotExistError(message="Market price not found.")
#
#     return _to_market_price_read(market_price)


# @router.put("/prices/{market_price_id}", response_model=MarketPriceRead)
# async def update_market_price_endpoint(
#     db_session: DbSession,
#     market_price_id: PrimaryKey,
#     market_price_in: MarketPriceUpdate,
# ):
#     """Update an existing market price."""
#     market_price = await get_market_price(db_session=db_session, market_price_id=market_price_id)
#     if not market_price:
#         raise EntityDoesNotExistError(message="Market price not found.")
#
#     market_price = await update_market_price(
#         db_session=db_session, market_price=market_price, market_price_in=market_price_in
#     )
#     return _to_market_price_read(market_price)
#
#
# @router.delete("/prices/{market_price_id}")
# async def delete_market_price_endpoint(
#     db_session: DbSession,
#     market_price_id: PrimaryKey,
# ):
#     """Delete a market price."""
#     market_price = await get_market_price(db_session=db_session, market_price_id=market_price_id)
#     if not market_price:
#         raise EntityDoesNotExistError(message="Market price not found.")
#
#     await delete_market_price(db_session=db_session, market_price_id=market_price_id)
#     return {"message": "Market price deleted successfully"}
