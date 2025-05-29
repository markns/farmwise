import asyncio

from temporalio.client import (
    Client,
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleSpec,
    ScheduleState,
)

from ..weather.shared import DEFAULT_TASK_QUEUE
from .workflows import FarmAlertWorkflow


async def main():
    client = await Client.connect("localhost:7233")

    await client.create_schedule(
        "farm-alert-schedule-id",
        Schedule(
            action=ScheduleActionStartWorkflow(
                FarmAlertWorkflow.run,
                id="farm-alert-workflow-id",
                task_queue=DEFAULT_TASK_QUEUE,
            ),
            spec=ScheduleSpec(
                cron_expressions=["0 * * * *"],  # Every hour at minute 0
                time_zone_name="Africa/Nairobi",  # EAT timezone
            ),
            state=ScheduleState(note="Farm alert workflow - runs every hour to check for new notes and send alerts to nearby farms."),
        ),
    )
    print("Farm alert schedule created successfully!")


if __name__ == "__main__":
    asyncio.run(main())