import asyncio

from pywa_async import WhatsApp
from temporalio import workflow
from temporalio.client import Client

from farmbase_workflows import workers
from farmbase_workflows.schedules import create_or_update_schedules
from farmbase_workflows.settings import settings

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    from temporalio.contrib.pydantic import pydantic_data_converter


async def main():
    # TODO: handle tls config optionally here

    client = await Client.connect(
        settings.TEMPORAL_ENDPOINT, data_converter=pydantic_data_converter
    )
    whatsapp = WhatsApp(
        phone_id=settings.WHATSAPP_PHONE_ID,
        token=settings.WHATSAPP_TOKEN,
    )

    await create_or_update_schedules(client)

    # await ensure_topics()
    await workers.run_all(client, whatsapp)


if __name__ == '__main__':
    asyncio.run(main())
