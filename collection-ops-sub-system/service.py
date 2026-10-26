from models.book import Book
from repository import BookRepository
from schemas.book import (
    BookFilter,
    BookSearch,
    BookSort,
    OffsetLimitBookResponse,
    OffsetLimitPagination,
    PageNumberPageSizePagination,
    PageNumPageSizeBookResponse,
)
from sqlalchemy.orm.query import Query


class BookService:
    def __init__(self, book_repository: BookRepository) -> None:
        self.book_repository = book_repository

    def filter_books(self, filter_prams: BookFilter):

        base_query: Query[Book] = self.book_repository.get_base_query()
        filterd_query: Query[Book] = self.book_repository.apply_book_filtering(
            base_query, filter_prams
        )

        return self.book_repository.execute_query(filterd_query)

    def sort_books(self, sort_prams: BookSort):

        base_query: Query[Book] = self.book_repository.get_base_query()
        filterd_query: Query[Book] = self.book_repository.apply_book_sorting(
            sort_prams, base_query
        )

        return self.book_repository.execute_query(filterd_query)

    def offset_limit_books(
        self, pagination_prams: OffsetLimitPagination
    ) -> OffsetLimitBookResponse:

        books = self.book_repository.get_books_with_simple_pagination(
            pagination_prams.offset, pagination_prams.limit
        )

        total: int = self.book_repository.count_books()

        return OffsetLimitBookResponse(
            data=books,  # pyright: ignore[reportArgumentType]
            total=total,
            offset=pagination_prams.offset,
            limit=pagination_prams.limit,
            has_next=(pagination_prams.offset + pagination_prams.limit) < total,
            has_prev=pagination_prams.offset > 0,
        )

    def page_number_page_size_books(self, pagination_prams: PageNumberPageSizePagination) -> PageNumPageSizeBookResponse:

        offset = (pagination_prams.page_number - 1) * pagination_prams.page_size

        books = self.book_repository.get_books_with_simple_pagination(
            offset, pagination_prams.page_size
        )

        total: int = self.book_repository.count_books()

        total_pages = -(-total // pagination_prams.page_size)

        return PageNumPageSizeBookResponse(
            data=books,  # pyright: ignore[reportArgumentType]
            total=total,
            page_number=pagination_prams.page_number,
            page_size=pagination_prams.page_size,
            total_pages=total_pages,
            has_next=pagination_prams.page_number < total_pages,
            has_prev=pagination_prams.page_number > 1,
        )

    def pattern_search_books(self, search_params: BookSearch):

        if search_params.q is None:
            return self.book_repository.get_books_with_simple_pagination()

        search_term: str = f"%{search_params.q}%"

        return self.book_repository.search_book_with_patterns(search_term)

    def full_txt_search_books(self, search_params: BookSearch):

        if search_params.q is None:
            return self.book_repository.get_books_with_simple_pagination()

        return self.book_repository.search_books_with_vectors(search_params.q)
