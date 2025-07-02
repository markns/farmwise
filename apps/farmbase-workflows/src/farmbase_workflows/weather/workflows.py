from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from farmbase_workflows.weather.activities import WeatherActivities
from farmbase_workflows.whatsapp.activities import WhatsAppActivities


@workflow.defn
class SendWeatherWorkflow:
    @workflow.run
    async def run(self):
        retry_policy = RetryPolicy(
            maximum_attempts=1,
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
                WhatsAppActivities.send_whatsapp_template,
                # TODO: could used named params once https://github.com/david-lev/pywa/issues/115 is fixed
                args=[contact, "weather_forecast", None, [forecast_summary.location] + forecast_summary.forecast],
                start_to_close_timeout=timedelta(seconds=10),
            )

            # Save new messages to db
            await workflow.execute_activity_method(
                WhatsAppActivities.save_message,
                args=[contact, "\n".join(forecast_summary.forecast)],
                start_to_close_timeout=timedelta(seconds=10),
            )

        # TODO: What is the right thing to return here?
