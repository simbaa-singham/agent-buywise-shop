"""Tokens MCP sends to buywise-services (ADR-050): never the incoming token - always a swapped one.

- For a tool: the caller's token is swapped at Keycloak for `aud: buywise-services` with only the scope that tool
  needs (RFC 8693). MCP asks only for scopes the caller's token already has (Keycloak would add others).
- For MCP's own public lookups (store names): MCP's own client-credentials token.
Tokens are cached until 30 s before they expire; a swapped token never outlives the user's token.
"""

import hashlib
import time

import httpx

from ..config import settings
from .errors import ErrorCode, ToolFailure
from .identity import Principal

EXCHANGE = "urn:ietf:params:oauth:grant-type:token-exchange"
ACCESS_TOKEN = "urn:ietf:params:oauth:token-type:access_token"
MARGIN_S = 30


class TokenService:
    def __init__(self) -> None:
        self._cache: dict[str, tuple[str, float]] = {}
        self.client = httpx.AsyncClient(timeout=10)

    async def for_services(self, caller: Principal, scope: str) -> str:
        if scope not in caller.scopes:
            raise ToolFailure(ErrorCode.FORBIDDEN, f"This assistant is not allowed to use this ({scope}).")
        key = f"{hashlib.sha256(caller.token.encode()).hexdigest()}:{scope}"
        return await self._cached(
            key,
            {
                "grant_type": EXCHANGE,
                "subject_token": caller.token,
                "subject_token_type": ACCESS_TOKEN,
                "requested_token_type": ACCESS_TOKEN,
                "audience": settings.services_audience,
                "scope": scope,
            },
        )

    async def own(self, scope: str) -> str:
        return await self._cached(f"own:{scope}", {"grant_type": "client_credentials", "scope": scope})

    async def _cached(self, key: str, form: dict) -> str:
        token, expires = self._cache.get(key, ("", 0.0))
        if time.time() < expires - MARGIN_S:
            return token
        try:
            r = await self.client.post(
                settings.token_url,
                data=form | {"client_id": settings.client_id, "client_secret": settings.client_secret},
            )
        except httpx.HTTPError:
            raise ToolFailure(ErrorCode.UNAVAILABLE, "Sign-in service is not responding.", retryable=True) from None
        if r.status_code >= 500:
            raise ToolFailure(ErrorCode.UNAVAILABLE, "Sign-in service is not responding.", retryable=True)
        if r.status_code != 200:
            raise ToolFailure(ErrorCode.FORBIDDEN, "This request is not allowed for this login.")
        body = r.json()
        if len(self._cache) > 10_000:  # bounded: drop everything rather than grow without limit
            self._cache.clear()
        self._cache[key] = (body["access_token"], time.time() + body.get("expires_in", 60))
        return body["access_token"]


tokens = TokenService()
