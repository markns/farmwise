from pywa_async import WhatsApp
from temporalio.client import Client
from temporalio.worker import Worker

from farmbase_workflows import crop_cycle
from farmbase_workflows.crop_cycle.activities import CropCycleActivities
from farmbase_workflows.crop_cycle.workflows import CropCycleWorkflow
from farmbase_workflows.whatsapp.activities import WhatsAppActivities


def crop_cycle_worker(client: Client, wa: WhatsApp):
    crop_cycle_activities = CropCycleActivities()
    whatsapp_activities = WhatsAppActivities(whatsapp_client=wa)

    return Worker(
        client,
        task_queue=crop_cycle.TASK_QUEUE,
        workflows=[CropCycleWorkflow],
        activities=[
            crop_cycle_activities.log_event_sent,
            whatsapp_activities.send_whatsapp_template,
        ],
    )
