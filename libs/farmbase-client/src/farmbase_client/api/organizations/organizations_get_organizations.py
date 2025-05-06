from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import ErrorResponse
from ...models import HTTPValidationError
from ...models import OrganizationPagination
from ...types import UNSET, Unset
from typing import cast
from typing import Union


def _get_kwargs(
    *,
    page: Union[Unset, int] = 1,
    items_per_page: Union[Unset, int] = 5,
    q: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    sort_by: Union[Unset, list[str]] = UNSET,
    descending: Union[Unset, list[bool]] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["items_per_page"] = items_per_page

    params["q"] = q

    params["filter"] = filter_

    json_sort_by: Union[Unset, list[str]] = UNSET
    if not isinstance(sort_by, Unset):
        json_sort_by = sort_by

    params["sortBy[]"] = json_sort_by

    json_descending: Union[Unset, list[bool]] = UNSET
    if not isinstance(descending, Unset):
        json_descending = descending

    params["descending[]"] = json_descending

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
    page: Union[Unset, int] = 1,
    items_per_page: Union[Unset, int] = 5,
    q: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    sort_by: Union[Unset, list[str]] = UNSET,
    descending: Union[Unset, list[bool]] = UNSET,
) -> Response[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]:
    """Get Organizations

     Get all organizations.

    Args:
        page (Union[Unset, int]):  Default: 1.
        items_per_page (Union[Unset, int]):  Default: 5.
        q (Union[Unset, str]):
        filter_ (Union[Unset, str]):
        sort_by (Union[Unset, list[str]]):
        descending (Union[Unset, list[bool]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]
    """

    kwargs = _get_kwargs(
        page=page,
        items_per_page=items_per_page,
        q=q,
        filter_=filter_,
        sort_by=sort_by,
        descending=descending,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 1,
    items_per_page: Union[Unset, int] = 5,
    q: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    sort_by: Union[Unset, list[str]] = UNSET,
    descending: Union[Unset, list[bool]] = UNSET,
) -> Optional[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]:
    """Get Organizations

     Get all organizations.

    Args:
        page (Union[Unset, int]):  Default: 1.
        items_per_page (Union[Unset, int]):  Default: 5.
        q (Union[Unset, str]):
        filter_ (Union[Unset, str]):
        sort_by (Union[Unset, list[str]]):
        descending (Union[Unset, list[bool]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, OrganizationPagination]
    """

    return sync_detailed(
        client=client,
        page=page,
        items_per_page=items_per_page,
        q=q,
        filter_=filter_,
        sort_by=sort_by,
        descending=descending,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 1,
    items_per_page: Union[Unset, int] = 5,
    q: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    sort_by: Union[Unset, list[str]] = UNSET,
    descending: Union[Unset, list[bool]] = UNSET,
) -> Response[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]:
    """Get Organizations

     Get all organizations.

    Args:
        page (Union[Unset, int]):  Default: 1.
        items_per_page (Union[Unset, int]):  Default: 5.
        q (Union[Unset, str]):
        filter_ (Union[Unset, str]):
        sort_by (Union[Unset, list[str]]):
        descending (Union[Unset, list[bool]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]
    """

    kwargs = _get_kwargs(
        page=page,
        items_per_page=items_per_page,
        q=q,
        filter_=filter_,
        sort_by=sort_by,
        descending=descending,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page: Union[Unset, int] = 1,
    items_per_page: Union[Unset, int] = 5,
    q: Union[Unset, str] = UNSET,
    filter_: Union[Unset, str] = UNSET,
    sort_by: Union[Unset, list[str]] = UNSET,
    descending: Union[Unset, list[bool]] = UNSET,
) -> Optional[Union[ErrorResponse, HTTPValidationError, OrganizationPagination]]:
    """Get Organizations

     Get all organizations.

    Args:
        page (Union[Unset, int]):  Default: 1.
        items_per_page (Union[Unset, int]):  Default: 5.
        q (Union[Unset, str]):
        filter_ (Union[Unset, str]):
        sort_by (Union[Unset, list[str]]):
        descending (Union[Unset, list[bool]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, OrganizationPagination]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            items_per_page=items_per_page,
            q=q,
            filter_=filter_,
            sort_by=sort_by,
            descending=descending,
        )
    ).parsed
