from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from fastapi.exceptions import RequestValidationError
from typing import cast


def _get_kwargs(
    *,
    latitude: float,
    longitude: float,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["latitude"] = latitude

    params["longitude"] = longitude

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/gaez/aez_classification",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[RequestValidationError, str]]:
    if response.status_code == 200:
        response_200 = cast(str, response.json())
        return response_200
    if response.status_code == 422:
        response_422 = RequestValidationError.model_validate(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[RequestValidationError, str]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    latitude: float,
    longitude: float,
) -> Response[Union[RequestValidationError, str]]:
    """Aez Classification

     Get the AEZ (Agro-Ecological Zone) classification for a given geographical coordinate.

    Args:
        latitude (float): The latitude coordinate
        longitude (float): The longitude coordinate

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, str]]
    """

    kwargs = _get_kwargs(
        latitude=latitude,
        longitude=longitude,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    latitude: float,
    longitude: float,
) -> Optional[Union[RequestValidationError, str]]:
    """Aez Classification

     Get the AEZ (Agro-Ecological Zone) classification for a given geographical coordinate.

    Args:
        latitude (float): The latitude coordinate
        longitude (float): The longitude coordinate

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, str]
    """

    return sync_detailed(
        client=client,
        latitude=latitude,
        longitude=longitude,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    latitude: float,
    longitude: float,
) -> Response[Union[RequestValidationError, str]]:
    """Aez Classification

     Get the AEZ (Agro-Ecological Zone) classification for a given geographical coordinate.

    Args:
        latitude (float): The latitude coordinate
        longitude (float): The longitude coordinate

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, str]]
    """

    kwargs = _get_kwargs(
        latitude=latitude,
        longitude=longitude,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    latitude: float,
    longitude: float,
) -> Optional[Union[RequestValidationError, str]]:
    """Aez Classification

     Get the AEZ (Agro-Ecological Zone) classification for a given geographical coordinate.

    Args:
        latitude (float): The latitude coordinate
        longitude (float): The longitude coordinate

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, str]
    """

    return (
        await asyncio_detailed(
            client=client,
            latitude=latitude,
            longitude=longitude,
        )
    ).parsed
