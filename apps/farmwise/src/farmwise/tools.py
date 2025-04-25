from __future__ import annotations as _annotations

import httpx
from agents import (
    RunContextWrapper,
    function_tool,
)

from farmwise.context import UserContext

#
# @function_tool(name_override="faq_lookup_tool", description_override="Lookup frequently asked questions.")
# async def faq_lookup_tool(question: str) -> str:
#     if "bag" in question or "baggage" in question:
#         return (
#             "You are allowed to bring one bag on the plane. "
#             "It must be under 50 pounds and 22 inches x 14 inches x 9 inches."
#         )
#     elif "seats" in question or "plane" in question:
#         return (
#             "There are 120 seats on the plane. "
#             "There are 22 business class seats and 98 economy seats. "
#             "Exit rows are rows 4 and 16. "
#             "Rows 5-8 are Economy Plus, with extra legroom. "
#         )
#     elif "wifi" in question:
#         return "We have free wifi on the plane, join Airline-Wifi"
#     return "I'm sorry, I don't know the answer to that question."
#
#
# @function_tool
# async def update_seat(context: RunContextWrapper[UserContext], confirmation_number: str, new_seat: str) -> str:
#     """
#     Update the seat for a given confirmation number.
#
#     Args:
#         confirmation_number: The confirmation number for the flight.
#         new_seat: The new seat to update to.
#     """
#     # Update the context based on the customer's input
#     context.context.confirmation_number = confirmation_number
#     context.context.seat_number = new_seat
#     # Ensure that the flight number has been set by the incoming handoff
#     assert context.context.flight_number is not None, "Flight number is required"
#     return f"Updated seat to {new_seat} for confirmation number {confirmation_number}"


@function_tool
async def crop_suitability(
    context: RunContextWrapper[UserContext], crop_type: str, latitude: float, longitude: float
) -> str:
    #  TODO: use farmbase-client / farmbase_agent_toolkit
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"http://127.0.0.1:8000/api/v1/crop-varieties/suitability?crop_type={crop_type}"
            f"&latitude={latitude}&longitude={longitude}"
        )
        return r.json()


@function_tool
async def aez_classification(context: RunContextWrapper[UserContext], latitude: float, longitude: float) -> str:
    #  TODO: use farmbase-client / farmbase_agent_toolkit
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "http://127.0.0.1:8000/api/v1/gaez/aez_classification",
            params={"latitude": latitude, "longitude": longitude},
        )
        return r.json()


@function_tool
async def growing_period(context: RunContextWrapper[UserContext], latitude: float, longitude: float) -> str:
    #  TODO: use farmbase-client / farmbase_agent_toolkit
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "http://127.0.0.1:8000/api/v1/gaez/growing_period",
            params={"latitude": latitude, "longitude": longitude},
        )
        return r.json()


@function_tool
async def maize_varieties(context: RunContextWrapper[UserContext], altitude: float, growing_period_days: int) -> str:
    #  TODO: use farmbase-client / farmbase_agent_toolkit
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "http://127.0.0.1:8000/api/v1/crop-varieties/maize",
            params={"altitude": altitude, "growing_period": growing_period_days},
        )
        return r.json()


@function_tool
async def elevation(ctx: RunContextWrapper[UserContext], latitude: float, longitude: float) -> float:
    """Fetch the elevation in metres for a given location.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
    """
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.open-meteo.com/v1/elevation", params={"latitude": latitude, "longitude": longitude}
        )
        return r.json()["elevation"][0]


@function_tool
async def soil_property(ctx: RunContextWrapper[UserContext], latitude: float, longitude: float) -> float:
    """Fetch an estimate of a soil property for a given location.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
    """
    uri = "https://api.isda-africa.com/v1/soilproperty"
    async with httpx.AsyncClient() as client:
        r = await client.get(
            uri,
            params={
                "key": "AIzaSyCruMPt43aekqITCooCNWGombhbcor3cf4",  # todo: get own key
                "lat": latitude,
                "lon": longitude,
                "property": "ph",
                "depth": "0-20",
            },
        )
        return r.json()["property"]["ph"][0]["value"]["value"]
