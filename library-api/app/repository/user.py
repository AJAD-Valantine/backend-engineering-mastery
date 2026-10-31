from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def read_by_id(self, pk: UUID) -> User | None:
        return self.db.get(User, pk)

    def read_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.scalar(stmt)

    def set_new_password(self, user: User, new_password: str) -> None:
        user.hashed_password = new_password
        self.db.flush()

    def verify_user(self, user: User) -> None:
        user.is_verified = True
        self.db.flush()

    def change_role(self, user: User, role: UserRole) -> User:
        user.role = role  # pyright: ignore[reportAttributeAccessIssue]
        self.db.flush()
        self.db.refresh(user)
        return user

    def update(self, user: User, new_data: dict[str, Any]) -> User:
        for k, v in new_data.items():
            setattr(user, k, v)
        self.db.flush()
        self.db.refresh(user)
        return user

    def deactivate(self, user: User) -> User:
        user.active = False
        self.db.flush()
        self.db.refresh(user)
        return user

    def activate(self, user: User) -> User:
        user.active = True
        self.db.flush()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.flush()
