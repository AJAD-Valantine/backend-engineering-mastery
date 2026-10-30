from uuid import UUID

from core.dependencies import (
    AuthServiceDep,
    OwnerOrOfficialUser,
    require_permission,
    require_role_or_above,
)
from core.enums import Permission, UserRole
from fastapi import Depends, FastAPI
from schemas.auth import TokenResponse
from schemas.user import (
    UserLoginRequest,
)

app = FastAPI()

# ==========================================
# 0. LOGIN
# ==========================================


@app.post(path="/login", response_model=TokenResponse)
def login_user(
    request_body: UserLoginRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    return auth_service.authenticate_user(request_body.email, request_body.password)


# ==========================================
# 1. TESTING ROLE HIERARCHY
# ==========================================


@app.get(
    "/demo/admin-only", dependencies=[Depends(require_role_or_above(UserRole.ADMIN))]
)
def test_admin_only() -> dict[str, str]:
    return {"message": "Success! You have Admin privileges."}


@app.get(
    "/demo/mod-or-above",
    dependencies=[Depends(require_role_or_above(UserRole.MODERATOR))],
)
def test_mod_or_above() -> dict[str, str]:
    return {"message": "Success! You have at least Moderator privileges."}


@app.get(
    "/demo/user-or-above", dependencies=[Depends(require_role_or_above(UserRole.USER))]
)
def test_user_or_above() -> dict[str, str]:
    return {"message": "Success! You have basic User privileges or higher."}


# ==========================================
# 2. TESTING GRANULAR PERMISSIONS
# ==========================================


@app.post(
    "/demo/books", dependencies=[Depends(require_permission(Permission.CREATE_BOOK))]
)
def test_create_book() -> dict[str, str]:
    return {"message": "Success! You have permission to create books."}


@app.delete(
    "/demo/books/{id}",
    dependencies=[Depends(require_permission(Permission.DELETE_BOOK))],
)
def test_delete_book(id: int) -> dict[str, str]:
    return {"message": f"Success! You have permission to delete book {id}."}


@app.delete(
    "/demo/users/{id}",
    dependencies=[Depends(require_permission(Permission.DELETE_USER))],
)
def test_delete_user(id: UUID) -> dict[str, str]:
    return {"message": f"Success! You have permission to delete user {id}."}


# ==========================================
# 3. TESTING RESOURCE OWNERSHIP
# ==========================================


@app.get("/demo/users/{user_id}/private-data")
def test_private_data(user_id: UUID, resource: OwnerOrOfficialUser) -> dict[str, str]:
    return {
        "message": "Access granted to private data.",
    }
