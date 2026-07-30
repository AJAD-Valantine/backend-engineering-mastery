from uuid import UUID

from app.exceptions.base_exception import ShopException
from app.exceptions.user_exceptions import EmailAlreadyExits, UserNotFound
from app.services.user_service import UserService
from fastapi import HTTPException, status


class UserController:
    
    def __init__(self) -> None:
        self.user_service = UserService()

    def create_user(self, db, request):

        try:
            return self.user_service.add_user(db, request)

        except EmailAlreadyExits as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_all_users(self, db):

        try:
            users = self.user_service.get_all_users(db)

            if not users:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no users available")
            
            return users

        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def get_user_by_id(self, db, user_id: UUID):

        try:
            return self.user_service.get_user_by_id(db, user_id)

        except UserNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def update_user(self, db, user_id, request):

        try:
            return self.user_service.update_user(db, user_id, request)

        except UserNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    def delete_user(self, db, user_id):

        try:
            return self.user_service.remove_user(db, user_id)
            
        except UserNotFound as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        
        except ShopException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))