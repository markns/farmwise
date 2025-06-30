from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx


from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models import ProductRead
from ...models import ProductUpdate
from fastapi.exceptions import RequestValidationError
from typing import cast


def _get_kwargs(
    organization: str,
    product_id: int,
    *,
    body: ProductUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/{organization}/products/{product_id}".format(
            organization=organization,
            product_id=product_id,
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ProductRead, RequestValidationError]]:
    if response.status_code == 200:
        response_200 = ProductRead.model_validate(response.json())

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
) -> Response[Union[ProductRead, RequestValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization: str,
    product_id: int,
    *,
    client: AuthenticatedClient,
    body: ProductUpdate,
) -> Response[Union[ProductRead, RequestValidationError]]:
    """Update Product

     Update an existing product.

    Args:
        organization (str):
        product_id (int):
        body (ProductUpdate): Schema for updating an existing product.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ProductRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        product_id=product_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization: str,
    product_id: int,
    *,
    client: AuthenticatedClient,
    body: ProductUpdate,
) -> Optional[Union[ProductRead, RequestValidationError]]:
    """Update Product

     Update an existing product.

    Args:
        organization (str):
        product_id (int):
        body (ProductUpdate): Schema for updating an existing product.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ProductRead, RequestValidationError]
    """

    return sync_detailed(
        organization=organization,
        product_id=product_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization: str,
    product_id: int,
    *,
    client: AuthenticatedClient,
    body: ProductUpdate,
) -> Response[Union[ProductRead, RequestValidationError]]:
    """Update Product

     Update an existing product.

    Args:
        organization (str):
        product_id (int):
        body (ProductUpdate): Schema for updating an existing product.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ProductRead, RequestValidationError]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        product_id=product_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization: str,
    product_id: int,
    *,
    client: AuthenticatedClient,
    body: ProductUpdate,
) -> Optional[Union[ProductRead, RequestValidationError]]:
    """Update Product

     Update an existing product.

    Args:
        organization (str):
        product_id (int):
        body (ProductUpdate): Schema for updating an existing product.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ProductRead, RequestValidationError]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            product_id=product_id,
            client=client,
            body=body,
        )
    ).parsed
