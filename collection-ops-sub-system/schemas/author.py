from pydantic import EmailStr

from schemas.base import AppBaseModel


class AuthorResponse(AppBaseModel):
    first_name: str
    last_name: str
    email: EmailStr
