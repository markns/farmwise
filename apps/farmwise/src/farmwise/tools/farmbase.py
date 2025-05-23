from agents import RunContextWrapper, function_tool
from farmbase_client import AuthenticatedClient
from farmbase_client.api.contacts import contacts_patch_contact
from farmbase_client.models import ContactPatch, ContactRead

from farmwise.dependencies import UserContext
from farmwise.settings import settings
from farmwise.tools.utils import join_with


@function_tool(
    description_override=f"""
Update a contact's details. 
Use this tool to update a users {join_with([k for k in ContactPatch.model_fields.keys()])} 
if the user mentions them in a message.
For example if a user mentions their location as a place name or as latitude,longitude coordinates, update them
using this tool.
"""
)
async def update_contact(wrapper: RunContextWrapper[UserContext], contact_in: ContactPatch) -> ContactRead:
    context = wrapper.context
    with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
        result = await contacts_patch_contact.asyncio(
            client=client,
            organization=context.contact.organization.slug,
            contact_id=context.contact.id,
            body=contact_in,
        )
        return result
