from enum import StrEnum


class UserRole(StrEnum):
    MOD = "moderator"
    MEMBER = "member"
    LIBRARIAN = "super_admin"
    ADMIN = "admin"
