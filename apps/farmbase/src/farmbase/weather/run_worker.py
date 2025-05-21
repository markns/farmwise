import asyncio
import os

from dotenv import find_dotenv, load_dotenv
from pywa_async import WhatsApp
from temporalio.client import Client
from temporalio.worker import Worker

from farmbase.weather.activities import WeatherActivities
from farmbase.weather.shared import DEFAULT_TASK_QUEUE
from farmbase.weather.workflows import SendWeatherWorkflow
from farmbase.whatsapp.activities import WhatsAppActivities

load_dotenv(find_dotenv())


async def main():
    client = await Client.connect("localhost:7233")

    wa = WhatsApp(
        phone_id=os.environ["WHATSAPP_PHONE_ID"],
        token=os.environ["WHATSAPP_TOKEN"],
    )

    weather_activities = WeatherActivities()
    whatsapp_activities = WhatsAppActivities(whatsapp_client=wa)
    worker = Worker(
        client,
        task_queue=DEFAULT_TASK_QUEUE,
        workflows=[SendWeatherWorkflow],
        activities=[
            weather_activities.get_contacts_with_location,
            weather_activities.get_weather_forecast,
            weather_activities.summarize_forecast,
            whatsapp_activities.send_whatsapp_message,
            whatsapp_activities.save_message,
        ],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
