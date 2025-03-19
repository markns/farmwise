from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import FieldPublic
from ...models import FieldUpdate
from ...models import HTTPValidationError
from typing import cast
from uuid import UUID


def _get_kwargs(
    farm_id: UUID,
    id: UUID,
    *,
    body: FieldUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v1/farms/{farm_id}/fields/{id}".format(
            farm_id=farm_id,
            id=id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[FieldPublic, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = FieldPublic.model_validate(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.model_validate(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[FieldPublic, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    farm_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient,
    body: FieldUpdate,
) -> Response[Union[FieldPublic, HTTPValidationError]]:
    """Update Field

     Update a field.

    Args:
        farm_id (UUID):
        id (UUID):
        body (FieldUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FieldPublic, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        farm_id=farm_id,
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    farm_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient,
    body: FieldUpdate,
) -> Optional[Union[FieldPublic, HTTPValidationError]]:
    """Update Field

     Update a field.

    Args:
        farm_id (UUID):
        id (UUID):
        body (FieldUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FieldPublic, HTTPValidationError]
    """

    return sync_detailed(
        farm_id=farm_id,
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    farm_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient,
    body: FieldUpdate,
) -> Response[Union[FieldPublic, HTTPValidationError]]:
    """Update Field

     Update a field.

    Args:
        farm_id (UUID):
        id (UUID):
        body (FieldUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[FieldPublic, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        farm_id=farm_id,
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    farm_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient,
    body: FieldUpdate,
) -> Optional[Union[FieldPublic, HTTPValidationError]]:
    """Update Field

     Update a field.

    Args:
        farm_id (UUID):
        id (UUID):
        body (FieldUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[FieldPublic, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            farm_id=farm_id,
            id=id,
            client=client,
            body=body,
        )
    ).parsed
