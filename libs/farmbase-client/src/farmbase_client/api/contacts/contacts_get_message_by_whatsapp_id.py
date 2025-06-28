from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import ErrorResponse
from ...models import HTTPValidationError
from ...models import MessageRead
from typing import cast


def _get_kwargs(
    organization: str,
    contact_id: int,
    whatsapp_message_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization}/contacts/{contact_id}/messages/whatsapp/{whatsapp_message_id}".format(
            organization=organization,
            contact_id=contact_id,
            whatsapp_message_id=whatsapp_message_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, HTTPValidationError, MessageRead]]:
    if response.status_code == 200:
        response_200 = MessageRead.model_validate(response.json())

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
) -> Response[Union[ErrorResponse, HTTPValidationError, MessageRead]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization: str,
    contact_id: int,
    whatsapp_message_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ErrorResponse, HTTPValidationError, MessageRead]]:
    """Get Message By Whatsapp Id

     Get a message by WhatsApp message ID.

    Args:
        organization (str):
        contact_id (int): Contact ID
        whatsapp_message_id (str): WhatsApp message ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, MessageRead]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        contact_id=contact_id,
        whatsapp_message_id=whatsapp_message_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization: str,
    contact_id: int,
    whatsapp_message_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ErrorResponse, HTTPValidationError, MessageRead]]:
    """Get Message By Whatsapp Id

     Get a message by WhatsApp message ID.

    Args:
        organization (str):
        contact_id (int): Contact ID
        whatsapp_message_id (str): WhatsApp message ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, MessageRead]
    """

    return sync_detailed(
        organization=organization,
        contact_id=contact_id,
        whatsapp_message_id=whatsapp_message_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    organization: str,
    contact_id: int,
    whatsapp_message_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ErrorResponse, HTTPValidationError, MessageRead]]:
    """Get Message By Whatsapp Id

     Get a message by WhatsApp message ID.

    Args:
        organization (str):
        contact_id (int): Contact ID
        whatsapp_message_id (str): WhatsApp message ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, MessageRead]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        contact_id=contact_id,
        whatsapp_message_id=whatsapp_message_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization: str,
    contact_id: int,
    whatsapp_message_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ErrorResponse, HTTPValidationError, MessageRead]]:
    """Get Message By Whatsapp Id

     Get a message by WhatsApp message ID.

    Args:
        organization (str):
        contact_id (int): Contact ID
        whatsapp_message_id (str): WhatsApp message ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, MessageRead]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            contact_id=contact_id,
            whatsapp_message_id=whatsapp_message_id,
            client=client,
        )
    ).parsed
