from core.enums import Permission, UserRole

ROLE_PERMISSIONS: dict[UserRole, set[Permission]] = {
    UserRole.USER: {
        Permission.REGISTER_USER,
        Permission.LOGIN_USER,
        Permission.LOGOUT_USER,
        Permission.UPDATE_USER,
        Permission.READ_BOOK,
    },
    UserRole.MODERATOR: {
        Permission.CREATE_BOOK,
        Permission.UPDATE_BOOK,
        Permission.DELETE_BOOK,
    },
    UserRole.ADMIN: {
        Permission.CREATE_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
    },
}

ROLE_HIERARCHY: dict[UserRole, set[UserRole]] = {
    UserRole.ADMIN: {UserRole.MODERATOR},
    UserRole.MODERATOR: {UserRole.USER},
    UserRole.USER: set(),
}

def get_inherited_roles(role: UserRole) -> set[UserRole]:
    inherited = set()
    queue = list(ROLE_HIERARCHY.get(role, set()))
    while queue:
        current = queue.pop()
        if current not in inherited:
            inherited.add(current)
            queue.extend(ROLE_HIERARCHY.get(current, set()))
    return inherited


def get_effective_permissions(role: UserRole) -> set[Permission]:
    permissions = set(ROLE_PERMISSIONS.get(role, set()))
    for r in get_inherited_roles(role):
        permissions |= ROLE_PERMISSIONS.get(r, set())
    return permissions


def has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in get_effective_permissions(role)
