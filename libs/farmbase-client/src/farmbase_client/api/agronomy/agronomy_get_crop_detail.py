from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import CropRead
from fastapi.exceptions import RequestValidationError
from typing import cast


def _get_kwargs(
    crop_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/agronomy/crops/{crop_id}".format(
            crop_id=crop_id,
        ),
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CropRead, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = CropRead.model_validate(response.json())

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
) -> Response[Union[CropRead, RequestValidationError]]:
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
) -> Response[Union[CropRead, RequestValidationError]]:
    """Get Crop Detail

     Get detailed information about a specific crop.

    Args:
        crop_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CropRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        crop_id=crop_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    crop_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[CropRead, RequestValidationError]]:
    """Get Crop Detail

     Get detailed information about a specific crop.

    Args:
        crop_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CropRead, RequestValidationError]
    """

    return sync_detailed(
        crop_id=crop_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    crop_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[CropRead, RequestValidationError]]:
    """Get Crop Detail

     Get detailed information about a specific crop.

    Args:
        crop_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CropRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        crop_id=crop_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    crop_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[CropRead, RequestValidationError]]:
    """Get Crop Detail

     Get detailed information about a specific crop.

    Args:
        crop_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CropRead, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            crop_id=crop_id,
            client=client,
        )
    ).parsed
