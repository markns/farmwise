import asyncio
import zoneinfo
from datetime import datetime

from dotenv import find_dotenv, load_dotenv
from temporalio import workflow
from temporalio.client import Client

from farmbase.workflow.cropcycle.shared import CROP_CYCLE_TASK_QUEUE, CropCycleEvent
from farmbase.workflow.cropcycle.workflows import CropCycleWorkflow
from farmbase.workflow.whatsapp.shared import SimpleContact

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    from temporalio.contrib.pydantic import pydantic_data_converter


load_dotenv(find_dotenv())


async def run_crop_cycle_workflow(
    contact: SimpleContact,
    planting_date: datetime,
    events: list[CropCycleEvent],
    workflow_id: str | None = None,
    demo=False,
):
    """Run the crop cycle workflow for a specific contact and crop cycle"""
    client = await Client.connect("localhost:7233", data_converter=pydantic_data_converter)

    if workflow_id is None:
        workflow_id = f"crop-cycle-{contact.id}-{planting_date.strftime('%Y%m%d')}"

    result = await client.execute_workflow(
        CropCycleWorkflow.run,
        args=[contact, planting_date, events, demo],
        id=workflow_id,
        task_queue=CROP_CYCLE_TASK_QUEUE,
    )

    return result


async def main():
    """Example usage of the crop cycle workflow"""
    # Example contact
    contact = SimpleContact(id=1, phone_number="+31657775781", name="Mark", location="Nairobi, Kenya")

    # Example planting date (can be in past or future)
    planting_date = datetime(2025, 6, 8, tzinfo=zoneinfo.ZoneInfo("Africa/Nairobi"))

    # Example crop cycle events DataFrame
    events = [
        CropCycleEvent(
            **{
                "event_type": "planting",
                "event_category": "planting_reminder",
                "title": "Time to Plant Maize",
                "start_day": 0,
                "end_day": 3,
                "identifier": "maize_planting_1",
                "nutshell": "Plant certified maize seeds for best yield",
                "description": "Use certified seeds and plant at recommended spacing for optimal growth.",
            }
        ),
        CropCycleEvent(
            **{
                "event_type": "fertilizer",
                "event_category": "fertilizer_application",
                "title": "Apply Base Fertilizer",
                "start_day": 7,
                "end_day": 10,
                "identifier": "base_fertilizer_1",
                "nutshell": "Apply DAP fertilizer to boost early growth",
                "description": "Apply DAP fertilizer at 50kg per acre during planting or within 2 weeks after germination.",
            }
        ),
        CropCycleEvent(
            **{
                "event_type": "weeding",
                "event_category": "weed_management",
                "title": "First Weeding",
                "start_day": 21,
                "end_day": 28,
                "identifier": "first_weeding_1",
                "nutshell": "Remove weeds to reduce competition",
                "description": "Conduct first weeding 3-4 weeks after planting to remove competing weeds.",
            }
        ),
    ]

    print(f"Starting crop cycle workflow for {contact.name}")
    print(f"Planting date: {planting_date}")
    print(f"Number of events: {len(events)}")

    result = await run_crop_cycle_workflow(contact, planting_date, events, demo=True)
    print(f"Workflow result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
