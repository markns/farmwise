from typing import Any, Coroutine

from agents import RunContextWrapper, function_tool
from fastapi.exceptions import RequestValidationError

from farmbase_client.api.contacts import contacts_patch_contact, contacts_create_contact_consent
from farmbase_client.api.farms import farms_create_farm
from farmbase_client.api.markets import markets_get_market_snapshot_endpoint, markets_get_markets
from farmbase_client.api.notes import notes_create_note
from farmbase_client.models import (
    ContactPatch,
    ContactRead,
    FarmCreate,
    FarmRead,
    MarketPagination,
    MarketSnapshotRead,
    NoteCreate,
    NoteRead, ContactConsentCreate, ContactConsentRead,
)

from farmwise.context import UserContext
from farmwise.farmbase import farmbase_api_client
from farmwise.utils import join_with


@function_tool(
    description_override=f"""
Update a contact's details. 
Use this tool to update a users {join_with([k for k in ContactPatch.model_fields.keys()])} 
if the user mentions them in a message.
"""
)
async def update_contact(wrapper: RunContextWrapper[UserContext], contact_in: ContactPatch) -> ContactRead:
    contact = wrapper.context.contact
    result = await contacts_patch_contact.asyncio(
        client=farmbase_api_client,
        organization=contact.organization.slug,
        contact_id=contact.id,
        body=contact_in,
    )
    return result

@function_tool
async def data_collection_consent(wrapper: RunContextWrapper[UserContext]) -> ContactConsentRead:
    """
    Use this tool when the contact consents for data collection
    """
    contact = wrapper.context.contact
    return await contacts_create_contact_consent.asyncio(
        client=farmbase_api_client,
        organization=contact.organization.slug,
        contact_id=contact.id,
        body= ContactConsentCreate(
            consent_type="data_collection",
            consent_given=True,
            consent_version="v1"
        )
    )

@function_tool(
    description_override="""
Create a farm with an optional location, and associated contacts
"""
)
async def create_farm(wrapper: RunContextWrapper[UserContext], farm_create: FarmCreate) -> FarmRead:
    context = wrapper.context

    result = await farms_create_farm.asyncio(
        client=farmbase_api_client,
        organization=context.contact.organization.slug,
        body=farm_create,
    )
    return result


@function_tool(
    description_override="""
Create a note with an optional location. Use the current contact's ID for the contact_id_created_by field.
"""
)
async def create_note(wrapper: RunContextWrapper[UserContext], note_create: NoteCreate) -> NoteRead:
    context = wrapper.context

    result = await notes_create_note.asyncio(
        client=farmbase_api_client,
        organization=context.contact.organization.slug,
        body=note_create,
    )
    return result


@function_tool(
    description_override="""
Get the closest markets to a given coordinate
"""
)
async def get_markets(_: RunContextWrapper[UserContext], latitude: float, longitude: float) -> MarketPagination:
    result = await markets_get_markets.asyncio(
        client=farmbase_api_client, items_per_page=10, latitude=latitude, longitude=longitude, price_within_days=30
    )
    return result


@function_tool(
    description_override="""
Get a snapshot of market prices for a given market
"""
)
async def get_market_price_snapshot(_: RunContextWrapper[UserContext], market_id: int) -> MarketSnapshotRead:
    result = await markets_get_market_snapshot_endpoint.asyncio(client=farmbase_api_client, market_id=market_id)
    return result
