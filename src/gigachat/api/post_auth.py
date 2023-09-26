import uuid
from http import HTTPStatus
from typing import Any, Dict

import httpx

from gigachat.exceptions import AuthenticationError, ResponseError
from gigachat.models import AccessToken


def _get_kwargs(url: str, credentials: str, scope: str) -> Dict[str, Any]:
    return {
        "method": "POST",
        "url": url,
        "data": {"scope": scope},
        "headers": {
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Bearer {credentials}",
        },
    }


def _build_response(response: httpx.Response) -> AccessToken:
    if response.status_code == HTTPStatus.OK:
        return AccessToken(**response.json())
    elif response.status_code == HTTPStatus.UNAUTHORIZED:
        raise AuthenticationError(response.url, response.status_code, response.content, response.headers)
    else:
        raise ResponseError(response.url, response.status_code, response.content, response.headers)


def sync(client: httpx.Client, url: str, credentials: str, scope: str) -> AccessToken:
    kwargs = _get_kwargs(url, credentials, scope)
    response = client.request(**kwargs)
    return _build_response(response)


async def asyncio(client: httpx.AsyncClient, url: str, credentials: str, scope: str) -> AccessToken:
    kwargs = _get_kwargs(url, credentials, scope)
    response = await client.request(**kwargs)
    return _build_response(response)