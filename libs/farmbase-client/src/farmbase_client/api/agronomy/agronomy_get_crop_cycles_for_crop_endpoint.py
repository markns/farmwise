from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import CropCycleRead
from ...models import ErrorResponse
from ...models import HTTPValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    crop_id: str,
    *,
    koppen_classification: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_koppen_classification: Union[None, Unset, str]
    if isinstance(koppen_classification, Unset):
        json_koppen_classification = UNSET
    else:
        json_koppen_classification = koppen_classification
    params["koppen_classification"] = json_koppen_classification

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/agronomy/crop-cycles/crop/{crop_id}".format(
            crop_id=crop_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, HTTPValidationError, list["CropCycleRead"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = CropCycleRead.model_validate(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[ErrorResponse, HTTPValidationError, list["CropCycleRead"]]]:
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
    koppen_classification: Union[None, Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, HTTPValidationError, list["CropCycleRead"]]]:
    """Get Crop Cycles For Crop Endpoint

     Get all crop cycles for a specific crop.

    Args:
        crop_id (str):
        koppen_classification (Union[None, Unset, str]): Filter by Köppen climate classification

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, list['CropCycleRead']]]
    """

    kwargs = _get_kwargs(
        crop_id=crop_id,
        koppen_classification=koppen_classification,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    crop_id: str,
    *,
    client: AuthenticatedClient,
    koppen_classification: Union[None, Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, HTTPValidationError, list["CropCycleRead"]]]:
    """Get Crop Cycles For Crop Endpoint

     Get all crop cycles for a specific crop.

    Args:
        crop_id (str):
        koppen_classification (Union[None, Unset, str]): Filter by Köppen climate classification

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, list['CropCycleRead']]
    """

    return sync_detailed(
        crop_id=crop_id,
        client=client,
        koppen_classification=koppen_classification,
    ).parsed


async def asyncio_detailed(
    crop_id: str,
    *,
    client: AuthenticatedClient,
    koppen_classification: Union[None, Unset, str] = UNSET,
) -> Response[Union[ErrorResponse, HTTPValidationError, list["CropCycleRead"]]]:
    """Get Crop Cycles For Crop Endpoint

     Get all crop cycles for a specific crop.

    Args:
        crop_id (str):
        koppen_classification (Union[None, Unset, str]): Filter by Köppen climate classification

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, list['CropCycleRead']]]
    """

    kwargs = _get_kwargs(
        crop_id=crop_id,
        koppen_classification=koppen_classification,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    crop_id: str,
    *,
    client: AuthenticatedClient,
    koppen_classification: Union[None, Unset, str] = UNSET,
) -> Optional[Union[ErrorResponse, HTTPValidationError, list["CropCycleRead"]]]:
    """Get Crop Cycles For Crop Endpoint

     Get all crop cycles for a specific crop.

    Args:
        crop_id (str):
        koppen_classification (Union[None, Unset, str]): Filter by Köppen climate classification

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, list['CropCycleRead']]
    """

    return (
        await asyncio_detailed(
            crop_id=crop_id,
            client=client,
            koppen_classification=koppen_classification,
        )
    ).parsed
