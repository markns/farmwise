from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import ErrorResponse
from ...models import EventCategory
from ...models import EventSearchResponse
from ...models import HTTPValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    crop_id: str,
    *,
    event_category: Union[EventCategory, None, Unset] = UNSET,
    start_day: Union[None, Unset, int] = UNSET,
    end_day: Union[None, Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_event_category: Union[None, Unset, str]
    if isinstance(event_category, Unset):
        json_event_category = UNSET
    elif isinstance(event_category, EventCategory):
        json_event_category = event_category.value
    else:
        json_event_category = event_category
    params["event_category"] = json_event_category

    json_start_day: Union[None, Unset, int]
    if isinstance(start_day, Unset):
        json_start_day = UNSET
    else:
        json_start_day = start_day
    params["start_day"] = json_start_day

    json_end_day: Union[None, Unset, int]
    if isinstance(end_day, Unset):
        json_end_day = UNSET
    else:
        json_end_day = end_day
    params["end_day"] = json_end_day

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/agronomy/events/crop/{crop_id}".format(
            crop_id=crop_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, EventSearchResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = EventSearchResponse.model_validate(response.json())

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
) -> Response[Union[ErrorResponse, EventSearchResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    crop_id: str,
    *,
    client: AuthenticatedClient,
    event_category: Union[EventCategory, None, Unset] = UNSET,
    start_day: Union[None, Unset, int] = UNSET,
    end_day: Union[None, Unset, int] = UNSET,
) -> Response[Union[ErrorResponse, EventSearchResponse, HTTPValidationError]]:
    """Get Events For Crop Endpoint

     Get events relevant to a specific crop.

    Args:
        crop_id (str):
        event_category (Union[EventCategory, None, Unset]):
        start_day (Union[None, Unset, int]): Filter events starting from this day
        end_day (Union[None, Unset, int]): Filter events ending before this day

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, EventSearchResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        crop_id=crop_id,
        event_category=event_category,
        start_day=start_day,
        end_day=end_day,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    crop_id: str,
    *,
    client: AuthenticatedClient,
    event_category: Union[EventCategory, None, Unset] = UNSET,
    start_day: Union[None, Unset, int] = UNSET,
    end_day: Union[None, Unset, int] = UNSET,
) -> Optional[Union[ErrorResponse, EventSearchResponse, HTTPValidationError]]:
    """Get Events For Crop Endpoint

     Get events relevant to a specific crop.

    Args:
        crop_id (str):
        event_category (Union[EventCategory, None, Unset]):
        start_day (Union[None, Unset, int]): Filter events starting from this day
        end_day (Union[None, Unset, int]): Filter events ending before this day

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, EventSearchResponse, HTTPValidationError]
    """

    return sync_detailed(
        crop_id=crop_id,
        client=client,
        event_category=event_category,
        start_day=start_day,
        end_day=end_day,
    ).parsed


async def asyncio_detailed(
    crop_id: str,
    *,
    client: AuthenticatedClient,
    event_category: Union[EventCategory, None, Unset] = UNSET,
    start_day: Union[None, Unset, int] = UNSET,
    end_day: Union[None, Unset, int] = UNSET,
) -> Response[Union[ErrorResponse, EventSearchResponse, HTTPValidationError]]:
    """Get Events For Crop Endpoint

     Get events relevant to a specific crop.

    Args:
        crop_id (str):
        event_category (Union[EventCategory, None, Unset]):
        start_day (Union[None, Unset, int]): Filter events starting from this day
        end_day (Union[None, Unset, int]): Filter events ending before this day

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, EventSearchResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        crop_id=crop_id,
        event_category=event_category,
        start_day=start_day,
        end_day=end_day,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    crop_id: str,
    *,
    client: AuthenticatedClient,
    event_category: Union[EventCategory, None, Unset] = UNSET,
    start_day: Union[None, Unset, int] = UNSET,
    end_day: Union[None, Unset, int] = UNSET,
) -> Optional[Union[ErrorResponse, EventSearchResponse, HTTPValidationError]]:
    """Get Events For Crop Endpoint

     Get events relevant to a specific crop.

    Args:
        crop_id (str):
        event_category (Union[EventCategory, None, Unset]):
        start_day (Union[None, Unset, int]): Filter events starting from this day
        end_day (Union[None, Unset, int]): Filter events ending before this day

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, EventSearchResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            crop_id=crop_id,
            client=client,
            event_category=event_category,
            start_day=start_day,
            end_day=end_day,
        )
    ).parsed
