from pydantic import EmailStr, Field
from schemas.base import AppBaseModel


class ResendVerificationRequest(AppBaseModel):
    email: EmailStr


class ForgotPasswordRequest(AppBaseModel):
    email: EmailStr


class ResetPasswordRequest(AppBaseModel):
    token: str
    new_password: str = Field(
        min_length=8,
        max_length=128,
        description="New password must be between 8 and 128 characters long.",
    )


class ChangePasswordRequest(AppBaseModel):
    current_password: str = Field(
        min_length=8,
        max_length=128,
        description="Current password must be between 8 and 128 characters long.",
    )
    new_password: str = Field(
        min_length=8,
        max_length=128,
        description="New password must be between 8 and 128 characters long.",
    )
