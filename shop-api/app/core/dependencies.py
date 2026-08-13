from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core import security
from app.core.database import SessionLocal
from app.exceptions.user import InvalidCredentials, PermissionDenied
from app.models import Users
from app.repository.user import UserRepository

# --- DATABASE DEPENDENCY ---

def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- AUTHENTICATION DEPENDENCY ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):

    result = security.verify_access_token(token)

    if result is None:
        raise InvalidCredentials

    str_user_id = result["user_id"]

    try:
        valid_uuid = UUID(str_user_id)
    except ValueError:
        raise InvalidCredentials

    user_repo = UserRepository()

    user = user_repo.read_user_by_id(db, valid_uuid)
    
    if user is None:
        raise InvalidCredentials

    return user

# --- AUTHORIZATION DEPENDENCIES ---

# - Admin Dependency

def require_admin(
        current_user : Users = Depends(get_current_user)
):
    if current_user.role.lower() != "admin":
        raise PermissionDenied

    return current_user