from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from farmbase.database.core import DbSession
from farmbase.models import PrimaryKey

from . import service
from .filterset import (
    FarmContactFilterSet,
    FarmContactQueryParams,
    FarmFilterSet,
    FarmQueryParams,
)
from .models import (
    Farm,
    FarmContact,
    FarmContactCreate,
    FarmContactPagination,
    FarmContactRead,
    FarmContactUpdate,
    FarmCreate,
    FarmPagination,
    FarmRead,
    FarmUpdate,
)

router = APIRouter()


# Farm endpoints
@router.get("", response_model=FarmPagination)
async def list_farms(
    db_session: DbSession,
    query_params: Annotated[FarmQueryParams, Query()],
):
    """List farms."""
    stmt = select(Farm).options(selectinload(Farm.contact_associations).selectinload(FarmContact.contact))
    filter_set = FarmFilterSet(db_session, stmt)
    params_d = query_params.model_dump(exclude_none=True)
    total = await filter_set.count(params_d)
    farms = await filter_set.filter(params_d)
    return FarmPagination(
        items=farms,
        items_per_page=query_params.items_per_page,
        page=query_params.page,
        total=total,
    )


@router.post("", response_model=FarmRead)
async def create_farm(
    db_session: DbSession,
    farm_in: FarmCreate,
):
    """Create a new farm."""
    return await service.create_farm(db_session=db_session, farm_in=farm_in)


@router.get("/{farm_id}", response_model=FarmRead)
async def get_farm(
    db_session: DbSession,
    farm_id: PrimaryKey,
):
    """Get a farm by ID."""
    farm = await service.get_farm(db_session=db_session, farm_id=farm_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Farm not found."}],
        )
    return farm


@router.put("/{farm_id}", response_model=FarmRead)
async def update_farm(
    db_session: DbSession,
    farm_id: PrimaryKey,
    farm_in: FarmUpdate,
):
    """Update an existing farm."""
    farm = await service.get_farm(db_session=db_session, farm_id=farm_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Farm not found."}],
        )
    return await service.update_farm(db_session=db_session, farm=farm, farm_in=farm_in)


@router.delete("/{farm_id}", response_model=None)
async def delete_farm(
    db_session: DbSession,
    farm_id: PrimaryKey,
):
    """Delete a farm by ID."""
    farm = await service.get_farm(db_session=db_session, farm_id=farm_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Farm not found."}],
        )
    await service.delete_farm(db_session=db_session, farm_id=farm_id)


# Farm Contact endpoints
@router.get("/contacts", response_model=FarmContactPagination)
async def list_farm_contacts(
    db_session: DbSession,
    query_params: Annotated[FarmContactQueryParams, Query()],
):
    """List farm contacts."""
    stmt = select(FarmContact).options(selectinload(FarmContact.contact))
    filter_set = FarmContactFilterSet(db_session, stmt)
    params_d = query_params.model_dump(exclude_none=True)
    total = await filter_set.count(params_d)
    farm_contacts = await filter_set.filter(params_d)
    return FarmContactPagination(
        items=farm_contacts,
        items_per_page=query_params.items_per_page,
        page=query_params.page,
        total=total,
    )


@router.post("/contacts", response_model=FarmContactRead)
async def create_farm_contact(
    db_session: DbSession,
    farm_contact_in: FarmContactCreate,
):
    """Create a new farm contact."""
    return await service.create_farm_contact(db_session=db_session, farm_contact_in=farm_contact_in)


@router.get("/contacts/{farm_contact_id}", response_model=FarmContactRead)
async def get_farm_contact(
    db_session: DbSession,
    farm_contact_id: PrimaryKey,
):
    """Get a farm contact by ID."""
    farm_contact = await service.get_farm_contact(db_session=db_session, farm_contact_id=farm_contact_id)
    if not farm_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Farm contact not found."}],
        )
    return farm_contact


@router.put("/contacts/{farm_contact_id}", response_model=FarmContactRead)
async def update_farm_contact(
    db_session: DbSession,
    farm_contact_id: PrimaryKey,
    farm_contact_in: FarmContactUpdate,
):
    """Update an existing farm contact."""
    farm_contact = await service.get_farm_contact(db_session=db_session, farm_contact_id=farm_contact_id)
    if not farm_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Farm contact not found."}],
        )
    return await service.update_farm_contact(
        db_session=db_session, farm_contact=farm_contact, farm_contact_in=farm_contact_in
    )


@router.delete("/contacts/{farm_contact_id}", response_model=None)
async def delete_farm_contact(
    db_session: DbSession,
    farm_contact_id: PrimaryKey,
):
    """Delete a farm contact by ID."""
    farm_contact = await service.get_farm_contact(db_session=db_session, farm_contact_id=farm_contact_id)
    if not farm_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Farm contact not found."}],
        )
    await service.delete_farm_contact(db_session=db_session, farm_contact_id=farm_contact_id)
