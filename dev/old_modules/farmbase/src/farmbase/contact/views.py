from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from farmbase.database.core import DbSession
from farmbase.models import PrimaryKey

from ..exceptions.exceptions import EntityAlreadyExistsError, EntityDoesNotExistError
from ..farm.models import FarmContact, FarmSummary
from ..organization.service import CurrentOrganization
from .filterset import ContactFilterSet, ContactQueryParams
from .flows import contact_init_flow
from .memory.views import router as memory_router
from .message.views import router as message_router
from .models import (
    Contact,
)
from .runresult.views import router as runresult_router
from .schemas import (
    ContactConsentCreate,
    ContactConsentRead,
    ContactCreate,
    ContactPagination,
    ContactPatch,
    ContactRead,
)
from .service import create, create_consent, delete, get, get_by_phone_number, patch

router = APIRouter()

# Include nested routers
router.include_router(runresult_router, prefix="/{contact_id}/runresults", tags=["runresults"])
router.include_router(memory_router, prefix="/{contact_id}/memories", tags=["memories"])
router.include_router(message_router, prefix="/{contact_id}/messages", tags=["messages"])


@router.get("", response_model=ContactPagination)
async def get_contacts(
    db_session: DbSession,
    query_params: Annotated[ContactQueryParams, Query()],
):
    """Get all contacts."""
    stmt = select(Contact).options(
        selectinload(Contact.farm_associations).selectinload(FarmContact.farm), selectinload(Contact.organization)
    )
    filter_set = ContactFilterSet(db_session, stmt)
    params_d = query_params.model_dump(exclude_none=True)
    total = await filter_set.count(params_d)
    contacts = await filter_set.filter(params_d)
    return ContactPagination(
        items=[_to_contact_read(c) for c in contacts],
        items_per_page=query_params.items_per_page,
        page=query_params.page,
        total=total,
    )


def _to_contact_read(contact: Contact) -> ContactRead:
    # Build a dict of fields for ContactRead from the ORM object, excluding farms
    data: dict = {}
    for field in ContactRead.model_fields:
        if field == "farms":
            continue
        data[field] = getattr(contact, field)
    # Manually construct farm summaries with roles
    data["farms"] = [
        FarmSummary(
            id=assoc.farm.id,
            farm_name=assoc.farm.farm_name,
            location=assoc.farm.location,
            role=assoc.role,
        )
        for assoc in contact.farm_associations
    ]
    return ContactRead(**data)


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
        raise EntityAlreadyExistsError("A contact with this phone number already exists.")

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
    return _to_contact_read(contact)


@router.get(
    "/by-phone",
    response_model=ContactRead,
    summary="Get a single contact by phone number.",
)
async def get_contact_by_phone(
    db_session: DbSession,
    phone: Annotated[str, Query(description="Phone number in E.164 format")],
):
    contact = await get_by_phone_number(db_session=db_session, phone_number=phone)
    if not contact:
        raise EntityDoesNotExistError("Contact not found")

    return _to_contact_read(contact)


@router.get(
    "/{contact_id}",
    response_model=ContactRead,
    summary="Get a contact.",
)
async def get_contact(db_session: DbSession, contact_id: PrimaryKey):
    """Get a contact."""
    contact = await get(db_session=db_session, contact_id=contact_id)
    if not contact:
        raise EntityDoesNotExistError("A contact with this id does not exist.")
    return _to_contact_read(contact)


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
        raise EntityDoesNotExistError("A contact with this id does not exist.")
    contact = await patch(db_session=db_session, contact=contact, contact_in=contact_in)
    return _to_contact_read(contact)


@router.delete(
    "/{contact_id}",
    response_model=None,
    # dependencies=[Depends(PermissionsDependency([ContactUpdatePermission]))],
)
async def delete_contact(db_session: DbSession, contact_id: PrimaryKey):
    """Delete a contact."""
    contact = await get(db_session=db_session, contact_id=contact_id)
    if not contact:
        raise EntityDoesNotExistError("A contact with this id does not exist.")
    await delete(db_session=db_session, contact_id=contact_id)


@router.post(
    "/{contact_id}/consent",
    response_model=ContactConsentRead,
    summary="Create a consent record for a contact.",
)
async def create_contact_consent(
    db_session: DbSession,
    contact_id: PrimaryKey,
    consent_in: ContactConsentCreate,
):
    """Create a consent record for a contact."""
    # Verify the contact exists
    contact = await get(db_session=db_session, contact_id=contact_id)
    if not contact:
        raise EntityDoesNotExistError("A contact with this id does not exist.")

    consent = await create_consent(db_session=db_session, contact_id=contact_id, consent_in=consent_in)
    return ContactConsentRead(
        id=consent.id,
        contact_id=consent.contact_id,
        consent_type=consent.consent_type,
        consent_given=consent.consent_given,
        consent_version=consent.consent_version,
    )
