from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.models.book import Book
from app.models.book_copy import BookCopy, CopyStatus
from app.repository.book import BookRepository
from app.schemas.book import BookCreateRequest, BookUpdateRequest


class BookService:
    def __init__(self, book_repository: BookRepository) -> None:
        self.book_repository = book_repository

    def add_book(self, book_data: BookCreateRequest) -> Book:

        existing_book = self.book_repository.read_by_isbn(book_data.isbn)
        
        if existing_book is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN '{book_data.isbn}' already exists",
            )

        today = datetime.now(UTC).date()
        if book_data.publish_date > today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Publish date cannot be in the future",
            )

        new_book = Book(
            title=book_data.title,
            isbn=book_data.isbn,
            publish_date=book_data.publish_date,
            page_count=book_data.page_count,
            language=book_data.language,
            description=book_data.description,
        )

        return self.book_repository.create(new_book)

    def get_book_by_id(self, book_id: int) -> Book:
        book = self.book_repository.read_by_id(book_id)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found",
            )
        return book

    def get_book_by_isbn(self, isbn: str) -> Book:
        clean_isbn = isbn.replace("-", "").replace(" ", "").strip()
        book = self.book_repository.read_by_isbn(clean_isbn)
        if book is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ISBN '{clean_isbn}' not found",
            )
        return book

    def get_all_books(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
    ) -> list[Book]:
        return self.book_repository.read_all(skip=skip, limit=limit, search=search)

    def update_book(self, book_id: int, book_data: BookUpdateRequest) -> Book:
        book = self.get_book_by_id(book_id)

        if book_data.isbn is not None and book_data.isbn != book.isbn:
            existing = self.book_repository.read_by_isbn(book_data.isbn)
            if existing is not None and existing.book_id != book_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Book with ISBN '{book_data.isbn}' already exists",
                )

        today = datetime.now(UTC).date()
        if book_data.publish_date is not None and book_data.publish_date > today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Publish date cannot be in the future",
            )

        update_dict = book_data.model_dump(exclude_unset=True)
        if not update_dict:
            return book

        return self.book_repository.update(book, update_dict)

    def delete_book(self, book_id: int) -> None:
        book = self.get_book_by_id(book_id)
        self.book_repository.delete(book)

    # -- Book Copy CRUD operations -- #

    def add_book_copy(
        self,
        book_id: int,
        copy_status: CopyStatus = CopyStatus.ACTIVE,
    ) -> BookCopy:
        # Validate that the book exists
        self.get_book_by_id(book_id)

        new_copy = BookCopy(
            book_id=book_id,
            status=copy_status,
        )
        return self.book_repository.create_copy(new_copy)

    def get_book_copy_by_id(self, copy_id: int) -> BookCopy:
        copy = self.book_repository.read_copy_by_id(copy_id)
        if copy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book copy with ID {copy_id} not found",
            )
        return copy

    def get_copies_for_book(self, book_id: int) -> list[BookCopy]:
        self.get_book_by_id(book_id)
        return self.book_repository.read_copies_by_book_id(book_id)

    def update_book_copy_status(
        self,
        copy_id: int,
        copy_status: CopyStatus,
    ) -> BookCopy:
        copy = self.get_book_copy_by_id(copy_id)
        return self.book_repository.update_copy(copy, {"status": copy_status})

    def delete_book_copy(self, copy_id: int) -> None:
        copy = self.get_book_copy_by_id(copy_id)
        self.book_repository.delete_copy(copy)
