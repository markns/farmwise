from agents import RunContextWrapper, function_tool
from farmbase_client import AuthenticatedClient
from farmbase_client.api.farmers import farmers_create_farmer, farmers_update_farmer
from farmbase_client.models import FarmerCreate, FarmerPatch, FarmerRead

from farmwise.context import UserContext
from farmwise.settings import settings
from farmwise.tools.utils import copy_doc


@function_tool
@copy_doc(farmers_create_farmer.asyncio)
async def create_farmer(ctx: RunContextWrapper[UserContext], farmer_in: FarmerCreate) -> FarmerRead:
    with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
        result = await farmers_create_farmer.asyncio(
            client=client, organization=ctx.context.organization, body=farmer_in
        )
        return result


@function_tool
@copy_doc(farmers_update_farmer.asyncio)
async def update_farmer(ctx: RunContextWrapper[UserContext], farmer_in: FarmerPatch) -> FarmerRead:
    with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
        result = await farmers_update_farmer.asyncio(
            client=client, organization=ctx.context.organization, farmer_id=ctx.context.user_id, body=farmer_in
        )
        return result
