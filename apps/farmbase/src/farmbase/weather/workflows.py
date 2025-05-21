from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from farmbase.weather.activities import WeatherActivities
from farmbase.whatsapp.activities import WhatsAppActivities


@workflow.defn
class SendWeatherWorkflow:
    @workflow.run
    async def run(self) -> str:
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            maximum_interval=timedelta(seconds=2),
            non_retryable_error_types=[],
        )

        # load all contacts with a location
        contacts = await workflow.execute_activity_method(
            WeatherActivities.get_contacts_with_location,
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=retry_policy,
        )
        for contact in contacts:
            forecast = await workflow.execute_activity_method(
                WeatherActivities.get_weather_forecast,
                contact,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy,
            )
            forecast_summary = await workflow.execute_activity_method(
                WeatherActivities.summarize_forecast,
                args=(forecast,),
                start_to_close_timeout=timedelta(seconds=10),
            )

            await workflow.execute_activity_method(
                WhatsAppActivities.send_whatsapp_message,
                args=[contact, forecast_summary],
                start_to_close_timeout=timedelta(seconds=10),
            )

            # Save new messages to db
            await workflow.execute_activity_method(
                WhatsAppActivities.save_message,
                args=[contact, forecast_summary],
                start_to_close_timeout=timedelta(seconds=10),
            )

        return "TODO"
