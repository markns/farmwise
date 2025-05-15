from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from farmbase.weather.activities import WeatherActivities
from farmbase.weather.shared import LocationQuery

# with workflow.unsafe.imports_passed_through():
# from activities import BankingActivities
#     from shared import PaymentDetails
#
#
# @workflow.defn
# class MoneyTransfer:
#     @workflow.run
#     async def run(self, payment_details: PaymentDetails) -> str:
#         retry_policy = RetryPolicy(
#             maximum_attempts=3,
#             maximum_interval=timedelta(seconds=2),
#             non_retryable_error_types=["InvalidAccountError", "InsufficientFundsError"],
#         )
#
#         # Withdraw money
#         withdraw_output = await workflow.execute_activity_method(
#             BankingActivities.withdraw,
#             payment_details,
#             start_to_close_timeout=timedelta(seconds=5),
#             retry_policy=retry_policy,
#         )

#         # Deposit money
#         try:
#             deposit_output = await workflow.execute_activity_method(
#                 BankingActivities.deposit,
#                 payment_details,
#                 start_to_close_timeout=timedelta(seconds=5),
#                 retry_policy=retry_policy,
#             )
#
#             result = f"Transfer complete (transaction IDs: {withdraw_output}, {deposit_output})"
#             return result
#         except ActivityError as deposit_err:
#             # Handle deposit error
#             workflow.logger.error(f"Deposit failed: {deposit_err}")
#             # Attempt to refund
#             try:
#                 refund_output = await workflow.execute_activity_method(
#                     BankingActivities.refund,
#                     payment_details,
#                     start_to_close_timeout=timedelta(seconds=5),
#                     retry_policy=retry_policy,
#                 )
#                 workflow.logger.info(f"Refund successful. Confirmation ID: {refund_output}")
#                 raise deposit_err
#             except ActivityError as refund_error:
#                 workflow.logger.error(f"Refund failed: {refund_error}")
#                 raise refund_error


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

        forecast = await workflow.execute_activity_method(
            WeatherActivities.get_weather_forecast,
            LocationQuery(location="0.5635, 34.5606"),
            # YourParams("Hello", name),
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=retry_policy,
        )
        forecast_summary = await workflow.execute_activity_method(
            WeatherActivities.summarize_forecast,
            args=(forecast,),
            # YourParams("Hello", name),
            start_to_close_timeout=timedelta(seconds=10),
        )

        await workflow.execute_activity_method(
            WeatherActivities.send_whatsapp_message,
            args=["31657775781", forecast_summary],
            # YourParams("Hello", name),
            start_to_close_timeout=timedelta(seconds=10),
        )

        # Save new messages to db
        await workflow.execute_activity_method(
            WeatherActivities.save_message,
            args=[1, forecast_summary],
            # YourParams("Hello", name),
            start_to_close_timeout=timedelta(seconds=10),
        )

        return f"sent {forecast_summary} to 3165"
