from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from fastapi.exceptions import RequestValidationError
from ...models import SubscriptionCreate
from ...models import SubscriptionRead
from typing import cast


def _get_kwargs(
    *,
    body: SubscriptionCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/subscriptions",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    *,
    client: AuthenticatedClient,
    body: SubscriptionCreate,
) -> Response[Union[RequestValidationError, SubscriptionRead]]:
    """Create Subscription Endpoint

     Create a new subscription.

    Args:
        body (SubscriptionCreate): Model for creating a new subscription.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, SubscriptionRead]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: SubscriptionCreate,
) -> Optional[Union[RequestValidationError, SubscriptionRead]]:
    """Create Subscription Endpoint

     Create a new subscription.

    Args:
        body (SubscriptionCreate): Model for creating a new subscription.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, SubscriptionRead]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: SubscriptionCreate,
) -> Response[Union[RequestValidationError, SubscriptionRead]]:
    """Create Subscription Endpoint

     Create a new subscription.

    Args:
        body (SubscriptionCreate): Model for creating a new subscription.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, SubscriptionRead]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: SubscriptionCreate,
) -> Optional[Union[RequestValidationError, SubscriptionRead]]:
    """Create Subscription Endpoint

     Create a new subscription.

    Args:
        body (SubscriptionCreate): Model for creating a new subscription.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, SubscriptionRead]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
