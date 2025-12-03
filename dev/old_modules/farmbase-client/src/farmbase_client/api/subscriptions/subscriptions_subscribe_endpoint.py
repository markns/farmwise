from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from fastapi.exceptions import RequestValidationError
from ...models import SubscriptionRead
from typing import cast


def _get_kwargs(
    contact_id: int,
    topic_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/subscriptions/subscribe/{contact_id}/{topic_id}".format(
            contact_id=contact_id,
            topic_id=topic_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[RequestValidationError, SubscriptionRead]]:
    if response.status_code == 200:
        response_200 = SubscriptionRead.model_validate(response.json())

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
) -> Response[Union[RequestValidationError, SubscriptionRead]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    contact_id: int,
    topic_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[RequestValidationError, SubscriptionRead]]:
    """Subscribe Endpoint

     Subscribe a contact to a topic.

    Args:
        contact_id (int):
        topic_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, SubscriptionRead]]
    """

    kwargs = _get_kwargs(
        contact_id=contact_id,
        topic_id=topic_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    contact_id: int,
    topic_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[RequestValidationError, SubscriptionRead]]:
    """Subscribe Endpoint

     Subscribe a contact to a topic.

    Args:
        contact_id (int):
        topic_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, SubscriptionRead]
    """

    return sync_detailed(
        contact_id=contact_id,
        topic_id=topic_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    contact_id: int,
    topic_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[RequestValidationError, SubscriptionRead]]:
    """Subscribe Endpoint

     Subscribe a contact to a topic.

    Args:
        contact_id (int):
        topic_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, SubscriptionRead]]
    """

    kwargs = _get_kwargs(
        contact_id=contact_id,
        topic_id=topic_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    contact_id: int,
    topic_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[RequestValidationError, SubscriptionRead]]:
    """Subscribe Endpoint

     Subscribe a contact to a topic.

    Args:
        contact_id (int):
        topic_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, SubscriptionRead]
    """

    return (
        await asyncio_detailed(
            contact_id=contact_id,
            topic_id=topic_id,
            client=client,
        )
    ).parsed
