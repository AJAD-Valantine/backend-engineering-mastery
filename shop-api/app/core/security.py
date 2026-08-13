from datetime import UTC, datetime, timedelta

from jwt import InvalidTokenError, decode, encode
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)
    

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
    

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:

    to_encode = data.copy()

    if expires_delta is not None:
        expire = datetime.now(UTC) + expires_delta

    else:
        expire = datetime.now(UTC) + timedelta(minutes = settings.access_token_expire_minutes)

    to_encode.update({"exp" : expire})

    encoded_jwt = encode(
        payload = to_encode,
        key = settings.secret_key.get_secret_value(),
        algorithm = settings.algorithm
    )

    return encoded_jwt

def verify_access_token(token : str) -> dict[str,str] | None:

    try:
        decoded_jwt = decode(
            jwt = token,
            key = settings.secret_key.get_secret_value(),
            algorithms = [settings.algorithm],
            options = {"require": ["exp", "sub"]}
        )

    except InvalidTokenError:
        return None

    else:
        return {
            "user_id" : decoded_jwt["sub"],
            "expire_at" : decoded_jwt["exp"]
        }