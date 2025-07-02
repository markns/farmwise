from pywa_async import WhatsApp
from temporalio.client import Client
from temporalio.worker import Worker

from farmbase_workflows import weather
from farmbase_workflows.weather.activities import WeatherActivities
from farmbase_workflows.weather.workflows import SendWeatherWorkflow
from farmbase_workflows.whatsapp.activities import WhatsAppActivities


def weather_worker(client: Client, wa: WhatsApp):
    weather_activities = WeatherActivities()
    whatsapp_activities = WhatsAppActivities(whatsapp_client=wa)

    return Worker(
        client,
        task_queue=weather.TASK_QUEUE,
        workflows=[SendWeatherWorkflow],
        activities=[
            weather_activities.get_contacts_with_location,
            weather_activities.get_weather_forecast,
            weather_activities.summarize_forecast,
            whatsapp_activities.send_whatsapp_template,
            whatsapp_activities.save_message,
        ],
    )
