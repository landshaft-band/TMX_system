from data import mock_data


class AnalyticsService:
    def calculate_discrepancy_rate(self) -> float:
        total = len(mock_data.ACCEPTED_PACKAGES) + len(mock_data.PROBLEM_POSITIONS)
        if total == 0:
            return 0.0
        return round(len(mock_data.PROBLEM_POSITIONS) / total * 100, 1)

    def calculate_today_accepted_count(self) -> int:
        return len(mock_data.ACCEPTED_PACKAGES)

    def calculate_closed_shipments(self) -> int:
        return sum(1 for status in mock_data.SHIPMENT_STATUSES.values() if status in ("Закрыта", "Выгружена в 1С"))

    def calculate_1c_sync_errors(self) -> int:
        return sum(1 for status in mock_data.ONEC_SYNC_STATUS.values() if status == "Ошибка синхронизации")

    def calculate_warehouse_load(self) -> int:
        loads = [zone["load"] for zone in mock_data.WAREHOUSE_ZONES]
        return round(sum(loads) / len(loads))


analytics_service = AnalyticsService()
