from typing import Annotated

from fastapi import APIRouter, Query

from farmbase.database.core import DbSession
from farmbase.models import PrimaryKey

from ..exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from .schemas import CommodityCreate, CommodityPagination, CommodityRead, CommodityUpdate
from .service import count, create, delete, get, get_all, get_by_name, update

router = APIRouter()


@router.get("", response_model=CommodityPagination)
async def get_commodities(
    db_session: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    items_per_page: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """Get all commodities with pagination."""
    offset = (page - 1) * items_per_page
    commodities = await get_all(db_session=db_session, limit=items_per_page, offset=offset)
    total = await count(db_session=db_session)

    return CommodityPagination(
        items=[CommodityRead.model_validate(commodity) for commodity in commodities],
        items_per_page=items_per_page,
        page=page,
        total=total,
    )


@router.post("", response_model=CommodityRead)
async def create_commodity(
    db_session: DbSession,
    commodity_in: CommodityCreate,
):
    """Create a new commodity."""
    # Check if commodity with same details already exists
    existing = await get_by_name(db_session=db_session, name=commodity_in.name)
    if existing:
        # Check if all details match (name, classification, grade, sex)
        if (
            existing.classification == commodity_in.classification
            and existing.grade == commodity_in.grade
            and existing.sex == commodity_in.sex
        ):
            raise EntityAlreadyExistsError(message="A commodity with these details already exists.")

    commodity = await create(db_session=db_session, commodity_in=commodity_in)
    return CommodityRead.model_validate(commodity)


@router.get("/{commodity_id}", response_model=CommodityRead)
async def get_commodity(
    db_session: DbSession,
    commodity_id: PrimaryKey,
):
    """Get a commodity by ID."""
    commodity = await get(db_session=db_session, commodity_id=commodity_id)
    if not commodity:
        raise EntityDoesNotExistError(message="Commodity not found.")

    return CommodityRead.model_validate(commodity)


@router.put("/{commodity_id}", response_model=CommodityRead)
async def update_commodity(
    db_session: DbSession,
    commodity_id: PrimaryKey,
    commodity_in: CommodityUpdate,
):
    """Update an existing commodity."""
    commodity = await get(db_session=db_session, commodity_id=commodity_id)
    if not commodity:
        raise EntityDoesNotExistError(message="Commodity not found.")

    commodity = await update(db_session=db_session, commodity=commodity, commodity_in=commodity_in)
    return CommodityRead.model_validate(commodity)


@router.delete("/{commodity_id}")
async def delete_commodity(
    db_session: DbSession,
    commodity_id: PrimaryKey,
):
    """Delete a commodity."""
    commodity = await get(db_session=db_session, commodity_id=commodity_id)
    if not commodity:
        raise EntityDoesNotExistError(message="Commodity not found.")

    await delete(db_session=db_session, commodity_id=commodity_id)
    return {"message": "Commodity deleted successfully"}
