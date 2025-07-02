from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import CropCycleEventRead
from fastapi.exceptions import RequestValidationError
from typing import cast


def _get_kwargs(
    cycle_id: int,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/agronomy/crop-cycles/{cycle_id}/events".format(
            cycle_id=cycle_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[RequestValidationError, list["CropCycleEventRead"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CropCycleEventRead.model_validate(response_200_item_data)

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
) -> Response[Union[RequestValidationError, list["CropCycleEventRead"]]]:
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
) -> Response[Union[RequestValidationError, list["CropCycleEventRead"]]]:
    """Get Crop Cycle Events

     Get all events for a specific crop cycle.

    Args:
        cycle_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, list['CropCycleEventRead']]]
    """

    kwargs = _get_kwargs(
        cycle_id=cycle_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    cycle_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[RequestValidationError, list["CropCycleEventRead"]]]:
    """Get Crop Cycle Events

     Get all events for a specific crop cycle.

    Args:
        cycle_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, list['CropCycleEventRead']]
    """

    return sync_detailed(
        cycle_id=cycle_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    cycle_id: int,
    *,
    client: AuthenticatedClient,
) -> Response[Union[RequestValidationError, list["CropCycleEventRead"]]]:
    """Get Crop Cycle Events

     Get all events for a specific crop cycle.

    Args:
        cycle_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, list['CropCycleEventRead']]]
    """

    kwargs = _get_kwargs(
        cycle_id=cycle_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    cycle_id: int,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[RequestValidationError, list["CropCycleEventRead"]]]:
    """Get Crop Cycle Events

     Get all events for a specific crop cycle.

    Args:
        cycle_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, list['CropCycleEventRead']]
    """

    return (
        await asyncio_detailed(
            cycle_id=cycle_id,
            client=client,
        )
    ).parsed
