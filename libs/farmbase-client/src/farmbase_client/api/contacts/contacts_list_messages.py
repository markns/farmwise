from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import MessageRead
from ...models import MessageType
from fastapi.exceptions import RequestValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    organization: str,
    contact_id: int,
    *,
    message_type: Union[MessageType, None, Unset] = UNSET,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_message_type: Union[None, Unset, str]
    if isinstance(message_type, Unset):
        json_message_type = UNSET
    elif isinstance(message_type, MessageType):
        json_message_type = message_type.value
    else:
        json_message_type = message_type
    params["message_type"] = json_message_type

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization}/contacts/{contact_id}/messages".format(
            organization=organization,
            contact_id=contact_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[RequestValidationError, list["MessageRead"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = MessageRead.model_validate(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[RequestValidationError, list["MessageRead"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization: str,
    contact_id: int,
    *,
    client: AuthenticatedClient,
    message_type: Union[MessageType, None, Unset] = UNSET,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
) -> Response[Union[RequestValidationError, list["MessageRead"]]]:
    """List Messages

     List messages for a contact.

    Args:
        organization (str):
        contact_id (int): Contact ID
        message_type (Union[MessageType, None, Unset]): Filter by message type
        limit (Union[Unset, int]): Number of messages to return Default: 100.
        offset (Union[Unset, int]): Number of messages to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, list['MessageRead']]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        contact_id=contact_id,
        message_type=message_type,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization: str,
    contact_id: int,
    *,
    client: AuthenticatedClient,
    message_type: Union[MessageType, None, Unset] = UNSET,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
) -> Optional[Union[RequestValidationError, list["MessageRead"]]]:
    """List Messages

     List messages for a contact.

    Args:
        organization (str):
        contact_id (int): Contact ID
        message_type (Union[MessageType, None, Unset]): Filter by message type
        limit (Union[Unset, int]): Number of messages to return Default: 100.
        offset (Union[Unset, int]): Number of messages to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, list['MessageRead']]
    """

    return sync_detailed(
        organization=organization,
        contact_id=contact_id,
        client=client,
        message_type=message_type,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    organization: str,
    contact_id: int,
    *,
    client: AuthenticatedClient,
    message_type: Union[MessageType, None, Unset] = UNSET,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
) -> Response[Union[RequestValidationError, list["MessageRead"]]]:
    """List Messages

     List messages for a contact.

    Args:
        organization (str):
        contact_id (int): Contact ID
        message_type (Union[MessageType, None, Unset]): Filter by message type
        limit (Union[Unset, int]): Number of messages to return Default: 100.
        offset (Union[Unset, int]): Number of messages to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, list['MessageRead']]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        contact_id=contact_id,
        message_type=message_type,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization: str,
    contact_id: int,
    *,
    client: AuthenticatedClient,
    message_type: Union[MessageType, None, Unset] = UNSET,
    limit: Union[Unset, int] = 100,
    offset: Union[Unset, int] = 0,
) -> Optional[Union[RequestValidationError, list["MessageRead"]]]:
    """List Messages

     List messages for a contact.

    Args:
        organization (str):
        contact_id (int): Contact ID
        message_type (Union[MessageType, None, Unset]): Filter by message type
        limit (Union[Unset, int]): Number of messages to return Default: 100.
        offset (Union[Unset, int]): Number of messages to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, list['MessageRead']]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            contact_id=contact_id,
            client=client,
            message_type=message_type,
            limit=limit,
            offset=offset,
        )
    ).parsed
