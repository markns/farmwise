from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import ContactRead
from fastapi.exceptions import RequestValidationError
from typing import cast


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
) -> Optional[Union[ContactRead, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = ContactRead.model_validate(response.json())

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
) -> Response[Union[ContactRead, RequestValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization: str,
    *,
    client: AuthenticatedClient,
    phone: str,
) -> Response[Union[ContactRead, RequestValidationError]]:
    """Get a single contact by phone number.

    Args:
        organization (str):
        phone (str): Phone number in E.164 format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ContactRead, RequestValidationError]]
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
    client: AuthenticatedClient,
    phone: str,
) -> Optional[Union[ContactRead, RequestValidationError]]:
    """Get a single contact by phone number.

    Args:
        organization (str):
        phone (str): Phone number in E.164 format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ContactRead, RequestValidationError]
    """

    return sync_detailed(
        organization=organization,
        client=client,
        phone=phone,
    ).parsed


async def asyncio_detailed(
    organization: str,
    *,
    client: AuthenticatedClient,
    phone: str,
) -> Response[Union[ContactRead, RequestValidationError]]:
    """Get a single contact by phone number.

    Args:
        organization (str):
        phone (str): Phone number in E.164 format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ContactRead, RequestValidationError]]
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
    client: AuthenticatedClient,
    phone: str,
) -> Optional[Union[ContactRead, RequestValidationError]]:
    """Get a single contact by phone number.

    Args:
        organization (str):
        phone (str): Phone number in E.164 format

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ContactRead, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            client=client,
            phone=phone,
        )
    ).parsed
