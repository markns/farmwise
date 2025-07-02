from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import FarmContactPagination
from fastapi.exceptions import RequestValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


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
) -> Optional[Union[FarmContactPagination, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = FarmContactPagination.model_validate(response.json())

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
) -> Response[Union[FarmContactPagination, RequestValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization: str,
    *,
    client: AuthenticatedClient,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    role: Union[None, Unset, str] = UNSET,
    farm_id: Union[None, Unset, int] = UNSET,
    contact_id: Union[None, Unset, int] = UNSET,
    contact_name: Union[None, Unset, str] = UNSET,
) -> Response[Union[FarmContactPagination, RequestValidationError]]:
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
        Response[Union[FarmContactPagination, RequestValidationError]]
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
    client: AuthenticatedClient,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    role: Union[None, Unset, str] = UNSET,
    farm_id: Union[None, Unset, int] = UNSET,
    contact_id: Union[None, Unset, int] = UNSET,
    contact_name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[FarmContactPagination, RequestValidationError]]:
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
        Union[FarmContactPagination, RequestValidationError]
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
    client: AuthenticatedClient,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    role: Union[None, Unset, str] = UNSET,
    farm_id: Union[None, Unset, int] = UNSET,
    contact_id: Union[None, Unset, int] = UNSET,
    contact_name: Union[None, Unset, str] = UNSET,
) -> Response[Union[FarmContactPagination, RequestValidationError]]:
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
        Response[Union[FarmContactPagination, RequestValidationError]]
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
    client: AuthenticatedClient,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    role: Union[None, Unset, str] = UNSET,
    farm_id: Union[None, Unset, int] = UNSET,
    contact_id: Union[None, Unset, int] = UNSET,
    contact_name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[FarmContactPagination, RequestValidationError]]:
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
        Union[FarmContactPagination, RequestValidationError]
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
