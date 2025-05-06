from __future__ import annotations as _annotations

import httpx
from agents import (
    RunContextWrapper,
    function_tool,
)
from farmbase_client import AuthenticatedClient
from farmbase_client.api.gaez import gaez_aez_classification, gaez_growing_period, gaez_suitability_index
from farmbase_client.models import SuitabilityIndexResponse

from farmwise.context import UserContext
from farmwise.settings import settings


def copy_doc(from_func):
    def decorator(to_func):
        to_func.__doc__ = from_func.__doc__
        return to_func

    return decorator


@function_tool
@copy_doc(gaez_suitability_index.asyncio)
async def suitability_index(
    _: RunContextWrapper[UserContext], latitude: float, longitude: float
) -> SuitabilityIndexResponse:
    with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
        return await gaez_suitability_index.asyncio(client=client, latitude=latitude, longitude=longitude)


@function_tool
@copy_doc(gaez_aez_classification.asyncio)
async def aez_classification(_: RunContextWrapper[UserContext], latitude: float, longitude: float) -> str:
    with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
        return await gaez_aez_classification.asyncio(client=client, latitude=latitude, longitude=longitude)


# Refining the Spatial Scale for Maize Crop Agro-Climatological Suitability Conditions in a Region
# with Complex Topography towards a Smart and Sustainable Agriculture. Case Study: Central Romania (Cluj Count

# Maturity Hybrid,growing season length (days/y)
# Extremely early,76–85
# Early,86–112
# Intermediate,113–129
# Late,130–145
# Very late,>150


@function_tool
@copy_doc(gaez_growing_period.asyncio)
async def growing_period(_: RunContextWrapper[UserContext], latitude: float, longitude: float) -> int:
    with AuthenticatedClient(base_url=settings.FARMBASE_ENDPOINT, token=settings.FARMBASE_API_KEY) as client:
        return await gaez_growing_period.asyncio(client=client, latitude=latitude, longitude=longitude)


@function_tool
async def maize_varieties(_: RunContextWrapper[UserContext], altitude: float, growing_period_days: int) -> str:
    #  TODO: use farmbase-client / farmbase_agent_toolkit
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "http://127.0.0.1:8000/api/v1/crop-varieties/maize",
            params={"altitude": altitude, "growing_period": growing_period_days},
        )
        return r.json()


@function_tool
async def elevation(_: RunContextWrapper[UserContext], latitude: float, longitude: float) -> float:
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
async def soil_property(_: RunContextWrapper[UserContext], latitude: float, longitude: float) -> float:
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
