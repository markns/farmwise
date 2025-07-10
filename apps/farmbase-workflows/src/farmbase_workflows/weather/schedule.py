from temporalio.client import (
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleSpec,
)

from . import TASK_QUEUE
from .workflows import WeatherForecastWorkflow

weather_schedules = {
    "daily-weather-forecast": Schedule(
        action=ScheduleActionStartWorkflow(
            workflow=WeatherForecastWorkflow.run,
            # "my schedule arg",
            id="daily-weather-workflow",
            task_queue=TASK_QUEUE,
        ),
        spec=ScheduleSpec(
            cron_expressions=["0 7 * * *"],  # UTC time: 7 AM EAT = 4 AM UTC
            time_zone_name="Africa/Nairobi",  # EAT corresponds to this IANA zone
        ),
    ),
    # TODO: weather warning?
}
