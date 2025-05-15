import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from farmbase.weather.activities import WeatherActivities
from farmbase.weather.shared import DEFAULT_TASK_QUEUE
from farmbase.weather.workflows import SendWeatherWorkflow


async def main():
    client = await Client.connect("localhost:7233")

    activities = WeatherActivities()
    worker = Worker(
        client,
        task_queue=DEFAULT_TASK_QUEUE,
        workflows=[SendWeatherWorkflow],
        activities=[
            activities.get_contacts_with_location,
            activities.get_weather_forecast,
            activities.summarize_forecast,
            activities.send_whatsapp_message,
            activities.save_message,
        ],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
