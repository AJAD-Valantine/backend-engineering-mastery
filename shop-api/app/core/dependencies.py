from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.database import SessionLocal
from app.exceptions.user import InvalidCredentials, PermissionDenied
from app.models import Users
from app.repository.cart_item import CartRepository
from app.repository.password_reset_token import PasswordResetTokenRepository
from app.repository.product import ProductRepository
from app.repository.user import UserRepository
from app.services.auth import AuthService
from app.services.cart_item import CartService
from app.services.product import ProductService
from app.services.user import UserService


# --- DATABASE DEPENDENCY ---

def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DBSession = Annotated[Session, Depends(get_db)]


# --- USER REPOSITORY DEPENDENCY ---

def get_user_repository(
        db : DBSession
):
    return UserRepository(db)

# --- USER SERVICE DEPENDENCY ---

def get_user_service(
        user_repository : UserRepository = Depends(get_user_repository)
):
    return UserService(user_repository)


# --- PRODUCT REPOSITORY DEPENDENCY ---

def get_product_repository(
        db : DBSession
):
    return ProductRepository(db)

# --- PRODUCT SERVICE DEPENDENCY ---

def get_product_service(
        product_repository : ProductRepository = Depends(get_product_repository)
):
    return ProductService(product_repository)

# --- CART REPOSITORY DEPENDENCY ---

def get_cart_repository(
        db : DBSession
):
    return CartRepository(db)

# --- CART SERVICE DEPENDENCY ---

def get_cart_service(
        cart_repository : CartRepository = Depends(get_cart_repository),
        user_service : UserService = Depends(get_user_service),
        product_service : ProductService = Depends(get_product_service),

):
    return CartService(
        cart_repository=cart_repository,
        user_service=user_service,
        product_service=product_service
    )

# --- AUTH REPOSITORY DEPENDENCY ---

def get_password_reset_token_repository(db: DBSession):
    return PasswordResetTokenRepository(db)

# --- AUTH SERVICE DEPENDENCY ---

def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    user_service: UserService = Depends(get_user_service),
    reset_token_repository: PasswordResetTokenRepository = Depends(get_password_reset_token_repository),
):
    return AuthService(
        user_repository=user_repository,
        user_service=user_service,
        reset_token_repository=reset_token_repository,
    )

# --- AUTHENTICATION DEPENDENCY ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_repository : UserRepository = Depends(get_user_repository)
):

    result = security.verify_access_token(token)

    if result is None:
        raise InvalidCredentials

    str_user_id = result["user_id"]

    try:
        valid_uuid = UUID(str_user_id)
    except ValueError:
        raise InvalidCredentials

    user = user_repository.read_user_by_id(valid_uuid)

    if user is None:
        raise InvalidCredentials

    return user

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
CurrentUser = Annotated[Users, Depends(get_current_user)]

# --- AUTHORIZATION DEPENDENCIES ---

# - Admin Dependency

def require_admin(
        current_user : CurrentUser
):
    if current_user.role.lower() != "admin":
        raise PermissionDenied

    return current_user