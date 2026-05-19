from datetime import datetime

from data import mock_data
from services.event_log_service import event_log_service


def _time_label() -> str:
    return datetime.now().strftime("%H:%M")


def add_event(message: str) -> None:
    event_log_service.add_event("NOTIFICATION", message)


def create_manager_notification(barcode: str, product: str, deviation: float) -> None:
    mock_data.MANAGER_NOTIFICATIONS.insert(
        0,
        [_time_label(), "Расхождение веса", f"{barcode}: {product}, отклонение {deviation:.2f}%"],
    )
    event_log_service.add_event("NOTIFICATION", f"Создано уведомление руководителю по {barcode}", entity_id=barcode)
