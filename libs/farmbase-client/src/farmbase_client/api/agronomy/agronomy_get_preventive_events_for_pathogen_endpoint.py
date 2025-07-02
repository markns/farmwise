from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import EventRead
from fastapi.exceptions import RequestValidationError
from ...types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union


def _get_kwargs(
    pathogen_id: int,
    *,
    crop_id: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_crop_id: Union[None, Unset, str]
    if isinstance(crop_id, Unset):
        json_crop_id = UNSET
    else:
        json_crop_id = crop_id
    params["crop_id"] = json_crop_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/agronomy/events/pathogen/{pathogen_id}/preventive".format(
            pathogen_id=pathogen_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[RequestValidationError, list["EventRead"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = EventRead.model_validate(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[RequestValidationError, list["EventRead"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pathogen_id: int,
    *,
    client: AuthenticatedClient,
    crop_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[RequestValidationError, list["EventRead"]]]:
    """Get Preventive Events For Pathogen Endpoint

     Get events that prevent a specific pathogen.

    Args:
        pathogen_id (int):
        crop_id (Union[None, Unset, str]): Filter by crop

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, list['EventRead']]]
    """

    kwargs = _get_kwargs(
        pathogen_id=pathogen_id,
        crop_id=crop_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pathogen_id: int,
    *,
    client: AuthenticatedClient,
    crop_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[RequestValidationError, list["EventRead"]]]:
    """Get Preventive Events For Pathogen Endpoint

     Get events that prevent a specific pathogen.

    Args:
        pathogen_id (int):
        crop_id (Union[None, Unset, str]): Filter by crop

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, list['EventRead']]
    """

    return sync_detailed(
        pathogen_id=pathogen_id,
        client=client,
        crop_id=crop_id,
    ).parsed


async def asyncio_detailed(
    pathogen_id: int,
    *,
    client: AuthenticatedClient,
    crop_id: Union[None, Unset, str] = UNSET,
) -> Response[Union[RequestValidationError, list["EventRead"]]]:
    """Get Preventive Events For Pathogen Endpoint

     Get events that prevent a specific pathogen.

    Args:
        pathogen_id (int):
        crop_id (Union[None, Unset, str]): Filter by crop

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[RequestValidationError, list['EventRead']]]
    """

    kwargs = _get_kwargs(
        pathogen_id=pathogen_id,
        crop_id=crop_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pathogen_id: int,
    *,
    client: AuthenticatedClient,
    crop_id: Union[None, Unset, str] = UNSET,
) -> Optional[Union[RequestValidationError, list["EventRead"]]]:
    """Get Preventive Events For Pathogen Endpoint

     Get events that prevent a specific pathogen.

    Args:
        pathogen_id (int):
        crop_id (Union[None, Unset, str]): Filter by crop

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[RequestValidationError, list['EventRead']]
    """

    return (
        await asyncio_detailed(
            pathogen_id=pathogen_id,
            client=client,
            crop_id=crop_id,
        )
    ).parsed
