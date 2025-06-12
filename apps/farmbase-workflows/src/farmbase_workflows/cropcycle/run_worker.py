import asyncio
import os

from dotenv import find_dotenv, load_dotenv
from pywa_async import WhatsApp
from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

from farmbase_workflows.cropcycle.activities import CropCycleActivities
from farmbase_workflows.cropcycle.shared import CROP_CYCLE_TASK_QUEUE
from farmbase_workflows.cropcycle.workflows import CropCycleWorkflow
from farmbase_workflows.whatsapp.activities import WhatsAppActivities

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    from temporalio.contrib.pydantic import pydantic_data_converter


load_dotenv(find_dotenv())

interrupt_event = asyncio.Event()


async def main():
    client = await Client.connect("localhost:7233", data_converter=pydantic_data_converter)

    wa = WhatsApp(
        phone_id=os.environ["WHATSAPP_PHONE_ID"],
        token=os.environ["WHATSAPP_TOKEN"],
    )

    crop_cycle_activities = CropCycleActivities()
    whatsapp_activities = WhatsAppActivities(whatsapp_client=wa)

    async with Worker(
        client,
        task_queue=CROP_CYCLE_TASK_QUEUE,
        workflows=[CropCycleWorkflow],
        activities=[
            crop_cycle_activities.log_event_sent,
            whatsapp_activities.send_whatsapp_template,
            whatsapp_activities.save_message,
        ],
    ):
        # Wait until interrupted
        print("Crop cycle worker started, ctrl+c to exit")
        await interrupt_event.wait()
        print("Shutting down")


if __name__ == "__main__":
    asyncio.run(main())
