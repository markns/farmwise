from agents import RunContextWrapper, function_tool
from farmbase_client.api.contacts import contacts_patch_contact
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
    NoteRead,
)

from farmwise.context import UserContext
from farmwise.farmbase import FarmbaseClient
from farmwise.utils import join_with


@function_tool(
    description_override=f"""
Update a contact's details. 
Use this tool to update a users {join_with([k for k in ContactPatch.model_fields.keys()])} 
if the user mentions them in a message.
"""
)
async def update_contact(wrapper: RunContextWrapper[UserContext], contact_in: ContactPatch) -> ContactRead:
    context = wrapper.context
    async with FarmbaseClient() as client:
        result = await contacts_patch_contact.asyncio(
            client=client.raw,
            organization=context.contact.organization.slug,
            contact_id=context.contact.id,
            body=contact_in,
        )
        return result


@function_tool(
    description_override="""
Create a farm with an optional location, and associated contacts
"""
)
async def create_farm(wrapper: RunContextWrapper[UserContext], farm_create: FarmCreate) -> FarmRead:
    context = wrapper.context

    async with FarmbaseClient() as client:
        result = await farms_create_farm.asyncio(
            client=client.raw,
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

    async with FarmbaseClient() as client:
        result = await notes_create_note.asyncio(
            client=client.raw,
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
    async with FarmbaseClient() as client:
        result = await markets_get_markets.asyncio(
            client=client.raw, items_per_page=10, latitude=latitude, longitude=longitude, price_within_days=30
        )
        return result


@function_tool(
    description_override="""
Get a snapshot of market prices for a given market
"""
)
async def get_market_price_snapshot(_: RunContextWrapper[UserContext], market_id: int) -> MarketSnapshotRead:
    async with FarmbaseClient() as client:
        result = await markets_get_market_snapshot_endpoint.asyncio(client=client.raw, market_id=market_id)
        return result
