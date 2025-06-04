from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models import ErrorResponse, HTTPValidationError, OrganizationPagination
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    name: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["items_per_page"] = items_per_page

    params["page"] = page

    json_ordering: Union[Unset, list[str]] = UNSET
    if not isinstance(ordering, Unset):
        json_ordering = ordering

    params["ordering"] = json_ordering

    json_name: Union[None, Unset, str]
    if isinstance(name, Unset):
        json_name = UNSET
    else:
        json_name = name
    params["name"] = json_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/organizations",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]:
    if response.status_code == 200:
        response_200 = OrganizationPagination.model_validate(response.json())

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
) -> Response[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    name: Union[None, Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]:
    """Get Organizations

     Get all organizations.

    Args:
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        ordering (Union[Unset, list[str]]):
        name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]
    """

    kwargs = _get_kwargs(
        items_per_page=items_per_page,
        page=page,
        ordering=ordering,
        name=name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]:
    """Get Organizations

     Get all organizations.

    Args:
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        ordering (Union[Unset, list[str]]):
        name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, OrganizationPagination]
    """

    return sync_detailed(
        client=client,
        items_per_page=items_per_page,
        page=page,
        ordering=ordering,
        name=name,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    name: Union[None, Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]:
    """Get Organizations

     Get all organizations.

    Args:
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        ordering (Union[Unset, list[str]]):
        name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]
    """

    kwargs = _get_kwargs(
        items_per_page=items_per_page,
        page=page,
        ordering=ordering,
        name=name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]:
    """Get Organizations

     Get all organizations.

    Args:
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        ordering (Union[Unset, list[str]]):
        name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, OrganizationPagination]
    """

    return (
        await asyncio_detailed(
            client=client,
            items_per_page=items_per_page,
            page=page,
            ordering=ordering,
            name=name,
        )
    ).parsed
