from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import ErrorResponse
from ...models import HTTPValidationError
from ...models import PathogenClass
from ...models import PathogenSearchResponse
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
) -> Optional[Union[ErrorResponse, HTTPValidationError, PathogenSearchResponse]]:
    if response.status_code == 200:
        response_200 = PathogenSearchResponse.model_validate(response.json())

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
) -> Response[Union[ErrorResponse, HTTPValidationError, PathogenSearchResponse]]:
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
) -> Response[Union[ErrorResponse, HTTPValidationError, PathogenSearchResponse]]:
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
        Response[Union[ErrorResponse, HTTPValidationError, PathogenSearchResponse]]
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
) -> Optional[Union[ErrorResponse, HTTPValidationError, PathogenSearchResponse]]:
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
        Union[ErrorResponse, HTTPValidationError, PathogenSearchResponse]
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
) -> Response[Union[ErrorResponse, HTTPValidationError, PathogenSearchResponse]]:
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
        Response[Union[ErrorResponse, HTTPValidationError, PathogenSearchResponse]]
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
) -> Optional[Union[ErrorResponse, HTTPValidationError, PathogenSearchResponse]]:
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
        Union[ErrorResponse, HTTPValidationError, PathogenSearchResponse]
    """

    return (
        await asyncio_detailed(
            crop_id=crop_id,
            client=client,
            pathogen_class=pathogen_class,
            severity=severity,
        )
    ).parsed
