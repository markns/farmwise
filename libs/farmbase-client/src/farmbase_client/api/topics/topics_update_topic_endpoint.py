from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from fastapi.exceptions import RequestValidationError
from ...models import TopicRead
from ...models import TopicUpdate
from typing import cast


def _get_kwargs(
    topic_id: int,
    *,
    body: TopicUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/topics/{topic_id}".format(
            topic_id=topic_id,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[RequestValidationError, TopicRead]]:
    if response.status_code == 200:
        response_200 = TopicRead.model_validate(response.json())

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
) -> Response[Union[RequestValidationError, TopicRead]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    topic_id: int,
    *,
    client: AuthenticatedClient,
    body: TopicUpdate,
) -> Response[Union[RequestValidationError, TopicRead]]:
    """Update Topic Endpoint

     Update a specific topic.

    Args:
        topic_id (int):
        body (TopicUpdate): Model for updating an existing topic.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, TopicRead]]
    """

    kwargs = _get_kwargs(
        topic_id=topic_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    topic_id: int,
    *,
    client: AuthenticatedClient,
    body: TopicUpdate,
) -> Optional[Union[RequestValidationError, TopicRead]]:
    """Update Topic Endpoint

     Update a specific topic.

    Args:
        topic_id (int):
        body (TopicUpdate): Model for updating an existing topic.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, TopicRead]
    """

    return sync_detailed(
        topic_id=topic_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    topic_id: int,
    *,
    client: AuthenticatedClient,
    body: TopicUpdate,
) -> Response[Union[RequestValidationError, TopicRead]]:
    """Update Topic Endpoint

     Update a specific topic.

    Args:
        topic_id (int):
        body (TopicUpdate): Model for updating an existing topic.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, TopicRead]]
    """

    kwargs = _get_kwargs(
        topic_id=topic_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    topic_id: int,
    *,
    client: AuthenticatedClient,
    body: TopicUpdate,
) -> Optional[Union[RequestValidationError, TopicRead]]:
    """Update Topic Endpoint

     Update a specific topic.

    Args:
        topic_id (int):
        body (TopicUpdate): Model for updating an existing topic.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, TopicRead]
    """

    return (
        await asyncio_detailed(
            topic_id=topic_id,
            client=client,
            body=body,
        )
    ).parsed
