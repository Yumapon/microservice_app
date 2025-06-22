from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.post_api_v1_quotes_product_type_product_type import PostApiV1QuotesProductTypeProductType
from ...models.quote_request import QuoteRequest
from ...models.quote_response import QuoteResponse
from ...types import Response


def _get_kwargs(
    product_type: PostApiV1QuotesProductTypeProductType,
    *,
    body: QuoteRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/quotes/{product_type}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, QuoteResponse]]:
    if response.status_code == 200:
        response_200 = QuoteResponse.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = ErrorResponse.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ErrorResponse, QuoteResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    product_type: PostApiV1QuotesProductTypeProductType,
    *,
    client: AuthenticatedClient,
    body: QuoteRequest,
) -> Response[Union[ErrorResponse, QuoteResponse]]:
    """保険見積もり作成

     認証済みユーザーが保険の見積もりを作成するAPI。

    Args:
        product_type (PostApiV1QuotesProductTypeProductType):
        body (QuoteRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, QuoteResponse]]
    """

    kwargs = _get_kwargs(
        product_type=product_type,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    product_type: PostApiV1QuotesProductTypeProductType,
    *,
    client: AuthenticatedClient,
    body: QuoteRequest,
) -> Optional[Union[ErrorResponse, QuoteResponse]]:
    """保険見積もり作成

     認証済みユーザーが保険の見積もりを作成するAPI。

    Args:
        product_type (PostApiV1QuotesProductTypeProductType):
        body (QuoteRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, QuoteResponse]
    """

    return sync_detailed(
        product_type=product_type,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    product_type: PostApiV1QuotesProductTypeProductType,
    *,
    client: AuthenticatedClient,
    body: QuoteRequest,
) -> Response[Union[ErrorResponse, QuoteResponse]]:
    """保険見積もり作成

     認証済みユーザーが保険の見積もりを作成するAPI。

    Args:
        product_type (PostApiV1QuotesProductTypeProductType):
        body (QuoteRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, QuoteResponse]]
    """

    kwargs = _get_kwargs(
        product_type=product_type,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    product_type: PostApiV1QuotesProductTypeProductType,
    *,
    client: AuthenticatedClient,
    body: QuoteRequest,
) -> Optional[Union[ErrorResponse, QuoteResponse]]:
    """保険見積もり作成

     認証済みユーザーが保険の見積もりを作成するAPI。

    Args:
        product_type (PostApiV1QuotesProductTypeProductType):
        body (QuoteRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, QuoteResponse]
    """

    return (
        await asyncio_detailed(
            product_type=product_type,
            client=client,
            body=body,
        )
    ).parsed
