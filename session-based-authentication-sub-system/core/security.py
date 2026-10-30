import hashlib
import secrets

from core.config import Settings
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

    # -- PASSWORD RESET TOKENS / EMAIL VERIFICATION TOKENS / SESSION IDs -- #

    def generate_token(self) -> str:

        return secrets.token_urlsafe(32)

    def hash_token(self, raw_token: str) -> str:

        return hashlib.sha256(raw_token.encode()).hexdigest()
