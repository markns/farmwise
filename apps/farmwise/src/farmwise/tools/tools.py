from __future__ import annotations as _annotations

import asyncio
from typing import Any

import httpx
from agents import (
    RunContextWrapper,
    function_tool,
)

from farmbase_client.api.crop_varieties import crop_varieties_get_maize_varieties
from farmbase_client.api.gaez import gaez_aez_classification, gaez_growing_period, gaez_suitability_index
from farmbase_client.models import SuitabilityIndexResponse, CropVarietiesResponse
from farmwise.dependencies import UserContext
from farmwise.farmbase import FarmbaseClient
from farmwise.utils import copy_doc


@function_tool
@copy_doc(gaez_suitability_index.asyncio)
async def suitability_index(
        _: RunContextWrapper[UserContext], latitude: float, longitude: float
) -> SuitabilityIndexResponse:
    async with FarmbaseClient() as client:
        return await gaez_suitability_index.asyncio(client=client.raw, latitude=latitude, longitude=longitude)


@function_tool
@copy_doc(gaez_aez_classification.asyncio)
async def aez_classification(_: RunContextWrapper[UserContext], latitude: float, longitude: float) -> str:
    async with FarmbaseClient() as client:
        return await gaez_aez_classification.asyncio(client=client.raw, latitude=latitude, longitude=longitude)


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
    async with FarmbaseClient() as client:
        return await gaez_growing_period.asyncio(client=client.raw, latitude=latitude, longitude=longitude)


@function_tool
@copy_doc(crop_varieties_get_maize_varieties.asyncio)
async def maize_varieties(_: RunContextWrapper[UserContext], altitude: float,
                          growing_period_days: int) -> CropVarietiesResponse:
    async with FarmbaseClient() as client:
        return await crop_varieties_get_maize_varieties.asyncio(client=client.raw, altitude=altitude,
                                                                growing_period=growing_period_days)


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


async def _fetch_property(
        client: httpx.AsyncClient, latitude: float, longitude: float, property_name: str
) -> dict[str, Any]:
    uri = "https://api.isda-africa.com/v1/soilproperty"
    response = await client.get(
        uri,
        params={
            "key": "AIzaSyCruMPt43aekqITCooCNWGombhbcor3cf4",  # TODO: replace with secure key management
            "lat": latitude,
            "lon": longitude,
            "property": property_name,
            "depth": "0-20",
        },
    )
    response.raise_for_status()
    return response.json().get("property", {}).get(property_name, [{}])[0]


@function_tool
async def soil_properties(latitude: float, longitude: float) -> dict[str, str]:
    """Fetch soil properties for a given location."""
    properties = [
        "ph",
        "texture_class",
        "nitrogen_total",
        "potassium_extractable",
        "phosphorous_extractable",
    ]

    async with httpx.AsyncClient() as client:
        tasks = [_fetch_property(client, latitude, longitude, prop) for prop in properties]
        results = await asyncio.gather(*tasks)

    resp = {}
    for prop, result in zip(properties, results):
        value = result.get("value", {}).get("value")
        unit = result.get("value", {}).get("unit")
        resp[prop] = f"{value} {unit}" if unit else str(value)
    return resp
