"""
Tests for RBAC (Role-Based Access Control) functionality.

Tests role definitions, permissions, and access control logic.
"""

import pytest
from src.security.roles import (
    Role,
    Permission,
    RolePermissions,
    get_role_permissions,
    check_permission,
    get_all_permissions,
    validate_role,
    get_roles_with_permission,
    ROLE_PERMISSIONS_MAP
)


class TestRoleDefinitions:
    """Test role enumeration and basic role properties."""
    
    def test_role_enum_values(self):
        """Test that all expected roles are defined."""
        assert Role.OBSERVER.value == "observer"
        assert Role.RELAY_OPERATOR.value == "relay_operator"
        assert Role.ADMIN.value == "admin"
    
    def test_permission_enum_values(self):
        """Test that all expected permissions are defined."""
        assert Permission.READ.value == "read"
        assert Permission.WRITE.value == "write"
        assert Permission.DELETE.value == "delete"
        assert Permission.ADMIN.value == "admin"
        assert Permission.MONITOR.value == "monitor"
        assert Permission.EXECUTE.value == "execute"


class TestRolePermissions:
    """Test role permission mappings and checks."""
    
    def test_observer_permissions(self):
        """Test observer role has correct permissions."""
        observer_perms = get_role_permissions(Role.OBSERVER)
        
        assert observer_perms.has_permission(Permission.READ)
        assert observer_perms.has_permission(Permission.MONITOR)
        assert not observer_perms.has_permission(Permission.WRITE)
        assert not observer_perms.has_permission(Permission.DELETE)
        assert not observer_perms.has_permission(Permission.ADMIN)
    
    def test_relay_operator_permissions(self):
        """Test relay_operator role has correct permissions."""
        operator_perms = get_role_permissions(Role.RELAY_OPERATOR)
        
        assert operator_perms.has_permission(Permission.READ)
        assert operator_perms.has_permission(Permission.WRITE)
        assert operator_perms.has_permission(Permission.MONITOR)
        assert operator_perms.has_permission(Permission.EXECUTE)
        assert operator_perms.has_permission(Permission.AUDIT)
        assert not operator_perms.has_permission(Permission.DELETE)
        assert not operator_perms.has_permission(Permission.ADMIN)
    
    def test_admin_permissions(self):
        """Test admin role has all permissions."""
        admin_perms = get_role_permissions(Role.ADMIN)
        
        # Admin should have all permissions
        for permission in Permission:
            assert admin_perms.has_permission(permission)
    
    def test_check_permission_function(self):
        """Test the check_permission utility function."""
        assert check_permission(Role.OBSERVER, Permission.READ)
        assert not check_permission(Role.OBSERVER, Permission.WRITE)
        assert check_permission(Role.ADMIN, Permission.DELETE)
        assert check_permission(Role.RELAY_OPERATOR, Permission.EXECUTE)
    
    def test_get_all_permissions(self):
        """Test getting all permissions for a role."""
        observer_perms = get_all_permissions(Role.OBSERVER)
        assert Permission.READ in observer_perms
        assert Permission.MONITOR in observer_perms
        assert Permission.WRITE not in observer_perms
        
        admin_perms = get_all_permissions(Role.ADMIN)
        assert len(admin_perms) >= 10  # Admin has many permissions


class TestRoleValidation:
    """Test role validation and conversion."""
    
    def test_validate_role_valid_strings(self):
        """Test validation of valid role strings."""
        assert validate_role("observer") == Role.OBSERVER
        assert validate_role("relay_operator") == Role.RELAY_OPERATOR
        assert validate_role("admin") == Role.ADMIN
        assert validate_role("ADMIN") == Role.ADMIN  # Case insensitive
    
    def test_validate_role_invalid_strings(self):
        """Test validation of invalid role strings."""
        assert validate_role("invalid_role") is None
        assert validate_role("") is None
        assert validate_role("super_admin") is None


class TestPermissionQueries:
    """Test queries for roles with specific permissions."""
    
    def test_get_roles_with_permission_read(self):
        """Test getting roles with READ permission."""
        roles = get_roles_with_permission(Permission.READ)
        
        assert Role.OBSERVER in roles
        assert Role.RELAY_OPERATOR in roles
        assert Role.ADMIN in roles
    
    def test_get_roles_with_permission_write(self):
        """Test getting roles with WRITE permission."""
        roles = get_roles_with_permission(Permission.WRITE)
        
        assert Role.OBSERVER not in roles
        assert Role.RELAY_OPERATOR in roles
        assert Role.ADMIN in roles
    
    def test_get_roles_with_permission_admin(self):
        """Test getting roles with ADMIN permission."""
        roles = get_roles_with_permission(Permission.ADMIN)
        
        assert Role.OBSERVER not in roles
        assert Role.RELAY_OPERATOR not in roles
        assert Role.ADMIN in roles


class TestRolePermissionsObject:
    """Test the RolePermissions dataclass."""
    
    def test_create_role_permissions(self):
        """Test creating a RolePermissions object."""
        role_perms = RolePermissions(
            role=Role.OBSERVER,
            permissions={Permission.READ, Permission.MONITOR}
        )
        
        assert role_perms.role == Role.OBSERVER
        assert len(role_perms.permissions) == 2
    
    def test_add_permission(self):
        """Test adding a permission to a role."""
        role_perms = RolePermissions(role=Role.OBSERVER)
        role_perms.add_permission(Permission.READ)
        
        assert role_perms.has_permission(Permission.READ)
    
    def test_remove_permission(self):
        """Test removing a permission from a role."""
        role_perms = RolePermissions(
            role=Role.OBSERVER,
            permissions={Permission.READ, Permission.MONITOR}
        )
        role_perms.remove_permission(Permission.READ)
        
        assert not role_perms.has_permission(Permission.READ)
        assert role_perms.has_permission(Permission.MONITOR)
    
    def test_role_permissions_map_integrity(self):
        """Test that ROLE_PERMISSIONS_MAP is properly configured."""
        assert len(ROLE_PERMISSIONS_MAP) >= 3
        
        for role, role_perms in ROLE_PERMISSIONS_MAP.items():
            assert isinstance(role, Role)
            assert isinstance(role_perms, RolePermissions)
            assert role_perms.role == role
            assert len(role_perms.description) > 0
