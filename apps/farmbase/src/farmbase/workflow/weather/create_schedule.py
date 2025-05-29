import asyncio

from temporalio.client import (
    Client,
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleSpec,
    ScheduleState,
)

from farmbase.weather.shared import DEFAULT_TASK_QUEUE
from farmbase.weather.workflows import SendWeatherWorkflow


async def main():
    client = await Client.connect("localhost:7233")

    await client.create_schedule(
        "workflow-schedule-id",
        Schedule(
            action=ScheduleActionStartWorkflow(
                SendWeatherWorkflow.run,
                # "my schedule arg",
                id="schedules-workflow-id",
                task_queue=DEFAULT_TASK_QUEUE,
            ),
            spec=ScheduleSpec(
                cron_expressions=["0 7 * * *"],  # UTC time: 7 AM EAT = 4 AM UTC
                time_zone_name="Africa/Nairobi",  # EAT corresponds to this IANA zone
            ),
            state=ScheduleState(note="Here's a note on my Schedule."),
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
