from uuid import UUID

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUserDep, RequireRoleDep, UserServiceDep
from app.models.user import User
from app.schemas.user import ChangeRoleRequest, UserResponse, UserUpdateRequest

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get(
    path="/me", status_code=status.HTTP_200_OK, response_model=UserResponse
)
def get_me(current_user: CurrentUserDep, user_service: UserServiceDep) -> User:
    return user_service.get_user_by_id(current_user.user_id)


@user_router.post(path="/update", status_code=200, response_model=UserResponse)
def update_me(
    current_user: CurrentUserDep,
    request_body: UserUpdateRequest,
    user_service: UserServiceDep,
) -> User:
    return user_service.update_user(current_user.user_id, request_body)


@user_router.post(
    path="/deactivate-my-account",
    status_code=200,
)
def deactivate_my_account(
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
) -> None:
    user_service.deactivate_user_account(current_user.user_id)


@user_router.get(
    path="/get/{user_id}",
    status_code=200,
    response_model=UserResponse,
)
def get_user_by_id(
    user_id: UUID, current_user: RequireRoleDep, user_service: UserServiceDep
) -> User:
    return user_service.get_user_by_id(user_id)


@user_router.post(
    path="/promote/{user_id}",
    status_code=200,
    response_model=UserResponse,
)
def change_user_role(
    user_id: UUID,
    current_user: RequireRoleDep,
    user_service: UserServiceDep,
    request_body: ChangeRoleRequest,
):
    return user_service.change_user_role(user_id, request_body.role)


@user_router.post(
    path="/deactivate/{user_id}",
    status_code=200,
)
def deactivate_user(
    user_id: UUID, user_service: UserServiceDep, current_user: RequireRoleDep
) -> None:
    user_service.deactivate_user_account(user_id)


@user_router.post(
    path="/activate/{user_id}",
    status_code=200,
)
def activate_user(
    user_id: UUID, user_service: UserServiceDep, current_user: RequireRoleDep
) -> None:
    user_service.deactivate_user_account(user_id)


@user_router.post(
    path="/hard-delete/{user_id}",
    status_code=200,
)
def hard_delete_user(
    user_id: UUID, user_service: UserServiceDep, current_user: RequireRoleDep
) -> None:
    user_service.deactivate_user_account(user_id)
