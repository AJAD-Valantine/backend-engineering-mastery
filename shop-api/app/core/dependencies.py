from collections.abc import Generator
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.database import SessionLocal
from app.models import Users
from app.repository.cart_item import CartRepository
from app.repository.product import ProductRepository
from app.repository.user import UserRepository
from app.services.auth import AuthService
from app.services.cart_item import CartService
from app.services.product import ProductService
from app.services.user import UserService

# --- DATABASE DEPENDENCY ---

def get_db() -> Generator[Session, Any, None]:

    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DBSession = Annotated[Session, Depends(get_db)]


# --- USER REPOSITORY DEPENDENCY ---

def get_user_repository(
        db : DBSession
) -> UserRepository:
    return UserRepository(db)

# --- USER SERVICE DEPENDENCY ---

def get_user_service(
        user_repository : UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(user_repository)


# --- PRODUCT REPOSITORY DEPENDENCY ---

def get_product_repository(
        db : DBSession
) -> ProductRepository:
    return ProductRepository(db)

# --- PRODUCT SERVICE DEPENDENCY ---

def get_product_service(
        product_repository : ProductRepository = Depends(get_product_repository)
) -> ProductService:
    return ProductService(product_repository)

# --- CART REPOSITORY DEPENDENCY ---

def get_cart_repository(
        db : DBSession
) -> CartRepository:
    return CartRepository(db)

# --- CART SERVICE DEPENDENCY ---

def get_cart_service(
        cart_repository : CartRepository = Depends(get_cart_repository),
        user_service : UserService = Depends(get_user_service),
        product_service : ProductService = Depends(get_product_service),

) -> CartService:
    return CartService(
        cart_repository=cart_repository,
        user_service=user_service,
        product_service=product_service
    )

# --- AUTH REPOSITORY DEPENDENCY ---

# --- AUTH SERVICE DEPENDENCY ---

def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    user_service: UserService = Depends(get_user_service),
) -> AuthService:
    return AuthService(
        user_repository=user_repository,
        user_service=user_service,
    )

# --- AUTHENTICATION DEPENDENCY ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_repository : UserRepository = Depends(get_user_repository)
) -> Users:

    result: dict[str, str] | None = security.verify_access_token(token)

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if result is None:
        raise invalid_credentials

    str_user_id: str = result["user_id"]

    try:
        valid_uuid = UUID(str_user_id)
    except ValueError:
        raise invalid_credentials

    user: Users | None = user_repository.read_user_by_id(valid_uuid)

    if user is None:
        raise invalid_credentials

    return user

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[Users, Depends(get_current_user)]

# --- AUTHORIZATION DEPENDENCIES ---

# - Admin Dependency

def require_admin(
        current_user : CurrentUser
):
    if current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

    return current_user
