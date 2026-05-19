from datetime import datetime

from data import mock_data


class AuditService:
    def add_record(
        self,
        action: str,
        object_id: str = "-",
        result: str = "Успешно",
        user: str | None = None,
        role: str | None = None,
    ) -> None:
        mock_data.USER_AUDIT_LOG.insert(
            0,
            [
                datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                user or mock_data.CURRENT_USER,
                role or mock_data.CURRENT_ROLE,
                action,
                object_id,
                result,
            ],
        )

    def get_records(self) -> list[list[str]]:
        return mock_data.USER_AUDIT_LOG


audit_service = AuditService()
