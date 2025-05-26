from agents import RunContextWrapper, function_tool
from farmbase_client import AuthenticatedClient
from farmbase_client.api.contacts import contacts_patch_contact
from farmbase_client.api.farms import farms_create_farm
from farmbase_client.models import ContactPatch, ContactRead, FarmCreate, FarmRead

from farmwise.dependencies import UserContext
from farmwise.settings import settings
from farmwise.tools.utils import join_with


@function_tool(
    description_override=f"""
Update a contact's details. 
Use this tool to update a users {join_with([k for k in ContactPatch.model_fields.keys()])} 
if the user mentions them in a message.
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


@function_tool(
    description_override="""
Create a farm with an optional location, and associated contacts
"""
)
async def create_farm(wrapper: RunContextWrapper[UserContext], farm_create: FarmCreate) -> FarmRead:
    context = wrapper.context

    with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
        result = await farms_create_farm.asyncio(
            client=client,
            organization=context.contact.organization.slug,
            body=farm_create,
        )
        return result
