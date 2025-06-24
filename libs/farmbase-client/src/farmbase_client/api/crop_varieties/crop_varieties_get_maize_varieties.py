from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import CropVarietiesResponse
from ...models import ErrorResponse
from ...models import HTTPValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    *,
    altitude: Union[Unset, float] = UNSET,
    growing_period: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["altitude"] = altitude

    params["growing_period"] = growing_period

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/crop-varieties/maize",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CropVarietiesResponse, ErrorResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = CropVarietiesResponse.model_validate(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = ErrorResponse.model_validate(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = ErrorResponse.model_validate(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = ErrorResponse.model_validate(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = ErrorResponse.model_validate(response.json())

        return response_404
    if response.status_code == 500:
        response_500 = ErrorResponse.model_validate(response.json())

        return response_500
    if response.status_code == 422:
        response_422 = HTTPValidationError.model_validate(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[CropVarietiesResponse, ErrorResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    altitude: Union[Unset, float] = UNSET,
    growing_period: Union[Unset, int] = UNSET,
) -> Response[Union[CropVarietiesResponse, ErrorResponse, HTTPValidationError]]:
    """Get Maize Varieties

     Filters and returns maize varieties based on optional altitude and growing period criteria.

    Args:
        altitude (Union[Unset, float]):
        growing_period (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CropVarietiesResponse, ErrorResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        altitude=altitude,
        growing_period=growing_period,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    altitude: Union[Unset, float] = UNSET,
    growing_period: Union[Unset, int] = UNSET,
) -> Optional[Union[CropVarietiesResponse, ErrorResponse, HTTPValidationError]]:
    """Get Maize Varieties

     Filters and returns maize varieties based on optional altitude and growing period criteria.

    Args:
        altitude (Union[Unset, float]):
        growing_period (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CropVarietiesResponse, ErrorResponse, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        altitude=altitude,
        growing_period=growing_period,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    altitude: Union[Unset, float] = UNSET,
    growing_period: Union[Unset, int] = UNSET,
) -> Response[Union[CropVarietiesResponse, ErrorResponse, HTTPValidationError]]:
    """Get Maize Varieties

     Filters and returns maize varieties based on optional altitude and growing period criteria.

    Args:
        altitude (Union[Unset, float]):
        growing_period (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CropVarietiesResponse, ErrorResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        altitude=altitude,
        growing_period=growing_period,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    altitude: Union[Unset, float] = UNSET,
    growing_period: Union[Unset, int] = UNSET,
) -> Optional[Union[CropVarietiesResponse, ErrorResponse, HTTPValidationError]]:
    """Get Maize Varieties

     Filters and returns maize varieties based on optional altitude and growing period criteria.

    Args:
        altitude (Union[Unset, float]):
        growing_period (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CropVarietiesResponse, ErrorResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            altitude=altitude,
            growing_period=growing_period,
        )
    ).parsed
