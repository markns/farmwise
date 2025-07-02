from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import PathogenClass
from ...models import PathogenPagination
from fastapi.exceptions import RequestValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    *,
    body: list[str],
    pathogen_class: Union[None, PathogenClass, Unset] = UNSET,
    severity: Union[None, Unset, int] = UNSET,
    crop_id: Union[None, Unset, str] = UNSET,
    is_activated: Union[Unset, bool] = True,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_pathogen_class: Union[None, Unset, str]
    if isinstance(pathogen_class, Unset):
        json_pathogen_class = UNSET
    elif isinstance(pathogen_class, PathogenClass):
        json_pathogen_class = pathogen_class.value
    else:
        json_pathogen_class = pathogen_class
    params["pathogen_class"] = json_pathogen_class

    json_severity: Union[None, Unset, int]
    if isinstance(severity, Unset):
        json_severity = UNSET
    else:
        json_severity = severity
    params["severity"] = json_severity

    json_crop_id: Union[None, Unset, str]
    if isinstance(crop_id, Unset):
        json_crop_id = UNSET
    else:
        json_crop_id = crop_id
    params["crop_id"] = json_crop_id

    params["is_activated"] = is_activated

    params["items_per_page"] = items_per_page

    params["page"] = page

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/agronomy/pathogens",
        "params": params,
    }

    _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[PathogenPagination, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = PathogenPagination.model_validate(response.json())

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
) -> Response[Union[PathogenPagination, RequestValidationError]]:
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
    pathogen_class: Union[None, PathogenClass, Unset] = UNSET,
    severity: Union[None, Unset, int] = UNSET,
    crop_id: Union[None, Unset, str] = UNSET,
    is_activated: Union[Unset, bool] = True,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
) -> Response[Union[PathogenPagination, RequestValidationError]]:
    """List Pathogens

     Get all pathogens with optional filtering and pagination.

    Args:
        pathogen_class (Union[None, PathogenClass, Unset]): Filter by pathogen class
        severity (Union[None, Unset, int]): Filter by severity level
        crop_id (Union[None, Unset, str]): Filter by affected crop
        is_activated (Union[Unset, bool]): Filter by activation status Default: True.
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PathogenPagination, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        pathogen_class=pathogen_class,
        severity=severity,
        crop_id=crop_id,
        is_activated=is_activated,
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
    pathogen_class: Union[None, PathogenClass, Unset] = UNSET,
    severity: Union[None, Unset, int] = UNSET,
    crop_id: Union[None, Unset, str] = UNSET,
    is_activated: Union[Unset, bool] = True,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
) -> Optional[Union[PathogenPagination, RequestValidationError]]:
    """List Pathogens

     Get all pathogens with optional filtering and pagination.

    Args:
        pathogen_class (Union[None, PathogenClass, Unset]): Filter by pathogen class
        severity (Union[None, Unset, int]): Filter by severity level
        crop_id (Union[None, Unset, str]): Filter by affected crop
        is_activated (Union[Unset, bool]): Filter by activation status Default: True.
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PathogenPagination, RequestValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
        pathogen_class=pathogen_class,
        severity=severity,
        crop_id=crop_id,
        is_activated=is_activated,
        items_per_page=items_per_page,
        page=page,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: list[str],
    pathogen_class: Union[None, PathogenClass, Unset] = UNSET,
    severity: Union[None, Unset, int] = UNSET,
    crop_id: Union[None, Unset, str] = UNSET,
    is_activated: Union[Unset, bool] = True,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
) -> Response[Union[PathogenPagination, RequestValidationError]]:
    """List Pathogens

     Get all pathogens with optional filtering and pagination.

    Args:
        pathogen_class (Union[None, PathogenClass, Unset]): Filter by pathogen class
        severity (Union[None, Unset, int]): Filter by severity level
        crop_id (Union[None, Unset, str]): Filter by affected crop
        is_activated (Union[Unset, bool]): Filter by activation status Default: True.
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PathogenPagination, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        pathogen_class=pathogen_class,
        severity=severity,
        crop_id=crop_id,
        is_activated=is_activated,
        items_per_page=items_per_page,
        page=page,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    body: list[str],
    pathogen_class: Union[None, PathogenClass, Unset] = UNSET,
    severity: Union[None, Unset, int] = UNSET,
    crop_id: Union[None, Unset, str] = UNSET,
    is_activated: Union[Unset, bool] = True,
    items_per_page: Union[Unset, int] = 100,
    page: Union[Unset, int] = 1,
) -> Optional[Union[PathogenPagination, RequestValidationError]]:
    """List Pathogens

     Get all pathogens with optional filtering and pagination.

    Args:
        pathogen_class (Union[None, PathogenClass, Unset]): Filter by pathogen class
        severity (Union[None, Unset, int]): Filter by severity level
        crop_id (Union[None, Unset, str]): Filter by affected crop
        is_activated (Union[Unset, bool]): Filter by activation status Default: True.
        items_per_page (Union[Unset, int]):  Default: 100.
        page (Union[Unset, int]):  Default: 1.
        body (list[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PathogenPagination, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            pathogen_class=pathogen_class,
            severity=severity,
            crop_id=crop_id,
            is_activated=is_activated,
            items_per_page=items_per_page,
            page=page,
        )
    ).parsed
