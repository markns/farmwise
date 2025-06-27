from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import BodyAgronomyUpdateExistingCropCycle
from ...models import CropCycleRead
from ...models import ErrorResponse
from ...models import HTTPValidationError
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
) -> Optional[Union[CropCycleRead, ErrorResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = CropCycleRead.model_validate(response.json())

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
) -> Response[Union[CropCycleRead, ErrorResponse, HTTPValidationError]]:
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
) -> Response[Union[CropCycleRead, ErrorResponse, HTTPValidationError]]:
    """Update Existing Crop Cycle

     Update an existing crop cycle.

    Args:
        cycle_id (int):
        body (BodyAgronomyUpdateExistingCropCycle):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CropCycleRead, ErrorResponse, HTTPValidationError]]
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
) -> Optional[Union[CropCycleRead, ErrorResponse, HTTPValidationError]]:
    """Update Existing Crop Cycle

     Update an existing crop cycle.

    Args:
        cycle_id (int):
        body (BodyAgronomyUpdateExistingCropCycle):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CropCycleRead, ErrorResponse, HTTPValidationError]
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
) -> Response[Union[CropCycleRead, ErrorResponse, HTTPValidationError]]:
    """Update Existing Crop Cycle

     Update an existing crop cycle.

    Args:
        cycle_id (int):
        body (BodyAgronomyUpdateExistingCropCycle):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CropCycleRead, ErrorResponse, HTTPValidationError]]
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
) -> Optional[Union[CropCycleRead, ErrorResponse, HTTPValidationError]]:
    """Update Existing Crop Cycle

     Update an existing crop cycle.

    Args:
        cycle_id (int):
        body (BodyAgronomyUpdateExistingCropCycle):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CropCycleRead, ErrorResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            cycle_id=cycle_id,
            client=client,
            body=body,
        )
    ).parsed
