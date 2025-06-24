from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_soil_data_isdasoil_v2_soilproperty_get_depth_type_0 import (
    GetSoilDataIsdasoilV2SoilpropertyGetDepthType0,
)
from ...models.get_soil_data_isdasoil_v2_soilproperty_get_property_type_0 import (
    GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0,
)
from ...models.http_validation_error import HTTPValidationError
from ...models.property_response import PropertyResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    lon: float,
    lat: float,
    depth: Union[GetSoilDataIsdasoilV2SoilpropertyGetDepthType0, None, Unset] = UNSET,
    property_: Union[GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0, None, Unset] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["lon"] = lon

    params["lat"] = lat

    json_depth: Union[None, Unset, str]
    if isinstance(depth, Unset):
        json_depth = UNSET
    elif isinstance(depth, GetSoilDataIsdasoilV2SoilpropertyGetDepthType0):
        json_depth = depth.value
    else:
        json_depth = depth
    params["depth"] = json_depth

    json_property_: Union[None, Unset, str]
    if isinstance(property_, Unset):
        json_property_ = UNSET
    elif isinstance(property_, GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0):
        json_property_ = property_.value
    else:
        json_property_ = property_
    params["property"] = json_property_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/isdasoil/v2/soilproperty",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, PropertyResponse]]:
    if response.status_code == 200:
        response_200 = PropertyResponse.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, PropertyResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    lon: float,
    lat: float,
    depth: Union[GetSoilDataIsdasoilV2SoilpropertyGetDepthType0, None, Unset] = UNSET,
    property_: Union[GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0, None, Unset] = UNSET,
) -> Response[Union[HTTPValidationError, PropertyResponse]]:
    """Get Soil Data

     Use the Soil Property endpoint to get soil property data for a specific location.

    Args:
        lon (float):
        lat (float):
        depth (Union[GetSoilDataIsdasoilV2SoilpropertyGetDepthType0, None, Unset]):
        property_ (Union[GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0, None, Unset]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PropertyResponse]]
    """

    kwargs = _get_kwargs(
        lon=lon,
        lat=lat,
        depth=depth,
        property_=property_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    lon: float,
    lat: float,
    depth: Union[GetSoilDataIsdasoilV2SoilpropertyGetDepthType0, None, Unset] = UNSET,
    property_: Union[GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0, None, Unset] = UNSET,
) -> Optional[Union[HTTPValidationError, PropertyResponse]]:
    """Get Soil Data

     Use the Soil Property endpoint to get soil property data for a specific location.

    Args:
        lon (float):
        lat (float):
        depth (Union[GetSoilDataIsdasoilV2SoilpropertyGetDepthType0, None, Unset]):
        property_ (Union[GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0, None, Unset]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PropertyResponse]
    """

    return sync_detailed(
        client=client,
        lon=lon,
        lat=lat,
        depth=depth,
        property_=property_,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    lon: float,
    lat: float,
    depth: Union[GetSoilDataIsdasoilV2SoilpropertyGetDepthType0, None, Unset] = UNSET,
    property_: Union[GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0, None, Unset] = UNSET,
) -> Response[Union[HTTPValidationError, PropertyResponse]]:
    """Get Soil Data

     Use the Soil Property endpoint to get soil property data for a specific location.

    Args:
        lon (float):
        lat (float):
        depth (Union[GetSoilDataIsdasoilV2SoilpropertyGetDepthType0, None, Unset]):
        property_ (Union[GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0, None, Unset]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, PropertyResponse]]
    """

    kwargs = _get_kwargs(
        lon=lon,
        lat=lat,
        depth=depth,
        property_=property_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    lon: float,
    lat: float,
    depth: Union[GetSoilDataIsdasoilV2SoilpropertyGetDepthType0, None, Unset] = UNSET,
    property_: Union[GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0, None, Unset] = UNSET,
) -> Optional[Union[HTTPValidationError, PropertyResponse]]:
    """Get Soil Data

     Use the Soil Property endpoint to get soil property data for a specific location.

    Args:
        lon (float):
        lat (float):
        depth (Union[GetSoilDataIsdasoilV2SoilpropertyGetDepthType0, None, Unset]):
        property_ (Union[GetSoilDataIsdasoilV2SoilpropertyGetPropertyType0, None, Unset]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, PropertyResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            lon=lon,
            lat=lat,
            depth=depth,
            property_=property_,
        )
    ).parsed
