from mcp.db.models.user import UserRoleEnum

class RBACService:
    @staticmethod
    def has_role(user_role: str, required_role: str) -> bool:
        roles_hierarchy = [UserRoleEnum.ADMIN, UserRoleEnum.EDITOR, UserRoleEnum.VIEWER]
        try:
            user_index = roles_hierarchy.index(UserRoleEnum(user_role))
            required_index = roles_hierarchy.index(UserRoleEnum(required_role))
            return user_index <= required_index
        except ValueError:
            return False

rbac_service = RBACService() 