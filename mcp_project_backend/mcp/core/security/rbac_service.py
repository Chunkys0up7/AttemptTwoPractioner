from enum import Enum
from typing import List, Dict, Any
# from mcp.db.models.user import User

class Permission(str, Enum):
    """
    Enum of all possible permissions in the MCP system.
    """
    CREATE_MCP = "create_mcp"
    READ_MCP = "read_mcp"
    UPDATE_MCP = "update_mcp"
    DELETE_MCP = "delete_mcp"
    EXECUTE_WORKFLOW = "execute_workflow"
    # ... add more permissions as needed

# Define roles and their associated permissions
ROLE_PERMISSIONS: Dict[str, List[Permission]] = {
    "Admin": list(Permission),  # Admin has all permissions
    "Editor": [
        Permission.CREATE_MCP, Permission.READ_MCP, Permission.UPDATE_MCP,
        Permission.EXECUTE_WORKFLOW
    ],
    "Viewer": [Permission.READ_MCP],
}

class RBACService:
    """
    Service for Role-Based Access Control (RBAC).

    Responsibilities:
    - Define roles and their permissions.
    - Check if a user has permission to perform an action.
    - (Future) Support for more granular or resource-based permissions.
    """
    @staticmethod
    def has_permission(user: Any, permission: Permission) -> bool:
        """
        Check if the user has the specified permission.
        Args:
            user: User object (should have a 'role' attribute or property).
            permission: Permission enum value to check.
        Returns:
            True if the user has the permission, False otherwise.
        """
        if not user or not hasattr(user, 'role') or not user.role:
            return False
        # Adjust if user.role is not just a string
        role_name = user.role.name if hasattr(user.role, 'name') else user.role
        user_permissions = ROLE_PERMISSIONS.get(role_name, [])
        return permission in user_permissions

    # More advanced RBAC might involve checking ownership of resources,
    # or more granular permissions associated directly with users or groups.
    # Example:
    # @staticmethod
    # def check_permission_or_raise(user: Any, permission: Permission):
    #     if not RBACService.has_permission(user, permission):
    #         raise HTTPException(status_code=403, detail="Not enough permissions")
