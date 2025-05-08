from fastapi import APIRouter

from farmbase.database.core import DbSession
from farmbase.database.service import CommonParameters, search_filter_sort_paginate
from farmbase.models import OrganizationSlug, PrimaryKey

from ..exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from .flows import farmer_init_flow
from .models import (
    FarmerCreate,
    FarmerPagination,
    FarmerPatch,
    FarmerRead,
)
from .service import create, delete, get, get_by_phone_number, patch

router = APIRouter()


@router.get("", response_model=FarmerPagination)
async def get_farmers(common: CommonParameters):
    """Get all farmers."""
    return await search_filter_sort_paginate(model="Farmer", **common)


@router.post(
    "",
    response_model=FarmerRead,
    summary="Create a new farmer.",
    # dependencies=[Depends(PermissionsDependency([FarmerCreatePermission]))],
)
async def create_farmer(
    db_session: DbSession,
    organization: OrganizationSlug,
    farmer_in: FarmerCreate,
):
    """Create a new farmer."""
    farmer = await get_by_phone_number(db_session=db_session, phone_number=farmer_in.phone_number)
    if farmer:
        raise EntityAlreadyExistsError(message="A farmer with this phone number already exists.")

    # if farmer_in.id and await get(db_session=db_session, farmer_id=farmer_in.id):
    #     raise ValueError("A farmer with this id already exists.")
    # raise ValidationError.from_exception_data(
    #     "FarmerCreate",
    #     [
    #         {
    #             "loc": ("id",),
    #             "msg": "A farmer with this id already exists.",
    #             "type": "value_error.already_exists",
    #         }
    #     ],
    # )

    farmer = await create(db_session=db_session, farmer_in=farmer_in)
    await farmer_init_flow(db_session=db_session, farmer_id=farmer.id, organization_slug=organization)
    return farmer


@router.get(
    "/{farmer_id}",
    response_model=FarmerRead,
    summary="Get a farmer.",
)
async def get_farmer(db_session: DbSession, farmer_id: PrimaryKey):
    """Get a farmer."""
    farmer = await get(db_session=db_session, farmer_id=farmer_id)
    if not farmer:
        raise EntityDoesNotExistError(message="A farmer with this id does not exist.")
    return farmer


@router.patch(
    "/{farmer_id}",
    response_model=FarmerRead,
    # dependencies=[Depends(PermissionsDependency([FarmerUpdatePermission]))],
)
async def update_farmer(
    db_session: DbSession,
    farmer_id: PrimaryKey,
    farmer_in: FarmerPatch,
):
    """Patch a farmer."""
    farmer = await get(db_session=db_session, farmer_id=farmer_id)
    if not farmer:
        raise EntityDoesNotExistError(message="A farmer with this id does not exist.")
    farmer = await patch(db_session=db_session, farmer=farmer, farmer_in=farmer_in)
    return farmer


@router.delete(
    "/{farmer_id}",
    response_model=None,
    # dependencies=[Depends(PermissionsDependency([FarmerUpdatePermission]))],
)
async def delete_farmer(db_session: DbSession, farmer_id: PrimaryKey):
    """Delete a farmer."""
    farmer = await get(db_session=db_session, farmer_id=farmer_id)
    if not farmer:
        raise EntityDoesNotExistError(message="A farmer with this id does not exist.")
    await delete(db_session=db_session, farmer_id=farmer_id)
