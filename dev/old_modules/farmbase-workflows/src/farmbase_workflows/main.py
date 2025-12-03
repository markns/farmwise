import asyncio

from pywa_async import WhatsApp
from temporalio import workflow
from temporalio.client import Client
from temporalio.service import TLSConfig

from farmbase_workflows import workers
from farmbase_workflows.schedules import create_or_update_schedules
from farmbase_workflows.settings import settings

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    from temporalio.contrib.pydantic import pydantic_data_converter


async def get_temporal_client() -> Client:
    if any([settings.TEMPORAL_TLS_CA_DATA, settings.TEMPORAL_TLS_CERT_DATA, settings.TEMPORAL_TLS_KEY_DATA]):
        tls = TLSConfig(server_root_ca_cert=settings.TEMPORAL_TLS_CA_DATA,
                        client_cert=settings.TEMPORAL_TLS_CERT_DATA,
                        client_private_key=settings.TEMPORAL_TLS_KEY_DATA)
    else:
        tls = False

    client: Client = await Client.connect(settings.TEMPORAL_ENDPOINT,
                                          tls=tls,
                                          data_converter=pydantic_data_converter)
    return client


async def main():
    client = await get_temporal_client()
    whatsapp = WhatsApp(
        phone_id=settings.WHATSAPP_PHONE_ID,
        token=settings.WHATSAPP_TOKEN,
    )

    await create_or_update_schedules(client)

    # await ensure_topics()
    await workers.run_all(client, whatsapp)


if __name__ == '__main__':
    asyncio.run(main())
