from more_itertools import flatten
from python_weather.forecast import Forecast
from sqlalchemy.ext.asyncio import async_sessionmaker
from temporalio import activity

from ..whatsapp.shared import Contact
from .shared import ForecastDetails


class WeatherActivities:
    @activity.defn
    async def get_contacts_with_location(self):
        from geoalchemy2.shape import to_shape

        # TODO: fake import
        from farmbase.auth.models import FarmbaseUserOrganization
        from farmbase.contact.service import get_all_with_location
        from farmbase.database.core import engine

        FarmbaseUserOrganization.organization

        organization = "default"
        schema = f"farmbase_organization_{organization}"
        schema_engine = engine.execution_options(schema_translate_map={None: schema})
        async_session_factory = async_sessionmaker(
            bind=schema_engine,
            expire_on_commit=False,
        )

        async with async_session_factory() as session:
            contacts = await get_all_with_location(db_session=session)

        def _get_contact(c):
            point = to_shape(c.location)
            return Contact(id=c.id, phone_number=c.phone_number, name=c.name, location=f"{point.y},{point.x}")

        return [_get_contact(c) for c in contacts]

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
    async def get_weather_forecast(self, contact: Contact) -> ForecastDetails:
        """
        Fetches and displays the current weather and a 3-day forecast for a given location.

        Args:
            contact (str): The name of the city or "latitude, longitude" string.
        """
        import python_weather

        async with python_weather.Client(unit=python_weather.METRIC) as client:
            forecast: Forecast = await client.get(contact.location)

        forecast_description = [
            [f"{daily.date} {hourly.time} {hourly.description}" for hourly in daily] for daily in forecast
        ]

        return ForecastDetails(
            location=forecast.location,
            country=forecast.country,
            hourly_descriptions=list(flatten(forecast_description)),
        )
