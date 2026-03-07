from __future__ import annotations

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

_JWKS_URL = (
    "https://login.microsoftonline.com"
    f"/{settings.entra_tenant_id}/discovery/v2.0/keys"
)
_ISSUER = f"https://login.microsoftonline.com/{settings.entra_tenant_id}/v2.0"

_jwks_cache: dict[str, object] | None = None


def _get_jwks() -> dict[str, object]:
    global _jwks_cache
    if _jwks_cache is None:
        response = httpx.get(_JWKS_URL)
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache  # type: ignore[return-value]


def verify_token(token: str = Depends(oauth2_scheme)) -> dict[str, object]:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        jwks = _get_jwks()
        payload: dict[str, object] = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.entra_client_id,
            issuer=_ISSUER,
        )
        return payload
    except JWTError:
        raise credentials_error
