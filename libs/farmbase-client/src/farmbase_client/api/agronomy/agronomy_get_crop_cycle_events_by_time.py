from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import CropCycleEventRead
from ...models import ErrorResponse
from ...models import HTTPValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    cycle_id: int,
    *,
    start_day: Union[None, Unset, int] = UNSET,
    end_day: Union[None, Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

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
        "url": "/agronomy/crop-cycles/{cycle_id}/events/time-range".format(
            cycle_id=cycle_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, HTTPValidationError, list["CropCycleEventRead"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CropCycleEventRead.model_validate(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[ErrorResponse, HTTPValidationError, list["CropCycleEventRead"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    cycle_id: int,
    *,
    client: AuthenticatedClient,
    start_day: Union[None, Unset, int] = UNSET,
    end_day: Union[None, Unset, int] = UNSET,
) -> Response[Union[ErrorResponse, HTTPValidationError, list["CropCycleEventRead"]]]:
    """Get Crop Cycle Events By Time

     Get crop cycle events within a specific time range.

    Args:
        cycle_id (int):
        start_day (Union[None, Unset, int]): Start day filter
        end_day (Union[None, Unset, int]): End day filter

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, list['CropCycleEventRead']]]
    """

    kwargs = _get_kwargs(
        cycle_id=cycle_id,
        start_day=start_day,
        end_day=end_day,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    cycle_id: int,
    *,
    client: AuthenticatedClient,
    start_day: Union[None, Unset, int] = UNSET,
    end_day: Union[None, Unset, int] = UNSET,
) -> Optional[Union[ErrorResponse, HTTPValidationError, list["CropCycleEventRead"]]]:
    """Get Crop Cycle Events By Time

     Get crop cycle events within a specific time range.

    Args:
        cycle_id (int):
        start_day (Union[None, Unset, int]): Start day filter
        end_day (Union[None, Unset, int]): End day filter

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, list['CropCycleEventRead']]
    """

    return sync_detailed(
        cycle_id=cycle_id,
        client=client,
        start_day=start_day,
        end_day=end_day,
    ).parsed


async def asyncio_detailed(
    cycle_id: int,
    *,
    client: AuthenticatedClient,
    start_day: Union[None, Unset, int] = UNSET,
    end_day: Union[None, Unset, int] = UNSET,
) -> Response[Union[ErrorResponse, HTTPValidationError, list["CropCycleEventRead"]]]:
    """Get Crop Cycle Events By Time

     Get crop cycle events within a specific time range.

    Args:
        cycle_id (int):
        start_day (Union[None, Unset, int]): Start day filter
        end_day (Union[None, Unset, int]): End day filter

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, list['CropCycleEventRead']]]
    """

    kwargs = _get_kwargs(
        cycle_id=cycle_id,
        start_day=start_day,
        end_day=end_day,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    cycle_id: int,
    *,
    client: AuthenticatedClient,
    start_day: Union[None, Unset, int] = UNSET,
    end_day: Union[None, Unset, int] = UNSET,
) -> Optional[Union[ErrorResponse, HTTPValidationError, list["CropCycleEventRead"]]]:
    """Get Crop Cycle Events By Time

     Get crop cycle events within a specific time range.

    Args:
        cycle_id (int):
        start_day (Union[None, Unset, int]): Start day filter
        end_day (Union[None, Unset, int]): End day filter

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, list['CropCycleEventRead']]
    """

    return (
        await asyncio_detailed(
            cycle_id=cycle_id,
            client=client,
            start_day=start_day,
            end_day=end_day,
        )
    ).parsed
