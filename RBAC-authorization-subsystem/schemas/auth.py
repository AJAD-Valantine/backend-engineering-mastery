from schemas.base import AppBaseModel


class TokenResponse(AppBaseModel):
    access_token: str
    token_type: str = "bearer"



