from pywa_async import WhatsApp
from temporalio.client import Client
from temporalio.worker import Worker

from farmbase_workflows.pest_alert import TASK_QUEUE
from farmbase_workflows.pest_alert.activities import AlertActivities
from farmbase_workflows.pest_alert.workflows import PestAlertWorkflow
from farmbase_workflows.whatsapp.activities import WhatsAppActivities


def pest_alert_worker(client: Client, wa: WhatsApp):
    alert_activities = AlertActivities()
    whatsapp_activities = WhatsAppActivities(whatsapp_client=wa)

    return Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[PestAlertWorkflow],
        activities=[
            alert_activities.get_recent_notes,
            alert_activities.find_nearby_farms,
            alert_activities.generate_alert_message,
            whatsapp_activities.send_whatsapp_template,
        ],
    )
