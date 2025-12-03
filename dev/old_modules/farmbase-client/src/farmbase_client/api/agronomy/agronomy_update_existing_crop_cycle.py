from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import BodyAgronomyUpdateExistingCropCycle
from ...models import CropCycleRead
from fastapi.exceptions import RequestValidationError
from typing import cast


def _get_kwargs(
    cycle_id: int,
    *,
    body: BodyAgronomyUpdateExistingCropCycle,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/agronomy/crop-cycles/{cycle_id}".format(
            cycle_id=cycle_id,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CropCycleRead, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = CropCycleRead.model_validate(response.json())

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
) -> Response[Union[CropCycleRead, RequestValidationError]]:
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
    body: BodyAgronomyUpdateExistingCropCycle,
) -> Response[Union[CropCycleRead, RequestValidationError]]:
    """Update Existing Crop Cycle

     Update an existing crop cycle.

    Args:
        cycle_id (int):
        body (BodyAgronomyUpdateExistingCropCycle):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CropCycleRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        cycle_id=cycle_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    cycle_id: int,
    *,
    client: AuthenticatedClient,
    body: BodyAgronomyUpdateExistingCropCycle,
) -> Optional[Union[CropCycleRead, RequestValidationError]]:
    """Update Existing Crop Cycle

     Update an existing crop cycle.

    Args:
        cycle_id (int):
        body (BodyAgronomyUpdateExistingCropCycle):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CropCycleRead, RequestValidationError]
    """

    return sync_detailed(
        cycle_id=cycle_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    cycle_id: int,
    *,
    client: AuthenticatedClient,
    body: BodyAgronomyUpdateExistingCropCycle,
) -> Response[Union[CropCycleRead, RequestValidationError]]:
    """Update Existing Crop Cycle

     Update an existing crop cycle.

    Args:
        cycle_id (int):
        body (BodyAgronomyUpdateExistingCropCycle):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CropCycleRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        cycle_id=cycle_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    cycle_id: int,
    *,
    client: AuthenticatedClient,
    body: BodyAgronomyUpdateExistingCropCycle,
) -> Optional[Union[CropCycleRead, RequestValidationError]]:
    """Update Existing Crop Cycle

     Update an existing crop cycle.

    Args:
        cycle_id (int):
        body (BodyAgronomyUpdateExistingCropCycle):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CropCycleRead, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            cycle_id=cycle_id,
            client=client,
            body=body,
        )
    ).parsed
