from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import Users


class UserRepository:

    def __init__(
            self,
            db : Session
    ) -> None:

        self.db = db
    
    def create_user(
            self,
            user: Users
    ) -> Users:

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def read_all_users(
            self,
            skip: int = 0,
            limit: int = 10
    )-> tuple[int, list[Users]]:

        total_items = self.db.query(func.count(Users.user_id)).scalar()
        users = self.db.query(Users).offset(skip).limit(limit).all()
        
        return total_items, users

    def read_user_by_id(
            self,
            user_id: UUID
    ) -> Users | None:

        return self.db.query(Users).filter(Users.user_id == user_id).first()

    def read_user_by_email(
            self,
            email: str
    ) -> Users | None:

        return self.db.query(Users).filter(Users.email == email).first()

    def update_user(
            self,
            user: Users,
            update_data : dict
    ) -> Users:

        for key, value in update_data.items():
            setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)

        return user

    def delete_user(
            self,
            user_id : UUID
    ) -> None:

        user = (self.db.query(Users).filter(Users.user_id == user_id).first())

        if user is not None:
            self.db.delete(user)
            self.db.commit()