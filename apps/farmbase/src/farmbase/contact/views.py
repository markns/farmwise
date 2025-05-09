from fastapi import APIRouter

from farmbase.database.core import DbSession
from farmbase.database.service import CommonParameters, search_filter_sort_paginate
from farmbase.models import PrimaryKey

from ..exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from ..organization.service import CurrentOrganization
from .flows import contact_init_flow
from .models import (
    ContactCreate,
    ContactPagination,
    ContactPatch,
    ContactRead,
)
from .service import create, delete, get, get_by_phone_number, get_or_create, patch

router = APIRouter()


@router.get("", response_model=ContactPagination)
async def get_contacts(common: CommonParameters):
    """Get all contacts."""
    return await search_filter_sort_paginate(model="Contact", **common)


@router.post(
    "",
    response_model=ContactRead,
    summary="Create a new contact.",
    # dependencies=[Depends(PermissionsDependency([ContactCreatePermission]))],
)
async def create_contact(
    db_session: DbSession,
    organization: CurrentOrganization,
    contact_in: ContactCreate,
):
    """Create a new contact."""
    contact = await get_by_phone_number(db_session=db_session, phone_number=contact_in.phone_number)
    if contact:
        raise EntityAlreadyExistsError(message="A contact with this phone number already exists.")

    # TODO: how to handle sqlalchemy.exc.IntegrityError: (sqlalchemy.dialects.postgresql.asyncpg.IntegrityError) <class 'asyncpg.exceptions.UniqueViolationError'>: duplicate key value violates unique constraint "contact_pkey"
    #  DETAIL:  Key (id)=(1) already exists.
    # if contact_in.id and await get(db_session=db_session, contact_id=contact_in.id):
    #     raise ValueError("A contact with this id already exists.")
    # raise ValidationError.from_exception_data(
    #     "ContactCreate",
    #     [
    #         {
    #             "loc": ("id",),
    #             "msg": "A contact with this id already exists.",
    #             "type": "value_error.already_exists",
    #         }
    #     ],
    # )
    contact = await create(db_session=db_session, contact_in=contact_in, organization=organization)
    await contact_init_flow(db_session=db_session, contact_id=contact.id, organization=organization)
    return contact


@router.put(
    "",
    response_model=ContactRead,
    summary="Get or create a new contact.",
    # dependencies=[Depends(PermissionsDependency([ContactCreatePermission]))],
)
async def get_or_create_contact(
    db_session: DbSession,
    organization: CurrentOrganization,
    contact_in: ContactCreate,
):
    return await get_or_create(db_session=db_session, organization=organization, contact_in=contact_in)


@router.get(
    "/{contact_id}",
    response_model=ContactRead,
    summary="Get a contact.",
)
async def get_contact(db_session: DbSession, contact_id: PrimaryKey):
    """Get a contact."""
    contact = await get(db_session=db_session, contact_id=contact_id)
    if not contact:
        raise EntityDoesNotExistError(message="A contact with this id does not exist.")
    return contact


@router.patch(
    "/{contact_id}",
    response_model=ContactRead,
    # dependencies=[Depends(PermissionsDependency([ContactUpdatePermission]))],
)
async def patch_contact(
    db_session: DbSession,
    contact_id: PrimaryKey,
    contact_in: ContactPatch,
):
    """Update an existing contact with partial data."""
    contact = await get(db_session=db_session, contact_id=contact_id)
    if not contact:
        raise EntityDoesNotExistError(message="A contact with this id does not exist.")
    contact = await patch(db_session=db_session, contact=contact, contact_in=contact_in)
    return contact


@router.delete(
    "/{contact_id}",
    response_model=None,
    # dependencies=[Depends(PermissionsDependency([ContactUpdatePermission]))],
)
async def delete_contact(db_session: DbSession, contact_id: PrimaryKey):
    """Delete a contact."""
    contact = await get(db_session=db_session, contact_id=contact_id)
    if not contact:
        raise EntityDoesNotExistError(message="A contact with this id does not exist.")
    await delete(db_session=db_session, contact_id=contact_id)
