from app.core import security
from app.exceptions.base_exception import ShopException
from app.exceptions.user_exceptions import EmailAlreadyExits
from app.presentation.schemas.auth_schema import Token
from app.presentation.schemas.user_schema import UserCreateRequest
from app.services.auth_service import AuthService
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


class AuthController:

    def __init__(self):
        self.auth_service = AuthService()

    def register(self, db: Session, request: UserCreateRequest):
        
        try:
            return self.auth_service.register_new_user(db, request)

        except EmailAlreadyExits as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=str(e)
                )

        except ShopException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=str(e)
                )
        
    def login(self, db: Session, form_data: OAuth2PasswordRequestForm) -> Token:
        
        user = self.auth_service.authenticate_user(db, form_data.username, form_data.password)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = {"sub": str(user.user_id), "role": user.role}
        token = security.create_access_token(payload)

        return Token(access_token=token, token_type="bearer")