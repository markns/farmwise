from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from fastapi.exceptions import RequestValidationError
from typing import cast


def _get_kwargs(
    organization: str,
    contact_id: int,
    message_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/{organization}/contacts/{contact_id}/messages/{message_id}".format(
            organization=organization,
            contact_id=contact_id,
            message_id=message_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, RequestValidationError]]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 422:
        response_422 = RequestValidationError.model_validate(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, RequestValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization: str,
    contact_id: int,
    message_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, RequestValidationError]]:
    """Delete Message

     Delete a message.

    Args:
        organization (str):
        contact_id (int): Contact ID
        message_id (int): Message ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        contact_id=contact_id,
        message_id=message_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization: str,
    contact_id: int,
    message_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, RequestValidationError]]:
    """Delete Message

     Delete a message.

    Args:
        organization (str):
        contact_id (int): Contact ID
        message_id (int): Message ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, RequestValidationError]
    """

    return sync_detailed(
        organization=organization,
        contact_id=contact_id,
        message_id=message_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization: str,
    contact_id: int,
    message_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[Any, RequestValidationError]]:
    """Delete Message

     Delete a message.

    Args:
        organization (str):
        contact_id (int): Contact ID
        message_id (int): Message ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        contact_id=contact_id,
        message_id=message_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization: str,
    contact_id: int,
    message_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[Any, RequestValidationError]]:
    """Delete Message

     Delete a message.

    Args:
        organization (str):
        contact_id (int): Contact ID
        message_id (int): Message ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            contact_id=contact_id,
            message_id=message_id,
            client=client,
        )
    ).parsed
