from temporalio.client import (
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleSpec, ScheduleState,
)

from .workflows import PestAlertWorkflow
from .. import pest_alert

pest_alert_schedules = {
    "pest-alert": Schedule(
        action=ScheduleActionStartWorkflow(
            PestAlertWorkflow.run,
            id="pest-alert-schedule",
            task_queue=pest_alert.TASK_QUEUE,
        ),
        spec=ScheduleSpec(
            cron_expressions=["0 19 * * *"],
            time_zone_name="Africa/Nairobi",  # EAT timezone
        ),
        state=ScheduleState(paused=True)
    )

}
