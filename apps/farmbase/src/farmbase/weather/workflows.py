from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from farmbase.weather.activities import WeatherActivities

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
                # TODO: Move to WhatsAppActivities
                WeatherActivities.send_whatsapp_message,
                args=[contact, forecast_summary],
                start_to_close_timeout=timedelta(seconds=10),
            )

            # Save new messages to db
            await workflow.execute_activity_method(
                # TODO: Move to WhatsAppActivities
                WeatherActivities.save_message,
                args=[contact, forecast_summary],
                start_to_close_timeout=timedelta(seconds=10),
            )

        return "TODO"
