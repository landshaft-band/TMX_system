from datetime import datetime
import random

from data import mock_data
from services.event_log_service import event_log_service


class OneCIntegrationService:
    def export_closed_shipment(self, shipment: dict[str, str]) -> bool:
        # TODO: здесь будет HTTP/API/COM-обмен с 1С.
        # TODO: здесь будет маппинг внутренних данных WMS/MES в формат документов 1С.
        # TODO: здесь будет обработка сетевых, бизнес- и валидационных ошибок интеграции.
        shipment_id = shipment["id"]
        if shipment["status"] != "Закрыта":
            mock_data.ONEC_SYNC_STATUS[shipment_id] = "Не выгружено"
            return False

        if random.random() < 0.15:
            mock_data.ONEC_SYNC_STATUS[shipment_id] = "Ошибка синхронизации"
            mock_data.ONEC_LAST_SYNC = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            event_log_service.add_event("ERROR", f"Ошибка выгрузки отгрузки {shipment_id} в 1С", entity_id=shipment_id)
            return False

        mock_data.ONEC_SYNC_STATUS[shipment_id] = "Выгружено в 1С"
        mock_data.SHIPMENT_STATUSES[shipment_id] = "Выгружена в 1С"
        mock_data.ONEC_LAST_SYNC = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        event_log_service.add_event("EXPORT_1C", f"Отгрузка {shipment_id} выгружена в 1С", entity_id=shipment_id)
        mock_data.SHIPMENT_HISTORY[shipment_id].insert(0, [datetime.now().strftime("%H:%M"), "Выгружено в 1С", mock_data.CURRENT_USER, "Экспорт выполнен"])
        return True

    def export_order(self, order: list[str]) -> bool:
        # TODO: здесь будет маппинг заказа в документ/справочник 1С.
        event_log_service.add_event("EXPORT_1C", f"Заказ {order[0]} подготовлен к выгрузке в 1С", entity_id=order[0])
        return True

    def check_connection(self) -> bool:
        return mock_data.ONEC_CONNECTION_OK

    def get_last_sync_status(self) -> dict[str, str | int]:
        closed = sum(1 for status in mock_data.SHIPMENT_STATUSES.values() if status == "Закрыта")
        errors = sum(1 for status in mock_data.ONEC_SYNC_STATUS.values() if status == "Ошибка синхронизации")
        return {
            "connection": "Подключение активно" if mock_data.ONEC_CONNECTION_OK else "Нет подключения",
            "last_sync": mock_data.ONEC_LAST_SYNC,
            "closed_shipments": closed,
            "sync_errors": errors,
        }

    def simulate_sync_error(self) -> None:
        mock_data.ONEC_CONNECTION_OK = False
        event_log_service.add_event("ERROR", "Смоделирована ошибка подключения к 1С")
