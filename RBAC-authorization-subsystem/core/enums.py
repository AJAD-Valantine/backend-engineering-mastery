from enum import StrEnum


class UserRole(StrEnum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class Permission(StrEnum):
    REGISTER_USER = "register:users"
    LOGIN_USER = "login:users"
    LOGOUT_USER = "logout:users"

    CREATE_USER = "create:users"
    READ_USER = "read:users"
    UPDATE_USER = "update:users"
    DELETE_USER = "delete:users"

    CREATE_BOOK = "create:books"
    READ_BOOK = "read:books"
    UPDATE_BOOK = "update:books"
    DELETE_BOOK = "delete:books"
