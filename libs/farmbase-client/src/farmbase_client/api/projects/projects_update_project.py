from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models import ErrorResponse, HTTPValidationError, ProjectRead, ProjectUpdate
from ...types import Response


def _get_kwargs(
    organization: str,
    project_id: int,
    *,
    body: ProjectUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/{organization}/projects/{project_id}".format(
            organization=organization,
            project_id=project_id,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, HTTPValidationError, ProjectRead]]:
    if response.status_code == 200:
        response_200 = ProjectRead.model_validate(response.json())

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
) -> Response[Union[ErrorResponse, HTTPValidationError, ProjectRead]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    organization: str,
    project_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ProjectUpdate,
) -> Response[Union[ErrorResponse, HTTPValidationError, ProjectRead]]:
    """Update Project

     Update a project.

    Args:
        organization (str):
        project_id (int):
        body (ProjectUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, ProjectRead]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        project_id=project_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    organization: str,
    project_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ProjectUpdate,
) -> Optional[Union[ErrorResponse, HTTPValidationError, ProjectRead]]:
    """Update Project

     Update a project.

    Args:
        organization (str):
        project_id (int):
        body (ProjectUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, ProjectRead]
    """

    return sync_detailed(
        organization=organization,
        project_id=project_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    organization: str,
    project_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ProjectUpdate,
) -> Response[Union[ErrorResponse, HTTPValidationError, ProjectRead]]:
    """Update Project

     Update a project.

    Args:
        organization (str):
        project_id (int):
        body (ProjectUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, HTTPValidationError, ProjectRead]]
    """

    kwargs = _get_kwargs(
        organization=organization,
        project_id=project_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    organization: str,
    project_id: int,
    *,
    client: Union[AuthenticatedClient, Client],
    body: ProjectUpdate,
) -> Optional[Union[ErrorResponse, HTTPValidationError, ProjectRead]]:
    """Update Project

     Update a project.

    Args:
        organization (str):
        project_id (int):
        body (ProjectUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, HTTPValidationError, ProjectRead]
    """

    return (
        await asyncio_detailed(
            organization=organization,
            project_id=project_id,
            client=client,
            body=body,
        )
    ).parsed
