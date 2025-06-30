from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import MessageRead
from fastapi.exceptions import RequestValidationError
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
) -> Optional[Union[MessageRead, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = MessageRead.model_validate(response.json())

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
) -> Response[Union[MessageRead, RequestValidationError]]:
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
) -> Response[Union[MessageRead, RequestValidationError]]:
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
        Response[Union[MessageRead, RequestValidationError]]
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
) -> Optional[Union[MessageRead, RequestValidationError]]:
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
        Union[MessageRead, RequestValidationError]
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
) -> Response[Union[MessageRead, RequestValidationError]]:
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
        Response[Union[MessageRead, RequestValidationError]]
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
) -> Optional[Union[MessageRead, RequestValidationError]]:
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
        Union[MessageRead, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            contact_id=contact_id,
            whatsapp_message_id=whatsapp_message_id,
            client=client,
        )
    ).parsed
