from pydantic import EmailStr

from app.schemas.base import AppBaseModel


class RefreshTokenRequest(AppBaseModel):
    refresh_token: str


class TokenResponse(AppBaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(AppBaseModel):
    email: str


class ResetPasswordRequest(AppBaseModel):
    token: str
    new_password: str

class LoginRequest(AppBaseModel):
    email: EmailStr
    password: str
