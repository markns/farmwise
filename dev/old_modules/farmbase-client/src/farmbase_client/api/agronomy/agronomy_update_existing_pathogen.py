from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import PathogenRead
from ...models import PathogenUpdate
from fastapi.exceptions import RequestValidationError
from typing import cast


def _get_kwargs(
    pathogen_id: int,
    *,
    body: PathogenUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/agronomy/pathogens/{pathogen_id}".format(
            pathogen_id=pathogen_id,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[PathogenRead, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = PathogenRead.model_validate(response.json())

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
) -> Response[Union[PathogenRead, RequestValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pathogen_id: int,
    *,
    client: AuthenticatedClient,
    body: PathogenUpdate,
) -> Response[Union[PathogenRead, RequestValidationError]]:
    """Update Existing Pathogen

     Update an existing pathogen.

    Args:
        pathogen_id (int):
        body (PathogenUpdate): Model for updating an existing Pathogen.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PathogenRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        pathogen_id=pathogen_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pathogen_id: int,
    *,
    client: AuthenticatedClient,
    body: PathogenUpdate,
) -> Optional[Union[PathogenRead, RequestValidationError]]:
    """Update Existing Pathogen

     Update an existing pathogen.

    Args:
        pathogen_id (int):
        body (PathogenUpdate): Model for updating an existing Pathogen.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PathogenRead, RequestValidationError]
    """

    return sync_detailed(
        pathogen_id=pathogen_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    pathogen_id: int,
    *,
    client: AuthenticatedClient,
    body: PathogenUpdate,
) -> Response[Union[PathogenRead, RequestValidationError]]:
    """Update Existing Pathogen

     Update an existing pathogen.

    Args:
        pathogen_id (int):
        body (PathogenUpdate): Model for updating an existing Pathogen.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PathogenRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        pathogen_id=pathogen_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pathogen_id: int,
    *,
    client: AuthenticatedClient,
    body: PathogenUpdate,
) -> Optional[Union[PathogenRead, RequestValidationError]]:
    """Update Existing Pathogen

     Update an existing pathogen.

    Args:
        pathogen_id (int):
        body (PathogenUpdate): Model for updating an existing Pathogen.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PathogenRead, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            pathogen_id=pathogen_id,
            client=client,
            body=body,
        )
    ).parsed
