from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import MarketSnapshotRead
from fastapi.exceptions import RequestValidationError
from typing import cast


def _get_kwargs(
    market_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/markets/{market_id}/snapshot".format(
            market_id=market_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[MarketSnapshotRead, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = MarketSnapshotRead.model_validate(response.json())

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
) -> Response[Union[MarketSnapshotRead, RequestValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    market_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[MarketSnapshotRead, RequestValidationError]]:
    """Get Market Snapshot Endpoint

     Get market snapshot with latest prices (3 months) for each commodity traded in this market.

    Args:
        market_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[MarketSnapshotRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        market_id=market_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    market_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[MarketSnapshotRead, RequestValidationError]]:
    """Get Market Snapshot Endpoint

     Get market snapshot with latest prices (3 months) for each commodity traded in this market.

    Args:
        market_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[MarketSnapshotRead, RequestValidationError]
    """

    return sync_detailed(
        market_id=market_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    market_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[MarketSnapshotRead, RequestValidationError]]:
    """Get Market Snapshot Endpoint

     Get market snapshot with latest prices (3 months) for each commodity traded in this market.

    Args:
        market_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[MarketSnapshotRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        market_id=market_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    market_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[MarketSnapshotRead, RequestValidationError]]:
    """Get Market Snapshot Endpoint

     Get market snapshot with latest prices (3 months) for each commodity traded in this market.

    Args:
        market_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[MarketSnapshotRead, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            market_id=market_id,
            client=client,
        )
    ).parsed
