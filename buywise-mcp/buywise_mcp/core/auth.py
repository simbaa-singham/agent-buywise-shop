"""MCP as an OAuth resource server (ADR-050): every request carries a Keycloak token, checked here.

Checked: signature (Keycloak's published keys), issuer = our realm only (RFC 9207), audience = buywise-mcp, expiry.
A token for anyone else - e.g. the user's own token, which is for the agent - is refused: no token passthrough.
The SDK's middleware calls `verify_token` and answers 401 with a pointer to our resource metadata (RFC 9728);
which scope and role each tool needs is checked per tool in identity.py.
"""

import asyncio
import logging

import jwt
from jwt import PyJWKClient
from mcp.server.auth.provider import AccessToken

from ..config import settings

log = logging.getLogger("buywise_mcp.auth")


class KeycloakTokenVerifier:
    def __init__(self) -> None:
        self._keys: PyJWKClient | None = None
        self._keys_url = ""

    def _jwks(self) -> PyJWKClient:
        if self._keys is None or self._keys_url != settings.jwks:  # keys are cached; refetched on an unknown key id
            self._keys, self._keys_url = PyJWKClient(settings.jwks, cache_keys=True, lifespan=300), settings.jwks
        return self._keys

    def _decode(self, token: str) -> dict:
        key = self._jwks().get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            key.key,
            algorithms=["RS256"],
            audience=settings.audience,
            issuer=settings.issuer,
            options={"require": ["exp", "iss", "aud", "azp"]},
            leeway=10,
        )

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            claims = await asyncio.to_thread(self._decode, token)  # first call fetches Keycloak's keys
        except jwt.PyJWTError as e:
            log.info("token refused: %s", type(e).__name__)
            return None
        return AccessToken(
            token=token,
            client_id=claims["azp"],
            scopes=claims.get("scope", "").split(),
            expires_at=claims["exp"],
            subject=claims.get("sub"),
            claims=claims,
        )


verifier = KeycloakTokenVerifier()
