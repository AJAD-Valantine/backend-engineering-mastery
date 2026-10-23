import secrets
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

from core.config import Settings
from core.email import EmailManager
from core.security import SecurityManager
from fastapi import HTTPException, Response, status
from httpx import AsyncClient
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from models.email_verification_token import EmailVerificationToken
from models.oauth_account import OAuthAccount
from models.password_reset_token import PasswordResetToken
from models.refresh_token import RefreshToken
from models.user import User
from repositories.email_verification_token import (
    EmailVerificationTokenRepository,
)
from repositories.password_reset_token import PasswordResetTokenRepository
from repositories.refresh_token import RefreshTokenRepository
from repositories.user import UserRepository
from schemas.auth import TokenResponse
from schemas.user import UserCreateRequest
from services.user import UserService


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        user_service: UserService,
        refresh_token_repository: RefreshTokenRepository,
        password_reset_token_repository: PasswordResetTokenRepository,
        email_verification_token_repository: EmailVerificationTokenRepository,
        settings: Settings,
        security_manager: SecurityManager,
        email_manager: EmailManager,
        client_ip: str,
        user_agent: str,
    ) -> None:

        self.user_repository = user_repository
        self.user_service = user_service
        self.refresh_token_repository = refresh_token_repository
        self.password_reset_token_repository = password_reset_token_repository
        self.email_verification_token_repository = email_verification_token_repository
        self.settings = settings
        self.security_manager = security_manager
        self.email_manager = email_manager
        self.client_ip = client_ip
        self.user_agent = user_agent

    def register_user(self, request: UserCreateRequest) -> User:
        return self.user_service.add_user(request)

    def verify_email(self, raw_token: str) -> None:

        hashed_email_verification_token: str = self.security_manager.hash_token(
            raw_token
        )

        stored_email_verification_token: EmailVerificationToken | None = (
            self.email_verification_token_repository.read_by_hash(
                hashed_email_verification_token
            )
        )

        now: datetime = datetime.now(UTC)

        if (
            stored_email_verification_token is None
            or stored_email_verification_token.expires_at.replace(tzinfo=UTC) < now
            or stored_email_verification_token.used_at is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email verification failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user: User | None = self.user_repository.read_by_id(
            stored_email_verification_token.user_id
        )

        if user is not None:
            self.user_repository.verify_user(user)

        self.email_verification_token_repository.mark_as_used(
            stored_email_verification_token
        )

    def resend_verification_email(self, email: str) -> None:

        user: User | None = self.user_repository.read_by_email(email)

        if user is None or user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email verification failed",
            )

        raw_email_verification_token: str = self.security_manager.generate_token()
        hashed_email_verification_token: str = self.security_manager.hash_token(
            raw_email_verification_token
        )

        new_email_verification_token = EmailVerificationToken(
            user_id=user.user_id,
            token_hash=hashed_email_verification_token,
            expires_at=datetime.now(UTC)
            + timedelta(days=self.settings.email_verification_token_expire_days),
        )

        self.email_verification_token_repository.create(new_email_verification_token)

        self.email_manager.send_verification_email(
            user.email, raw_email_verification_token
        )

    def authenticate_user(
        self,
        email: str,
        plain_password: str,
    ) -> TokenResponse:

        user: User | None = self.user_repository.read_by_email(email)

        if user is None or not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email verification required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user is None or not self.security_manager.verify_password(
            plain_password, user.hashed_password # pyright: ignore[reportArgumentType]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token: str = self.security_manager.create_access_token(user.user_id)
        refresh_token: str = self.security_manager.generate_token()

        hashed_refresh_token: str = self.security_manager.hash_token(refresh_token)

        now: datetime = datetime.now(UTC)

        token = RefreshToken(
            user_id=user.user_id,
            token_hash=hashed_refresh_token,
            expires_at=now + timedelta(days=self.settings.refresh_token_expire_days),
            created_at=now,
            ip_address=self.client_ip,
            user_agent=self.user_agent,
        )

        self.refresh_token_repository.create(token)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def refresh_tokens(self, raw_token: str) -> TokenResponse:

        token_hash: str = self.security_manager.hash_token(raw_token)
        stored_refresh_token: RefreshToken | None = (
            self.refresh_token_repository.read_by_hash(token_hash)
        )

        if stored_refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if stored_refresh_token.revoked_at is not None:
            self.refresh_token_repository.revoke_all_for_user(
                stored_refresh_token.user_id
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if stored_refresh_token.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        self.refresh_token_repository.revoke(stored_refresh_token)

        new_access_token: str = self.security_manager.create_access_token(
            stored_refresh_token.user_id # pyright: ignore[reportArgumentType]
        )
        new_refresh_token: str = self.security_manager.generate_token()

        hashed_refresh_token: str = self.security_manager.hash_token(new_refresh_token)

        now: datetime = datetime.now(UTC)

        token = RefreshToken(
            user_id=stored_refresh_token.user_id,
            token_hash=hashed_refresh_token,
            expires_at=now + timedelta(days=self.settings.refresh_token_expire_days),
            created_at=now,
            ip_address=self.client_ip,
            user_agent=self.user_agent,
        )

        self.refresh_token_repository.create(token)

        return TokenResponse(
            access_token=new_access_token, refresh_token=new_refresh_token
        )

    def logout(self, raw_token: str) -> None:

        token_hash: str = self.security_manager.hash_token(raw_token)
        stored: RefreshToken | None = self.refresh_token_repository.read_by_hash(
            token_hash
        )

        if stored is None or stored.revoked_at is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        self.refresh_token_repository.revoke(stored)

    def logout_all(self, raw_token: str) -> None:

        hashed_refresh_token: str = self.security_manager.hash_token(raw_token)

        stored_refresh_token: RefreshToken | None = (
            self.refresh_token_repository.read_by_hash(hashed_refresh_token)
        )

        if stored_refresh_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        self.refresh_token_repository.revoke_all_for_user(stored_refresh_token.user_id)

    def forgot_password(self, email: str) -> None:

        user: User | None = self.user_repository.read_by_email(email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password reset failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        raw_password_reset_token: str = self.security_manager.generate_token()
        hashed_password_reset_token: str = self.security_manager.hash_token(raw_password_reset_token)

        new_password_reset_token = PasswordResetToken(
            user_id=user.user_id,
            token_hash=hashed_password_reset_token,
            expires_at=datetime.now(UTC)
            + timedelta(minutes=self.settings.password_reset_expire_minutes),
        )

        self.password_reset_token_repository.create(new_password_reset_token)

        self.email_manager.send_reset_email(user.email, raw_password_reset_token)

    def reset_password(self, raw_token: str, new_password: str) -> None:

        hashed_password_reset_token: str = self.security_manager.hash_token(raw_token)
        stored_password_reset_token: PasswordResetToken | None = (
            self.password_reset_token_repository.read_by_hash(
                hashed_password_reset_token
            )
        )

        now: datetime = datetime.now(UTC)

        if (
            stored_password_reset_token is None
            or stored_password_reset_token.expires_at.replace(tzinfo=UTC) < now
            or stored_password_reset_token.used_at is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password reset failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        new_hashed_password: str = self.security_manager.hash_password(new_password)
        user: User | None = self.user_repository.read_by_id(
            stored_password_reset_token.user_id
        )

        if user is not None:
            self.user_repository.set_new_password(user, new_hashed_password)

        self.password_reset_token_repository.mark_as_used(stored_password_reset_token)

    def change_password(self, user: User, current_password: str, new_password: str) -> None:

        if not self.security_manager.verify_password(
            current_password, user.hashed_password # pyright: ignore[reportArgumentType]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password change failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        new_hashed_password: str = self.security_manager.hash_password(new_password)
        self.user_repository.set_new_password(user, new_hashed_password)
        self.refresh_token_repository.revoke_all_for_user(user.user_id)

    def get_active_sessions(self, user: User) -> Sequence[RefreshToken]:
        return self.refresh_token_repository.read_all_for_user(user.user_id)

    def logout_session(self, user: User, session_id: UUID) -> None:

        session: RefreshToken | None = self.refresh_token_repository.read_by_id(session_id)

        if session is None or session.user_id != user.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        self.refresh_token_repository.revoke(session)

    def logout_all_sessions(self, user: User) -> None:
        self.refresh_token_repository.revoke_all_for_user(user.user_id)

    def generate_state(self) -> str:
        return self.security_manager.generate_token()


    def set_state_cookie(self, response: Response, state: str) -> None:
        state_serializer = URLSafeTimedSerializer(
            self.settings.state_secret_key.get_secret_value()
        )

        signed_state: str = state_serializer.dumps(state)

        response.set_cookie(
            key=self.settings.state_cookie_name,
            value=signed_state,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=self.settings.state_max_age,
        )


    def verify_state(
        self,
        returned_state: str,
        state_cookie: str | None,
        response: Response,
    ) -> None:

        state_serializer = URLSafeTimedSerializer(self.settings.state_secret_key.get_secret_value())

        if state_cookie is None:
            raise HTTPException(status_code=400, detail="Missing state cookie")

        try:
            original_state = state_serializer.loads(state_cookie, max_age=self.settings.state_max_age)
        except SignatureExpired:
            raise HTTPException(status_code=400, detail="State expired — restart login")
        except BadSignature:
            raise HTTPException(status_code=400, detail="Invalid state")

        if not secrets.compare_digest(original_state, returned_state):
            raise HTTPException(status_code=400, detail="State mismatch")

        response.delete_cookie(self.settings.state_cookie_name)

    def authenticate_oauth_user(
        self,
        provider: str,
        account_id: str,
        email: str,
        first_name: str,
        last_name: str,
    ) -> TokenResponse:

        user: User | None = self.user_repository.read_by_email(email)

        if user is None:
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                hashed_password=None,
                is_verified=True,
                role="member",
            )
            user = self.user_repository.create(user)

        # 2. Link the OAuth account if it isn't already
        is_linked: bool = any(
            acc.oauth_name == provider and acc.account_id == account_id
            for acc in user.oauth_accounts
        )

        if not is_linked:
            new_oauth = OAuthAccount(
                oauth_name=provider,
                account_id=account_id,
                account_email=email,
                user_id=user.user_id,
            )
            self.user_repository.db.add(new_oauth)

        access_token: str = self.security_manager.create_access_token(user.user_id)
        refresh_token: str = self.security_manager.generate_token()
        hashed_refresh_token: str = self.security_manager.hash_token(refresh_token)

        now: datetime = datetime.now(UTC)
        token = RefreshToken(
            user_id=user.user_id,
            token_hash=hashed_refresh_token,
            expires_at=now + timedelta(days=self.settings.refresh_token_expire_days),
            created_at=now,
            ip_address=self.client_ip,
            user_agent=self.user_agent,
        )

        self.refresh_token_repository.create(token)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def url_for_google(self, state: str) -> str:

        params: dict[str, str] = {
            "client_id": self.settings.google_client_id,
            "redirect_uri": self.settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }

        auth_url = self.settings.google_auth_url / urlencode(params)
        return str(auth_url)


    async def exchange_code_for_tokens(
        self, code: str, client: AsyncClient
    ) -> dict[str, Any]:

        response = await client.post(
            url=self.settings.google_token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.settings.google_redirect_uri,
                "client_id": self.settings.google_client_id,
                "client_secret": self.settings.google_client_secret,
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code",
            )

        return response.json()

    async def fetch_user_info(
        self, access_token: str, client: AsyncClient
    ) -> dict[str, Any]:

        response = await client.get(
                url=self.settings.google_user_info_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info",
            )

        return response.json()
