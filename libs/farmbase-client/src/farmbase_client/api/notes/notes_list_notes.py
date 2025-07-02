from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import NotePagination
from fastapi.exceptions import RequestValidationError
from ...types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime


def _get_kwargs(
    organization: str,
    *,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    farm_id: Union[None, Unset, int] = UNSET,
    field_id: Union[None, Unset, int] = UNSET,
    planting_id: Union[None, Unset, int] = UNSET,
    note_date: Union[None, Unset, datetime.date] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["items_per_page"] = items_per_page

    params["page"] = page

    json_ordering: Union[Unset, list[str]] = UNSET
    if not isinstance(ordering, Unset):
        json_ordering = ordering

    params["ordering"] = json_ordering

    json_farm_id: Union[None, Unset, int]
    if isinstance(farm_id, Unset):
        json_farm_id = UNSET
    else:
        json_farm_id = farm_id
    params["farm_id"] = json_farm_id

    json_field_id: Union[None, Unset, int]
    if isinstance(field_id, Unset):
        json_field_id = UNSET
    else:
        json_field_id = field_id
    params["field_id"] = json_field_id

    json_planting_id: Union[None, Unset, int]
    if isinstance(planting_id, Unset):
        json_planting_id = UNSET
    else:
        json_planting_id = planting_id
    params["planting_id"] = json_planting_id

    json_note_date: Union[None, Unset, str]
    if isinstance(note_date, Unset):
        json_note_date = UNSET
    elif isinstance(note_date, datetime.date):
        json_note_date = note_date.isoformat()
    else:
        json_note_date = note_date
    params["note_date"] = json_note_date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{organization}/notes".format(
            organization=organization,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[NotePagination, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = NotePagination.model_validate(response.json())

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
) -> Response[Union[NotePagination, RequestValidationError]]:
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
    farm_id: Union[None, Unset, int] = UNSET,
    field_id: Union[None, Unset, int] = UNSET,
    planting_id: Union[None, Unset, int] = UNSET,
    note_date: Union[None, Unset, datetime.date] = UNSET,
) -> Response[Union[NotePagination, RequestValidationError]]:
    """List Notes

     List notes.

    Args:
        organization (str):
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        ordering (Union[Unset, list[str]]):
        farm_id (Union[None, Unset, int]):
        field_id (Union[None, Unset, int]):
        planting_id (Union[None, Unset, int]):
        note_date (Union[None, Unset, datetime.date]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[NotePagination, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        items_per_page=items_per_page,
        page=page,
        ordering=ordering,
        farm_id=farm_id,
        field_id=field_id,
        planting_id=planting_id,
        note_date=note_date,
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
    farm_id: Union[None, Unset, int] = UNSET,
    field_id: Union[None, Unset, int] = UNSET,
    planting_id: Union[None, Unset, int] = UNSET,
    note_date: Union[None, Unset, datetime.date] = UNSET,
) -> Optional[Union[NotePagination, RequestValidationError]]:
    """List Notes

     List notes.

    Args:
        organization (str):
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        ordering (Union[Unset, list[str]]):
        farm_id (Union[None, Unset, int]):
        field_id (Union[None, Unset, int]):
        planting_id (Union[None, Unset, int]):
        note_date (Union[None, Unset, datetime.date]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[NotePagination, RequestValidationError]
    """

    return sync_detailed(
        organization=organization,
        client=client,
        items_per_page=items_per_page,
        page=page,
        ordering=ordering,
        farm_id=farm_id,
        field_id=field_id,
        planting_id=planting_id,
        note_date=note_date,
    ).parsed


async def asyncio_detailed(
    organization: str,
    *,
    client: AuthenticatedClient,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
    ordering: Union[Unset, list[str]] = UNSET,
    farm_id: Union[None, Unset, int] = UNSET,
    field_id: Union[None, Unset, int] = UNSET,
    planting_id: Union[None, Unset, int] = UNSET,
    note_date: Union[None, Unset, datetime.date] = UNSET,
) -> Response[Union[NotePagination, RequestValidationError]]:
    """List Notes

     List notes.

    Args:
        organization (str):
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        ordering (Union[Unset, list[str]]):
        farm_id (Union[None, Unset, int]):
        field_id (Union[None, Unset, int]):
        planting_id (Union[None, Unset, int]):
        note_date (Union[None, Unset, datetime.date]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[NotePagination, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        items_per_page=items_per_page,
        page=page,
        ordering=ordering,
        farm_id=farm_id,
        field_id=field_id,
        planting_id=planting_id,
        note_date=note_date,
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
    farm_id: Union[None, Unset, int] = UNSET,
    field_id: Union[None, Unset, int] = UNSET,
    planting_id: Union[None, Unset, int] = UNSET,
    note_date: Union[None, Unset, datetime.date] = UNSET,
) -> Optional[Union[NotePagination, RequestValidationError]]:
    """List Notes

     List notes.

    Args:
        organization (str):
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        ordering (Union[Unset, list[str]]):
        farm_id (Union[None, Unset, int]):
        field_id (Union[None, Unset, int]):
        planting_id (Union[None, Unset, int]):
        note_date (Union[None, Unset, datetime.date]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[NotePagination, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            client=client,
            items_per_page=items_per_page,
            page=page,
            ordering=ordering,
            farm_id=farm_id,
            field_id=field_id,
            planting_id=planting_id,
            note_date=note_date,
        )
    ).parsed
