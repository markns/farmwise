from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import CropPagination
from ...models import ErrorResponse
from ...models import HTTPValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    *,
    body: list[str],
    cultivation_type: Union[None, Unset, str] = UNSET,
    labor_level: Union[None, Unset, str] = UNSET,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_cultivation_type: Union[None, Unset, str]
    if isinstance(cultivation_type, Unset):
        json_cultivation_type = UNSET
    else:
        json_cultivation_type = cultivation_type
    params["cultivation_type"] = json_cultivation_type

    json_labor_level: Union[None, Unset, str]
    if isinstance(labor_level, Unset):
        json_labor_level = UNSET
    else:
        json_labor_level = labor_level
    params["labor_level"] = json_labor_level

    params["items_per_page"] = items_per_page

    params["page"] = page

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/agronomy/crops",
        "params": params,
    }

    _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CropPagination, ErrorResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = CropPagination.model_validate(response.json())

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
) -> Response[Union[CropPagination, ErrorResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: list[str],
    cultivation_type: Union[None, Unset, str] = UNSET,
    labor_level: Union[None, Unset, str] = UNSET,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
) -> Response[Union[CropPagination, ErrorResponse, HTTPValidationError]]:
    """List Crops

     Get all crops with optional filtering and pagination.

    Args:
        cultivation_type (Union[None, Unset, str]): Filter by cultivation type
        labor_level (Union[None, Unset, str]): Filter by labor level
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CropPagination, ErrorResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        cultivation_type=cultivation_type,
        labor_level=labor_level,
        items_per_page=items_per_page,
        page=page,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    body: list[str],
    cultivation_type: Union[None, Unset, str] = UNSET,
    labor_level: Union[None, Unset, str] = UNSET,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
) -> Optional[Union[CropPagination, ErrorResponse, HTTPValidationError]]:
    """List Crops

     Get all crops with optional filtering and pagination.

    Args:
        cultivation_type (Union[None, Unset, str]): Filter by cultivation type
        labor_level (Union[None, Unset, str]): Filter by labor level
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CropPagination, ErrorResponse, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
        cultivation_type=cultivation_type,
        labor_level=labor_level,
        items_per_page=items_per_page,
        page=page,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: list[str],
    cultivation_type: Union[None, Unset, str] = UNSET,
    labor_level: Union[None, Unset, str] = UNSET,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
) -> Response[Union[CropPagination, ErrorResponse, HTTPValidationError]]:
    """List Crops

     Get all crops with optional filtering and pagination.

    Args:
        cultivation_type (Union[None, Unset, str]): Filter by cultivation type
        labor_level (Union[None, Unset, str]): Filter by labor level
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CropPagination, ErrorResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        cultivation_type=cultivation_type,
        labor_level=labor_level,
        items_per_page=items_per_page,
        page=page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: list[str],
    cultivation_type: Union[None, Unset, str] = UNSET,
    labor_level: Union[None, Unset, str] = UNSET,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
) -> Optional[Union[CropPagination, ErrorResponse, HTTPValidationError]]:
    """List Crops

     Get all crops with optional filtering and pagination.

    Args:
        cultivation_type (Union[None, Unset, str]): Filter by cultivation type
        labor_level (Union[None, Unset, str]): Filter by labor level
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CropPagination, ErrorResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            cultivation_type=cultivation_type,
            labor_level=labor_level,
            items_per_page=items_per_page,
            page=page,
        )
    ).parsed
