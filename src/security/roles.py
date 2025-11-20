"""
Role-Based Access Control (RBAC) Module

Defines user roles, permissions, and role-based access control utilities.
Supports hierarchical permissions and role inheritance.
"""

from enum import Enum
from typing import Set, List, Optional
from dataclasses import dataclass, field


class Permission(str, Enum):
    """
    System permissions that can be assigned to roles.

    Permissions follow a hierarchical structure:
    - READ: View data
    - WRITE: Create and update data
    - DELETE: Remove data
    - ADMIN: Full system administration
    - MONITOR: View monitoring and metrics
    - EXECUTE: Execute operations and workflows
    """

    # Basic data permissions
    READ = "read"
    WRITE = "write"
    DELETE = "delete"

    # System administration
    ADMIN = "admin"

    # Operational permissions
    MONITOR = "monitor"
    EXECUTE = "execute"

    # Advanced permissions
    CONFIGURE = "configure"
    AUDIT = "audit"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"


class Role(str, Enum):
    """
    User roles in the Aurora CloudBank system.

    Roles hierarchy (from least to most privileged):
    1. OBSERVER: Read-only access, monitoring
    2. RELAY_OPERATOR: Execute operations, read/write data
    3. ADMIN: Full system administration
    """

    OBSERVER = "observer"
    RELAY_OPERATOR = "relay_operator"
    ADMIN = "admin"


@dataclass
class RolePermissions:
    """
    Maps roles to their associated permissions.
    Supports permission inheritance and composition.
    """

    role: Role
    permissions: Set[Permission] = field(default_factory=set)
    description: str = ""

    def has_permission(self, permission: Permission) -> bool:
        """Check if this role has a specific permission."""
        return permission in self.permissions

    def add_permission(self, permission: Permission) -> None:
        """Add a permission to this role."""
        self.permissions.add(permission)

    def remove_permission(self, permission: Permission) -> None:
        """Remove a permission from this role."""
        self.permissions.discard(permission)


# Define default role permissions
ROLE_PERMISSIONS_MAP = {
    Role.OBSERVER: RolePermissions(
        role=Role.OBSERVER,
        permissions={
            Permission.READ,
            Permission.MONITOR,
        },
        description="Read-only access with monitoring capabilities. Can view data and system metrics.",
    ),
    Role.RELAY_OPERATOR: RolePermissions(
        role=Role.RELAY_OPERATOR,
        permissions={
            Permission.READ,
            Permission.WRITE,
            Permission.MONITOR,
            Permission.EXECUTE,
            Permission.AUDIT,
        },
        description="Operational access with read/write capabilities. Can execute workflows and operations.",
    ),
    Role.ADMIN: RolePermissions(
        role=Role.ADMIN,
        permissions={
            Permission.READ,
            Permission.WRITE,
            Permission.DELETE,
            Permission.ADMIN,
            Permission.MONITOR,
            Permission.EXECUTE,
            Permission.CONFIGURE,
            Permission.AUDIT,
            Permission.MANAGE_USERS,
            Permission.MANAGE_ROLES,
        },
        description="Full system administration with all permissions.",
    ),
}


def get_role_permissions(role: Role) -> RolePermissions:
    """
    Get the permissions associated with a role.

    Args:
        role: The role to look up

    Returns:
        RolePermissions object containing role permissions
    """
    return ROLE_PERMISSIONS_MAP.get(role, RolePermissions(role=role))


def check_permission(role: Role, permission: Permission) -> bool:
    """
    Check if a role has a specific permission.

    Args:
        role: The role to check
        permission: The permission to verify

    Returns:
        True if the role has the permission, False otherwise
    """
    role_perms = get_role_permissions(role)
    return role_perms.has_permission(permission)


def get_all_permissions(role: Role) -> Set[Permission]:
    """
    Get all permissions for a given role.

    Args:
        role: The role to get permissions for

    Returns:
        Set of permissions for the role
    """
    role_perms = get_role_permissions(role)
    return role_perms.permissions.copy()


def validate_role(role_str: str) -> Optional[Role]:
    """
    Validate and convert a string to a Role enum.

    Args:
        role_str: String representation of a role

    Returns:
        Role enum if valid, None otherwise
    """
    try:
        return Role(role_str.lower())
    except ValueError:
        return None


def get_roles_with_permission(permission: Permission) -> List[Role]:
    """
    Get all roles that have a specific permission.

    Args:
        permission: The permission to search for

    Returns:
        List of roles that have the permission
    """
    roles = []
    for role, role_perms in ROLE_PERMISSIONS_MAP.items():
        if role_perms.has_permission(permission):
            roles.append(role)
    return roles
