from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import FarmContactCreate
from ...models import FarmContactRead
from fastapi.exceptions import RequestValidationError
from typing import cast


def _get_kwargs(
    organization: str,
    *,
    body: FarmContactCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/{organization}/farms/contacts".format(
            organization=organization,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[FarmContactRead, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = FarmContactRead.model_validate(response.json())

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
) -> Response[Union[FarmContactRead, RequestValidationError]]:
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
    body: FarmContactCreate,
) -> Response[Union[FarmContactRead, RequestValidationError]]:
    """Create Farm Contact

     Create a new farm contact.

    Args:
        organization (str):
        body (FarmContactCreate): Model for creating a new FarmContact.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FarmContactRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization: str,
    *,
    client: AuthenticatedClient,
    body: FarmContactCreate,
) -> Optional[Union[FarmContactRead, RequestValidationError]]:
    """Create Farm Contact

     Create a new farm contact.

    Args:
        organization (str):
        body (FarmContactCreate): Model for creating a new FarmContact.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FarmContactRead, RequestValidationError]
    """

    return sync_detailed(
        organization=organization,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization: str,
    *,
    client: AuthenticatedClient,
    body: FarmContactCreate,
) -> Response[Union[FarmContactRead, RequestValidationError]]:
    """Create Farm Contact

     Create a new farm contact.

    Args:
        organization (str):
        body (FarmContactCreate): Model for creating a new FarmContact.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FarmContactRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization: str,
    *,
    client: AuthenticatedClient,
    body: FarmContactCreate,
) -> Optional[Union[FarmContactRead, RequestValidationError]]:
    """Create Farm Contact

     Create a new farm contact.

    Args:
        organization (str):
        body (FarmContactCreate): Model for creating a new FarmContact.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FarmContactRead, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            client=client,
            body=body,
        )
    ).parsed
