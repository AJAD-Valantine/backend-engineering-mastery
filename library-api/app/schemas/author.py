from base import AppBaseModel
from pydantic import EmailStr, Field

from app.schemas.book import BookResponse


class CreateAuthorRequest(AppBaseModel):
    first_name: str = Field()
    last_name: str = Field()
    email: EmailStr

class UpdateAuthorRequest(AppBaseModel):
    first_name: str | None = Field(None)
    last_name: str | None = Field(None)

class AuthorResponse(AppBaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    books: list[BookResponse]
