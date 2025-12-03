import asyncio

from loguru import logger
from pywa_async import WhatsApp
from pywa_async.types import FlowCategory

from farmwise.settings import settings
from farmwise.whatsapp.flows.edit_profile.flow import FLOW_ENDPOINT, FLOW_NAME, build_flow


async def create_or_update_flows(wa: WhatsApp):
    flows = await wa.get_flows()
    logger.info(flows)

    flows = await wa.get_flows()
    logger.info(flows)
    flow_id_map = {flow.name: flow.id for flow in flows}
    logger.info(flow_id_map)

    if FLOW_NAME not in flow_id_map:
        flow = await wa.create_flow(name=FLOW_NAME, categories=[FlowCategory.CUSTOMER_SUPPORT])
    else:
        flow = await wa.get_flow(flow_id=flow_id_map[FLOW_NAME])
        flow_assets = await flow.get_assets()
        logger.info(flow_assets)
        for asset in flow_assets:
            if asset.type == "FLOW_JSON":
                asset.url
                # todo: diff with existing and only update if changed? How to handle versioning/ published?

        new_json = build_flow()

        res = await flow.update_json(flow_json=new_json)
        await flow.publish()

    await flow.update_metadata(endpoint_uri=f"{settings.WHATSAPP_CALLBACK_URL}{FLOW_ENDPOINT}")

    if not res:
        logger.error("Validation errors:")
        for error in res.validation_errors:
            logger.error(error)


async def manage_flows():
    from farmwise.app import wa

    await create_or_update_flows(wa)


if __name__ == "__main__":
    asyncio.run(manage_flows())
