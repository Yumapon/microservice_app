from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.application_response import ApplicationResponse
from ...models.error_response import ErrorResponse
from ...types import Response


def _get_kwargs(
    contract_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/user/contracts/{contract_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ApplicationResponse, ErrorResponse]]:
    if response.status_code == 200:
        response_200 = ApplicationResponse.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ApplicationResponse, ErrorResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    contract_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ApplicationResponse, ErrorResponse]]:
    """契約詳細取得

     選択された契約IDに対応する詳細情報を取得するAPI。

    Args:
        contract_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApplicationResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        contract_id=contract_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    contract_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ApplicationResponse, ErrorResponse]]:
    """契約詳細取得

     選択された契約IDに対応する詳細情報を取得するAPI。

    Args:
        contract_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApplicationResponse, ErrorResponse]
    """

    return sync_detailed(
        contract_id=contract_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    contract_id: str,
    *,
    client: AuthenticatedClient,
) -> Response[Union[ApplicationResponse, ErrorResponse]]:
    """契約詳細取得

     選択された契約IDに対応する詳細情報を取得するAPI。

    Args:
        contract_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ApplicationResponse, ErrorResponse]]
    """

    kwargs = _get_kwargs(
        contract_id=contract_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    contract_id: str,
    *,
    client: AuthenticatedClient,
) -> Optional[Union[ApplicationResponse, ErrorResponse]]:
    """契約詳細取得

     選択された契約IDに対応する詳細情報を取得するAPI。

    Args:
        contract_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ApplicationResponse, ErrorResponse]
    """

    return (
        await asyncio_detailed(
            contract_id=contract_id,
            client=client,
        )
    ).parsed
