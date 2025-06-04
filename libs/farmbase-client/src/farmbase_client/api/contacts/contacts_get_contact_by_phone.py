from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models import ContactRead, ErrorResponse, HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    organization: str,
    *,
    phone: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["phone"] = phone

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization}/contacts/by-phone".format(
            organization=organization,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ContactRead, ErrorResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = ContactRead.model_validate(response.json())

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
) -> Response[Union[ContactRead, ErrorResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization: str,
    *,
    client: Union[AuthenticatedClient, Client],
    phone: str,
) -> Response[Union[ContactRead, ErrorResponse, HTTPValidationError]]:
    """Get a single contact by phone number.

    Args:
        organization (str):
        phone (str): Phone number in E.164 format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ContactRead, ErrorResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        phone=phone,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization: str,
    *,
    client: Union[AuthenticatedClient, Client],
    phone: str,
) -> Optional[Union[ContactRead, ErrorResponse, HTTPValidationError]]:
    """Get a single contact by phone number.

    Args:
        organization (str):
        phone (str): Phone number in E.164 format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ContactRead, ErrorResponse, HTTPValidationError]
    """

    return sync_detailed(
        organization=organization,
        client=client,
        phone=phone,
    ).parsed


async def asyncio_detailed(
    organization: str,
    *,
    client: Union[AuthenticatedClient, Client],
    phone: str,
) -> Response[Union[ContactRead, ErrorResponse, HTTPValidationError]]:
    """Get a single contact by phone number.

    Args:
        organization (str):
        phone (str): Phone number in E.164 format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ContactRead, ErrorResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        phone=phone,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization: str,
    *,
    client: Union[AuthenticatedClient, Client],
    phone: str,
) -> Optional[Union[ContactRead, ErrorResponse, HTTPValidationError]]:
    """Get a single contact by phone number.

    Args:
        organization (str):
        phone (str): Phone number in E.164 format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ContactRead, ErrorResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            client=client,
            phone=phone,
        )
    ).parsed
