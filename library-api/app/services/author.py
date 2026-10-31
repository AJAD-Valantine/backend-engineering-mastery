from collections.abc import Sequence

from fastapi import HTTPException

from app.models.author import Author
from app.repository.author import AuthorRepository
from app.schemas.author import CreateAuthorRequest, UpdateAuthorRequest


class AuthorService:

    def __init__(self, author_repository: AuthorRepository) -> None:
        self.author_repository = author_repository

    def add_author(self, author_data: CreateAuthorRequest) -> Author:

        author: Author | None = self.author_repository.read_by_email(author_data.email)

        if author is not None:
            raise HTTPException(
                status_code=400,
                detail="Email already exists",
            )

        new_author = Author(
            first_name = author_data.first_name,
            last_name = author_data.last_name,
            email = author_data.email
        )

        return self.author_repository.create(new_author)

    def get_author(self, author_id: int) -> Author:

        author: Author | None = self.author_repository.read_by_id(author_id)

        if author is None:
            raise HTTPException(
                status_code=400,
                detail="Author does not exist",
            )

        return author

    def get_all_authors(self) -> Sequence[Author]:
        return self.author_repository.read_all()

    def update_author(self, author_id: int, new_data: UpdateAuthorRequest) -> Author:

        updated_data = new_data.model_dump(exclude_unset=True)

        author: Author | None = self.author_repository.read_by_id(author_id)

        if author is None:
            raise HTTPException(
                status_code=400,
                detail="Author does not exist",
            )

        return self.author_repository.update(author, updated_data)

    def delete_author(self, author_id: int) -> None:

        author: Author | None = self.author_repository.read_by_id(author_id)

        if author is None:
            raise HTTPException(
                status_code=400,
                detail="Author does not exist",
            )

        self.author_repository.delete(author)

