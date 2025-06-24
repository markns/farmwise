from __future__ import annotations as _annotations

import asyncio

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
from farmwise.settings import settings
from farmwise.utils import copy_doc
from isdasoil_api_client import Client as IsdaClient, AuthenticatedClient as AuthenticatedIsdaClient
from isdasoil_api_client.api.authentication import login_login_post
from isdasoil_api_client.api.version_2 import get_soil_data_isdasoil_v2_soilproperty_get
from isdasoil_api_client.models import BodyLoginLoginPost
from isdasoil_api_client.models.get_soil_data_isdasoil_v2_soilproperty_get_depth_type_0 import \
    GetSoilDataIsdasoilV2SoilpropertyGetDepthType0 as DepthType
from isdasoil_api_client.models.get_soil_data_isdasoil_v2_soilproperty_get_property_type_0 import \
    GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0 as PropertyType

ISDA_URL = "https://api.isda-africa.com"


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


async def get_isda_token():
    async with IsdaClient(base_url=ISDA_URL) as client:
        token = await login_login_post.asyncio(client=client,
                                               body=BodyLoginLoginPost(
                                                   username=settings.ISDA_USERNAME,
                                                   password=settings.ISDA_PASSWORD.get_secret_value()))
        return token.access_token


async def get_soil_property(client, lat, lon, property_, depth):
    return await get_soil_data_isdasoil_v2_soilproperty_get.asyncio(client=client, lon=lon, lat=lat,
                                                                    property_=property_,
                                                                    depth=depth)


@function_tool
async def soil_properties(_: RunContextWrapper[UserContext], latitude: float, longitude: float) -> dict[str, str]:
    """Fetch soil properties for a given location."""

    properties = [
        PropertyType.PH,
        PropertyType.TEXTURE_CLASS,
        PropertyType.NITROGEN_TOTAL,
        PropertyType.POTASSIUM_EXTRACTABLE,
        PropertyType.PHOSPHOROUS_EXTRACTABLE,
    ]

    token = await get_isda_token()
    async with AuthenticatedIsdaClient(token=token, base_url=ISDA_URL) as client:
        tasks = [get_soil_property(client, lat=latitude, lon=longitude,
                                   property_=prop, depth=DepthType.VALUE_0) for prop in properties]
        results = await asyncio.gather(*tasks)

    merged = {k: v[0] for r in results for k, v in r.property_.additional_properties.items()}
    resp = {}
    for prop, soil_data in merged.items():
        value = soil_data.value.value
        unit = soil_data.value.unit
        resp[prop] = f"{value} {unit}" if unit else str(value)
    return resp
