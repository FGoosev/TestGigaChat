from http import HTTPStatus
from typing import Any, Dict, Optional

import httpx

from gigachat.context import (
    authorization_cvar,
    client_id_cvar,
    operation_id_cvar,
    request_id_cvar,
    service_id_cvar,
    session_id_cvar,
)
from gigachat.exceptions import AuthenticationError, ResponseError
from gigachat.models import Chat, ChatCompletion


def _get_kwargs(
    *,
    chat: Chat,
    access_token: Optional[str] = None,
) -> Dict[str, Any]:
    headers = {}

    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    authorization = authorization_cvar.get()
    client_id = client_id_cvar.get()
    session_id = session_id_cvar.get()
    request_id = request_id_cvar.get()
    service_id = service_id_cvar.get()
    operation_id = operation_id_cvar.get()

    if authorization:
        headers["Authorization"] = authorization
    if client_id:
        headers["X-Client-ID"] = client_id
    if session_id:
        headers["X-Session-ID"] = session_id
    if request_id:
        headers["X-Request-ID"] = request_id
    if service_id:
        headers["X-Service-ID"] = service_id
    if operation_id:
        headers["X-Operation-ID"] = operation_id

    return {
        "method": "POST",
        "url": "/chat/completions",
        "json": chat.dict(exclude_none=True, exclude={"stream"}),
        "headers": headers,
    }


def _build_response(response: httpx.Response) -> ChatCompletion:
    if response.status_code == HTTPStatus.OK:
        return ChatCompletion(**response.json())
    elif response.status_code == HTTPStatus.UNAUTHORIZED:
        raise AuthenticationError(response.url, response.status_code, response.content, response.headers)
    else:
        raise ResponseError(response.url, response.status_code, response.content, response.headers)


def sync(
    client: httpx.Client,
    *,
    chat: Chat,
    access_token: Optional[str] = None,
) -> ChatCompletion:
    kwargs = _get_kwargs(chat=chat, access_token=access_token)
    response = client.request(**kwargs)
    return _build_response(response)


async def asyncio(
    client: httpx.AsyncClient,
    *,
    chat: Chat,
    access_token: Optional[str] = None,
) -> ChatCompletion:
    kwargs = _get_kwargs(chat=chat, access_token=access_token)
    response = await client.request(**kwargs)
    return _build_response(response)
