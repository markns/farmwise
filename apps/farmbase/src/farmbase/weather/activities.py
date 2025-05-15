import os

from dotenv import find_dotenv, load_dotenv
from more_itertools import flatten
from python_weather.forecast import Forecast
from shared import ForecastDetails, LocationQuery
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import async_sessionmaker
from temporalio import activity

load_dotenv(find_dotenv())


class WeatherActivities:
    @activity.defn
    async def summarize_forecast(self, forecast: ForecastDetails):
        from openai import OpenAI

        client = OpenAI()

        response = client.responses.create(
            model="gpt-4.1-nano",
            input=f"""
    Summarise the weather forecast for the next 3 days using the details below.
    The forecast is to be sent to farmers in {forecast.location}, {forecast.country}.
    Use one summary emoji at the start of each line.
    
    {forecast.hourly_descriptions}
          """,
        )

        return response.output[0].content[0].text

    @activity.defn
    async def get_weather_forecast(self, location_query: LocationQuery) -> ForecastDetails:
        """
        Fetches and displays the current weather and a 3-day forecast for a given location.

        Args:
            location_query (str): The name of the city or "latitude, longitude" string.
        """
        import python_weather

        async with python_weather.Client(unit=python_weather.METRIC) as client:
            forecast: Forecast = await client.get(location_query.location)

        forecast_description = [
            [f"{daily.date} {hourly.time} {hourly.description}" for hourly in daily] for daily in forecast
        ]

        return ForecastDetails(
            location=forecast.location,
            country=forecast.country,
            hourly_descriptions=list(flatten(forecast_description)),
        )

    @activity.defn
    async def send_whatsapp_message(self, send_to: str, message: str):
        from pywa_async import WhatsApp

        wa = WhatsApp(
            phone_id=os.environ["WHATSAPP_PHONE_ID"],
            token=os.environ["WHATSAPP_TOKEN"],
        )
        # TODO: This should be a template message: https://pywa.readthedocs.io/en/latest/content/examples/template.html
        await wa.send_message(to=send_to, text=message)

    @activity.defn
    async def save_message(self, contact_id: int, text: str):
        from farmbase.auth.models import FarmbaseUserOrganization
        from farmbase.database.core import engine
        from farmbase.message.models import Message

        # TODO: fake import
        FarmbaseUserOrganization.organization

        organization = "default"
        schema = f"farmbase_organization_{organization}"
        schema_engine = engine.execution_options(schema_translate_map={None: schema})
        async_session_factory = async_sessionmaker(
            bind=schema_engine,
            expire_on_commit=False,
        )

        async with async_session_factory() as session:
            stmt = insert(Message).values(contact_id=contact_id, text=text).returning(Message.id)
            result = await session.execute(stmt)
            new_id = result.scalar_one()
            await session.commit()
            return new_id


#
# class BankingActivities:
#     def __init__(self):
#         self.bank = BankingService("bank-api.example.com")
#
#     @activity.defn
#     async def withdraw(self, data: PaymentDetails) -> str:
#         reference_id = f"{data.reference_id}-withdrawal"
#         try:
#             confirmation = await asyncio.to_thread(self.bank.withdraw, data.source_account, data.amount, reference_id)
#             return confirmation
#         except InvalidAccountError:
#             raise
#         except Exception:
#             activity.logger.exception("Withdrawal failed")
#             raise
#
#     # @@@SNIPEND
#     # @@@SNIPSTART python-money-transfer-project-template-deposit
#     @activity.defn
#     async def deposit(self, data: PaymentDetails) -> str:
#         reference_id = f"{data.reference_id}-deposit"
#         try:
#             confirmation = await asyncio.to_thread(self.bank.deposit, data.target_account, data.amount, reference_id)
#             """
#             confirmation = await asyncio.to_thread(
#                 self.bank.deposit_that_fails,
#                 data.target_account,
#                 data.amount,
#                 reference_id,
#             )
#             """
#             return confirmation
#         except InvalidAccountError:
#             raise
#         except Exception:
#             activity.logger.exception("Deposit failed")
#             raise
#
#     # @@@SNIPEND
#
#     # @@@SNIPSTART python-money-transfer-project-template-refund
#     @activity.defn
#     async def refund(self, data: PaymentDetails) -> str:
#         reference_id = f"{data.reference_id}-refund"
#         try:
#             confirmation = await asyncio.to_thread(self.bank.deposit, data.source_account, data.amount, reference_id)
#             return confirmation
#         except InvalidAccountError:
#             raise
#         except Exception:
#             activity.logger.exception("Refund failed")
#             raise
#
#     # @@@SNIPEND
