from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import NoteRead
from fastapi.exceptions import RequestValidationError
from typing import cast


def _get_kwargs(
    organization: str,
    note_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization}/notes/{note_id}".format(
            organization=organization,
            note_id=note_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[NoteRead, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = NoteRead.model_validate(response.json())

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
) -> Response[Union[NoteRead, RequestValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization: str,
    note_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[NoteRead, RequestValidationError]]:
    """Get Note

     Get a note by ID.

    Args:
        organization (str):
        note_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[NoteRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        note_id=note_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization: str,
    note_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[NoteRead, RequestValidationError]]:
    """Get Note

     Get a note by ID.

    Args:
        organization (str):
        note_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[NoteRead, RequestValidationError]
    """

    return sync_detailed(
        organization=organization,
        note_id=note_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization: str,
    note_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[NoteRead, RequestValidationError]]:
    """Get Note

     Get a note by ID.

    Args:
        organization (str):
        note_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[NoteRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        note_id=note_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization: str,
    note_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[NoteRead, RequestValidationError]]:
    """Get Note

     Get a note by ID.

    Args:
        organization (str):
        note_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[NoteRead, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            note_id=note_id,
            client=client,
        )
    ).parsed
