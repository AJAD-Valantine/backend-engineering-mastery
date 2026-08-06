from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core import security
from app.core.database import SessionLocal
from app.repository.user_repository import UserRepository
from app.schemas.auth_schema import TokenData

# --- DATABASE DEPENDENCY ---

def db_connection():
    """Yields a database session and closes it after the request finishes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- AUTHENTICATION DEPENDENCY ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(db_connection)): 
    """The Bouncer: Intercepts the token, decodes it, and returns the database User."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id_str = security.verify_access_token(token)

    if user_id_str is None:
        raise credentials_exception

    try:
        valid_uuid = UUID(user_id_str)
    except ValueError:
        raise credentials_exception
        
    token_data = TokenData(id=valid_uuid)

    if token_data.id is None:
        raise credentials_exception

    user_repo = UserRepository()

    user = user_repo.read_user_by_id(db, token_data.id)
    
    if user is None:
        raise credentials_exception

    return user