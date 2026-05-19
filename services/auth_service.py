from data import mock_data


ROLE_PERMISSIONS = {
    "Приёмщик": {"dashboard:view", "receiving:view", "receiving:accept", "reports:discrepancy", "reports:batch"},
    "Менеджер": {"dashboard:view", "orders:view", "orders:create", "shipping:view", "shipping:form", "shipping:close", "reports:view"},
    "Логист": {"dashboard:view", "shipping:view", "logistics:view", "logistics:calculate", "reports:view"},
    "Руководитель": {"dashboard:view", "receiving:view", "shipping:view", "orders:view", "logistics:view", "reports:view", "users:view"},
    "Администратор": {"*"},
}


class AuthService:
    def set_role(self, role: str) -> None:
        mock_data.CURRENT_ROLE = role

    def current_role(self) -> str:
        return mock_data.CURRENT_ROLE

    def has_permission(self, permission: str) -> bool:
        role_permissions = ROLE_PERMISSIONS.get(mock_data.CURRENT_ROLE, set())
        return "*" in role_permissions or permission in role_permissions


auth_service = AuthService()
