from datetime import datetime

from pydantic import EmailStr, Field
from schemas.base import AppBaseModel


class RefreshTokenRequest(AppBaseModel):
    refresh_token: str


class TokenResponse(AppBaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ResendVerificationRequest(AppBaseModel):
    email: EmailStr


class ForgotPasswordRequest(AppBaseModel):
    email: EmailStr


class ResetPasswordRequest(AppBaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128, description="New password must be between 8 and 128 characters long.")

class ChangePasswordRequest(AppBaseModel):
    current_password: str = Field(min_length=8, max_length=128, description="Current password must be between 8 and 128 characters long.")
    new_password: str = Field(min_length=8, max_length=128, description="New password must be between 8 and 128 characters long.")


class RefreshTokenResponse(AppBaseModel):
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None

