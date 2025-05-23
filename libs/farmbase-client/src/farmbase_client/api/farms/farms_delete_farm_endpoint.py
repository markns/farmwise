from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import ErrorResponse
from ...models import HTTPValidationError
from typing import cast


def _get_kwargs(
    organization: str,
    farm_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/{organization}/farms/{farm_id}".format(
            organization=organization,
            farm_id=farm_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ErrorResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = response.json()
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
) -> Response[Union[Any, ErrorResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization: str,
    farm_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, ErrorResponse, HTTPValidationError]]:
    """Delete Farm Endpoint

     Delete a farm by ID.

    Args:
        organization (str):
        farm_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        farm_id=farm_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization: str,
    farm_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, ErrorResponse, HTTPValidationError]]:
    """Delete Farm Endpoint

     Delete a farm by ID.

    Args:
        organization (str):
        farm_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, HTTPValidationError]
    """

    return sync_detailed(
        organization=organization,
        farm_id=farm_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization: str,
    farm_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, ErrorResponse, HTTPValidationError]]:
    """Delete Farm Endpoint

     Delete a farm by ID.

    Args:
        organization (str):
        farm_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ErrorResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        farm_id=farm_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization: str,
    farm_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, ErrorResponse, HTTPValidationError]]:
    """Delete Farm Endpoint

     Delete a farm by ID.

    Args:
        organization (str):
        farm_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ErrorResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            farm_id=farm_id,
            client=client,
        )
    ).parsed
