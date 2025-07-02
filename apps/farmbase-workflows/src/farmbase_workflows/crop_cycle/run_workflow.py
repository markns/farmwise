import asyncio
import json
import zoneinfo
from datetime import datetime
from operator import itemgetter

from dotenv import find_dotenv, load_dotenv
from temporalio import workflow
from temporalio.client import Client

from farmbase_workflows import crop_cycle
from farmbase_workflows.crop_cycle.schema import CropCycleEvent
from farmbase_workflows.crop_cycle.workflows import CropCycleWorkflow
from farmbase_workflows.whatsapp.shared import SimpleContact

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
        task_queue=crop_cycle.TASK_QUEUE,
    )

    return result


async def main():
    """Example usage of the crop cycle workflow"""
    # Example contact
    contact = SimpleContact(id=1, phone_number="+31657775781", name="Mark", location="Nairobi, Kenya")

    # Example planting date (can be in past or future)
    planting_date = datetime(2025, 6, 8, tzinfo=zoneinfo.ZoneInfo("Africa/Nairobi"))

    with open("/Users/markns/workspace/farmwise/plantix/crop-cycle/Cfb_maize_direct_seeding.json") as f:
        cycle_events = json.load(f)
    with open("/Users/markns/workspace/farmwise/plantix/events.json") as f:
        all_events = json.load(f)

    all_events = {e["identifier"]: e for e in all_events}

    for event in cycle_events["events"]:
        event.update(all_events[event["identifier"]])

    crop_cycle = list(sorted(cycle_events["events"], key=itemgetter("start_day")))

    events = [CropCycleEvent(**e) for e in crop_cycle]

    print(f"Starting crop cycle workflow for {contact.name}")
    print(f"Planting date: {planting_date}")
    print(f"Number of events: {len(events)}")

    result = await run_crop_cycle_workflow(contact, planting_date, events, demo=True)
    print(f"Workflow result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
