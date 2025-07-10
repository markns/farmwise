from functools import reduce

from loguru import logger
from temporalio.client import (
    Client,
    ScheduleUpdate, ScheduleUpdateInput, Schedule,
)

from farmbase_workflows.pest_alert.schedule import pest_alert_schedules
from farmbase_workflows.weather.schedule import weather_schedules


def merge_dicts(dicts):
    return reduce(lambda a, b: a | b, dicts)


all_schedules = merge_dicts([
    weather_schedules,
    # pest_alert_schedules
])


async def update_schedule(client: Client, schedule_id, schedule: Schedule):
    handle = client.get_schedule_handle(schedule_id)

    async def update_schedule_simple(_: ScheduleUpdateInput) -> ScheduleUpdate:
        return ScheduleUpdate(schedule=schedule)

    await handle.update(update_schedule_simple)


async def create_or_update_schedules(client: Client):
    existing = {}
    async for item in await client.list_schedules():
        existing[item.id] = item.schedule

    for schedule_id, schedule in all_schedules.items():

        if schedule_id in existing:
            logger.info(f"Updating schedule {schedule_id} with definition {schedule}")
            await update_schedule(client, schedule_id, schedule)
        else:
            logger.info(f"Creating schedule {schedule_id} with definition {schedule}")
            await client.create_schedule(schedule_id, schedule)
