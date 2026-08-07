from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user_model import Users
from app.schemas.user_schema import UserUpdateRequest


class UserRepository:
    
    def create_user(self, db: Session, user: Users):

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def read_all_users(self, db: Session, skip: int = 0, limit: int = 10):

        total_items = db.query(func.count(Users.user_id)).scalar()
        
        users = db.query(Users).offset(skip).limit(limit).all()
        
        return total_items, users

    def read_user_by_id(self, db: Session, user_id: UUID):

        return db.query(Users).filter(Users.user_id == user_id).first()

    def read_user_by_email(self, db: Session, email: str):

        return db.query(Users).filter(Users.email == email).first()

    def update_user(
        self, db: Session, user_id: UUID, request: UserUpdateRequest
    ):

        user = (
            db.query(Users).filter(Users.user_id == user_id).first()
        )

        update_data = request.model_dump(exclude_unset=True)

        if user is not None:
            for key, value in update_data.items():
                setattr(user, key, value)

            db.commit()
            db.refresh(user)
            return user

    def delete_user(self, db: Session, user_id):

        user = (
            db.query(Users).filter(Users.user_id == user_id).first()
        )

        db.delete(user)
        db.commit()

        return user
