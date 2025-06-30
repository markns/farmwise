from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import PathogenClass
from ...models import PathogenSearchResponse
from fastapi.exceptions import RequestValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    crop_id: str,
    *,
    pathogen_class: Union[None, PathogenClass, Unset] = UNSET,
    severity: Union[None, Unset, int] = UNSET,
) -> dict[str, Any]:
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

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/agronomy/pathogens/search/by-crop/{crop_id}".format(
            crop_id=crop_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[PathogenSearchResponse, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = PathogenSearchResponse.model_validate(response.json())

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
) -> Response[Union[PathogenSearchResponse, RequestValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    crop_id: str,
    *,
    client: AuthenticatedClient,
    pathogen_class: Union[None, PathogenClass, Unset] = UNSET,
    severity: Union[None, Unset, int] = UNSET,
) -> Response[Union[PathogenSearchResponse, RequestValidationError]]:
    """Search Pathogens For Crop

     Search pathogens that affect a specific crop.

    Args:
        crop_id (str):
        pathogen_class (Union[None, PathogenClass, Unset]):
        severity (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PathogenSearchResponse, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        crop_id=crop_id,
        pathogen_class=pathogen_class,
        severity=severity,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    crop_id: str,
    *,
    client: AuthenticatedClient,
    pathogen_class: Union[None, PathogenClass, Unset] = UNSET,
    severity: Union[None, Unset, int] = UNSET,
) -> Optional[Union[PathogenSearchResponse, RequestValidationError]]:
    """Search Pathogens For Crop

     Search pathogens that affect a specific crop.

    Args:
        crop_id (str):
        pathogen_class (Union[None, PathogenClass, Unset]):
        severity (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PathogenSearchResponse, RequestValidationError]
    """

    return sync_detailed(
        crop_id=crop_id,
        client=client,
        pathogen_class=pathogen_class,
        severity=severity,
    ).parsed


async def asyncio_detailed(
    crop_id: str,
    *,
    client: AuthenticatedClient,
    pathogen_class: Union[None, PathogenClass, Unset] = UNSET,
    severity: Union[None, Unset, int] = UNSET,
) -> Response[Union[PathogenSearchResponse, RequestValidationError]]:
    """Search Pathogens For Crop

     Search pathogens that affect a specific crop.

    Args:
        crop_id (str):
        pathogen_class (Union[None, PathogenClass, Unset]):
        severity (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[PathogenSearchResponse, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        crop_id=crop_id,
        pathogen_class=pathogen_class,
        severity=severity,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    crop_id: str,
    *,
    client: AuthenticatedClient,
    pathogen_class: Union[None, PathogenClass, Unset] = UNSET,
    severity: Union[None, Unset, int] = UNSET,
) -> Optional[Union[PathogenSearchResponse, RequestValidationError]]:
    """Search Pathogens For Crop

     Search pathogens that affect a specific crop.

    Args:
        crop_id (str):
        pathogen_class (Union[None, PathogenClass, Unset]):
        severity (Union[None, Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[PathogenSearchResponse, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            crop_id=crop_id,
            client=client,
            pathogen_class=pathogen_class,
            severity=severity,
        )
    ).parsed
