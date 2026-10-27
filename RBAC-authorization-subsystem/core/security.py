from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from core.config import Settings
from fastapi import HTTPException, status
from jwt import InvalidTokenError, decode, encode
from pwdlib import PasswordHash


class SecurityManager:

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.password_hash = PasswordHash.recommended()

    # -- PASSWORD HASHING & VERIFICATION -- #

    def hash_password(self, password: str) -> str:
        return self.password_hash.hash(password)


    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.password_hash.verify(plain_password, hashed_password)


    # -- ACCESS TOKEN -- #

    def create_access_token(self, user_id: UUID, role: str, expires_delta: timedelta | None = None) -> str:

        now: datetime = datetime.now(UTC)

        expire: datetime = now + (
            expires_delta
            if expires_delta is not None
            else timedelta(minutes=self.settings.access_token_expire_minutes)
        )

        token_data: dict[str, Any] = {
            "sub": str(user_id),
            "role": role,
            "iat": now,
            "exp": expire,
            "type": "access",
        }

        encoded_access_token: str = encode(
            payload=token_data,
            key=self.settings.jwt_secret_key.get_secret_value(),
            algorithm=self.settings.algorithm,
        )

        return encoded_access_token


    def verify_access_token(self, token: str) -> str:

        try:
            decoded_jwt: dict[str, Any] = decode(
                jwt=token,
                key=self.settings.jwt_secret_key.get_secret_value(),
                algorithms=[self.settings.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "require": ["sub", "role", "iat", "exp", "type"],
                },
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
