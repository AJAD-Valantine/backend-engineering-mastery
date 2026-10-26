from core.dependencies import (
    BookFilterDep,
    BookSearchDep,
    BookServiceDep,
    BookSortDep,
    OffsetLimitDep,
    PageNumberPageSizeDep,
)
from fastapi import FastAPI
from schemas.book import (
    BookResponse,
    OffsetLimitBookResponse,
    PageNumPageSizeBookResponse,
)

app = FastAPI()


@app.get(path="/filter/books", response_model=list[BookResponse], status_code=200)
def filter_books_endpoint(
    query_params: BookFilterDep, book_service: BookServiceDep
):
    return book_service.filter_books(query_params)

@app.get(path="/sort/books", response_model=list[BookResponse], status_code=200)
def sort_books_endpoint(
    query_params: BookSortDep, book_service: BookServiceDep
):
    return book_service.sort_books(query_params)

@app.get(path="/like_ilike-search/books", response_model=list[BookResponse], status_code=200)
def pattern_search_books_endpoint(query_params: BookSearchDep, book_service: BookServiceDep):
    return book_service.pattern_search_books(query_params)

@app.get(
    path="/full_text-search/books", response_model=list[BookResponse], status_code=200
)
def full_text_search_books_endpoint(query_params: BookSearchDep, book_service: BookServiceDep):
    return book_service.full_txt_search_books(query_params)

@app.get(path="/offset-limit/books", response_model=OffsetLimitBookResponse)
def offset_limit_book_endpoint(
    query_params: OffsetLimitDep, book_service: BookServiceDep
) -> OffsetLimitBookResponse:
    return book_service.offset_limit_books(query_params)

@app.get(path="/page_number-page_size/books", response_model=PageNumPageSizeBookResponse)
def page_number_page_limit_book_endpoint(
    query_params: PageNumberPageSizeDep, book_service: BookServiceDep
) -> PageNumPageSizeBookResponse:
    return book_service.page_number_page_size_books(query_params)

