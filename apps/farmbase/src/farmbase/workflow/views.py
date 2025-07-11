import traceback
from datetime import date

from fastapi import APIRouter, HTTPException
from loguru import logger
from temporalio import workflow
from temporalio.client import Client, WorkflowFailureError
from temporalio.service import TLSConfig

from farmbase.config import settings

with workflow.unsafe.imports_passed_through():
    from temporalio.contrib.pydantic import pydantic_data_converter

router = APIRouter()


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


@router.post("/weather-forecast")
async def weather_forecast():
    client = await get_temporal_client()
    try:
        result = await client.start_workflow(
            "weather-forecast",
            id=f"weather-forecast-{date.today()}",
            task_queue="weather-task-queue",
        )

        logger.info(f"Result: {result}")
        return {"success": True, "workflow_id": result.id}

    except WorkflowFailureError as e:
        logger.error("Got expected exception: ", traceback.format_exc())
        raise HTTPException(status_code=500, detail=e.cause)


@router.post("/pest-alert")
async def pest_alert():
    client = await get_temporal_client()
    try:
        result = await client.start_workflow(
            "pest-alert",
            id=f"pest-alert-{date.today()}",
            task_queue="pest-alert-task-queue",
        )

        logger.info(f"Result: {result}")
        return {"success": True, "workflow_id": result.id}

    except WorkflowFailureError as e:
        logger.error("Got expected exception: ", traceback.format_exc())
        raise HTTPException(status_code=500, detail=e.cause)
