from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models import ErrorResponse, FarmContactPagination, HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    organization: str,
    *,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    role: Union[None, Unset, str] = UNSET,
    farm_id: Union[None, Unset, int] = UNSET,
    contact_id: Union[None, Unset, int] = UNSET,
    contact_name: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["items_per_page"] = items_per_page

    params["page"] = page

    json_ordering: Union[Unset, list[str]] = UNSET
    if not isinstance(ordering, Unset):
        json_ordering = ordering

    params["ordering"] = json_ordering

    json_role: Union[None, Unset, str]
    if isinstance(role, Unset):
        json_role = UNSET
    else:
        json_role = role
    params["role"] = json_role

    json_farm_id: Union[None, Unset, int]
    if isinstance(farm_id, Unset):
        json_farm_id = UNSET
    else:
        json_farm_id = farm_id
    params["farm_id"] = json_farm_id

    json_contact_id: Union[None, Unset, int]
    if isinstance(contact_id, Unset):
        json_contact_id = UNSET
    else:
        json_contact_id = contact_id
    params["contact_id"] = json_contact_id

    json_contact_name: Union[None, Unset, str]
    if isinstance(contact_name, Unset):
        json_contact_name = UNSET
    else:
        json_contact_name = contact_name
    params["contact_name"] = json_contact_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization}/farms/contacts".format(
            organization=organization,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, FarmContactPagination, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = FarmContactPagination.model_validate(response.json())

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
) -> Response[Union[ErrorResponse, FarmContactPagination, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization: str,
    *,
    client: Union[AuthenticatedClient, Client],
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    role: Union[None, Unset, str] = UNSET,
    farm_id: Union[None, Unset, int] = UNSET,
    contact_id: Union[None, Unset, int] = UNSET,
    contact_name: Union[None, Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, FarmContactPagination, HTTPValidationError]]:
    """List Farm Contacts

     List farm contacts.

    Args:
        organization (str):
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        ordering (Union[Unset, list[str]]):
        role (Union[None, Unset, str]):
        farm_id (Union[None, Unset, int]):
        contact_id (Union[None, Unset, int]):
        contact_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, FarmContactPagination, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        items_per_page=items_per_page,
        page=page,
        ordering=ordering,
        role=role,
        farm_id=farm_id,
        contact_id=contact_id,
        contact_name=contact_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization: str,
    *,
    client: Union[AuthenticatedClient, Client],
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    role: Union[None, Unset, str] = UNSET,
    farm_id: Union[None, Unset, int] = UNSET,
    contact_id: Union[None, Unset, int] = UNSET,
    contact_name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, FarmContactPagination, HTTPValidationError]]:
    """List Farm Contacts

     List farm contacts.

    Args:
        organization (str):
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        ordering (Union[Unset, list[str]]):
        role (Union[None, Unset, str]):
        farm_id (Union[None, Unset, int]):
        contact_id (Union[None, Unset, int]):
        contact_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, FarmContactPagination, HTTPValidationError]
    """

    return sync_detailed(
        organization=organization,
        client=client,
        items_per_page=items_per_page,
        page=page,
        ordering=ordering,
        role=role,
        farm_id=farm_id,
        contact_id=contact_id,
        contact_name=contact_name,
    ).parsed


async def asyncio_detailed(
    organization: str,
    *,
    client: Union[AuthenticatedClient, Client],
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    role: Union[None, Unset, str] = UNSET,
    farm_id: Union[None, Unset, int] = UNSET,
    contact_id: Union[None, Unset, int] = UNSET,
    contact_name: Union[None, Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, FarmContactPagination, HTTPValidationError]]:
    """List Farm Contacts

     List farm contacts.

    Args:
        organization (str):
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        ordering (Union[Unset, list[str]]):
        role (Union[None, Unset, str]):
        farm_id (Union[None, Unset, int]):
        contact_id (Union[None, Unset, int]):
        contact_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, FarmContactPagination, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        items_per_page=items_per_page,
        page=page,
        ordering=ordering,
        role=role,
        farm_id=farm_id,
        contact_id=contact_id,
        contact_name=contact_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization: str,
    *,
    client: Union[AuthenticatedClient, Client],
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    role: Union[None, Unset, str] = UNSET,
    farm_id: Union[None, Unset, int] = UNSET,
    contact_id: Union[None, Unset, int] = UNSET,
    contact_name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, FarmContactPagination, HTTPValidationError]]:
    """List Farm Contacts

     List farm contacts.

    Args:
        organization (str):
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        ordering (Union[Unset, list[str]]):
        role (Union[None, Unset, str]):
        farm_id (Union[None, Unset, int]):
        contact_id (Union[None, Unset, int]):
        contact_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, FarmContactPagination, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            client=client,
            items_per_page=items_per_page,
            page=page,
            ordering=ordering,
            role=role,
            farm_id=farm_id,
            contact_id=contact_id,
            contact_name=contact_name,
        )
    ).parsed
