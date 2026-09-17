import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from jwt import InvalidTokenError, decode, encode
from pwdlib import PasswordHash

from app.core.config import Settings

settings = Settings()  # pyright: ignore[reportCallIssue]
password_hash: PasswordHash = PasswordHash.recommended()

# -- PASSWORD -- #


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# -- ACCESS TOKEN -- #


def create_access_token(user_id: UUID, expires_delta: timedelta | None = None) -> str:

    now: datetime = datetime.now(UTC)

    expire: datetime = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )

    token_data: dict[str, Any] = {
        "sub": str(user_id),
        "iss": "shop-api",
        "aud": "shop-api-client",
        "iat": now,
        "exp": expire,
        "type": "access",
    }

    encoded_access_token: str = encode(
        payload=token_data,
        key=settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    return encoded_access_token


def verify_access_token(token: str) -> str:

    try:
        decoded_jwt: dict[str, Any] = decode(
            jwt=token,
            key=settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True,
                "require": ["sub", "iss", "aud", "iat", "exp", "type"],
            },
            audience="shop-api-client",
            issuer="shop-api",
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if decoded_jwt["type"] != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return decoded_jwt["sub"]


# -- REFRESH / PASSWORD RESET / EMAIL VERIFICATION TOKENS -- #


def generate_token() -> str:

    return secrets.token_urlsafe(32)


def hash_token(raw_token: str) -> str:

    return hashlib.sha256(raw_token.encode()).hexdigest()
