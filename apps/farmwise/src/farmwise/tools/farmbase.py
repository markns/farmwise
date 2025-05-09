from agents import RunContextWrapper, function_tool
from farmbase_client import AuthenticatedClient
from farmbase_client.api.contacts import contacts_create_contact, contacts_patch_contact
from farmbase_client.models import ContactCreate, ContactPatch, ContactRead

from farmwise.context import UserContext
from farmwise.settings import settings
from farmwise.tools.utils import copy_doc, join_with


@function_tool
@copy_doc(contacts_create_contact.asyncio)
async def create_contact(ctx: RunContextWrapper[UserContext], contact_in: ContactCreate) -> ContactRead:
    with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
        result = await contacts_create_contact.asyncio(
            client=client, organization=ctx.context.organization, body=contact_in
        )
        return result


@function_tool(
    description_override=f"""Update a contact's details. 
    Use this tool to update a users {join_with([k for k in ContactPatch.model_fields.keys()])} 
    if the user mentions them in a message."""
)
async def update_contact(ctx: RunContextWrapper[UserContext], contact_in: ContactPatch) -> ContactRead:
    with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
        result = await contacts_patch_contact.asyncio(
            client=client, organization=ctx.context.organization, contact_id=ctx.context.user_id, body=contact_in
        )
        return result
