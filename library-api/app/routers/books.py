from fastapi import APIRouter, status

from app.models.book import Book
from app.models.book_copy import BookCopy
from app.schemas.book import BookCreateRequest, BookResponse, BookUpdateRequest
from app.core.dependencies import BookServiceDep

book_router = APIRouter(prefix="/book", tags=["Authentication"])


@book_router.post(
    path="/create",
    status_code=status.HTTP_201_CREATED,
    response_model=BookResponse
)
def create_book(
    request_body: BookCreateRequest,
    book_service: BookServiceDep
) -> Book:
    return book_service.add_book(request_body)

@book_router.get(
    path="/get/{book_id}",
    status_code=status.HTTP_200_OK,
    response_model=BookResponse
)
def get_book(
    book_id: int,
    book_service: BookServiceDep
) -> Book:
    return book_service.get_book_by_id(book_id)

@book_router.get(
    path="/get/all", status_code=status.HTTP_200_OK, response_model=BookResponse
)
def get_all_book(book_id: int, book_service: BookServiceDep) -> Book:
    return book_service.get_all_books()
