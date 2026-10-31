from fastapi import APIRouter

from app.core.dependencies import AuthorServiceDep, RequireRoleDep
from app.models.author import Author
from app.schemas.author import AuthorResponse, CreateAuthorRequest, UpdateAuthorRequest

author_router = APIRouter(prefix="author", tags=["Author"])

@author_router.post(
    path="/create",
    response_model=AuthorResponse,
    status_code=200,
)
def create_author(
    author_service: AuthorServiceDep,
    current_user: RequireRoleDep,
    request_body: CreateAuthorRequest
) -> Author:
    return author_service.add_author(request_body)

@author_router.get(
    path="/get/{author_id}",
    response_model=AuthorResponse,
    status_code=200,
)
def find_author(
    author_service: AuthorServiceDep,
    author_id: int,
) -> Author:
    return author_service.get_author(author_id)

@author_router.get(
    path="/get",
    response_model=list[AuthorResponse],
    status_code=200,
)
def find_authors(
    author_service: AuthorServiceDep,
):
    return author_service.get_all_authors()


@author_router.post(
    path="/update{author_id}",
    response_model=AuthorResponse,
    status_code=200,
)
def update_author_details(
    request_body: UpdateAuthorRequest,
    author_service: AuthorServiceDep,
    current_user: RequireRoleDep,
    author_id: int,
) -> Author:
    return author_service.update_author(author_id, request_body)


@author_router.post(
    path="/delete{author_id}",
    response_model=None,
    status_code=200,
)
def delete_author(
    author_service: AuthorServiceDep,
    current_user: RequireRoleDep,
    author_id: int,
) -> None:
    return author_service.delete_author(author_id)

