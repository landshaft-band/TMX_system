from datetime import datetime

from data import mock_data


class EventLogService:
    def add_event(self, event_type: str, message: str, user: str | None = None, entity_id: str | None = None) -> None:
        event = {
            "datetime": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "time": datetime.now().strftime("%H:%M"),
            "type": event_type,
            "user": user or mock_data.CURRENT_USER,
            "entity_id": entity_id or "-",
            "message": message,
        }
        mock_data.STRUCTURED_EVENTS.insert(0, event)
        mock_data.EVENT_LOG.insert(0, [event["datetime"], event_type, event["user"], event["entity_id"], message])

    def get_events(self) -> list[dict[str, str]]:
        return mock_data.STRUCTURED_EVENTS

    def get_recent_events(self, limit: int = 20) -> list[list[str]]:
        return mock_data.EVENT_LOG[:limit]

    def clear_events(self) -> None:
        mock_data.STRUCTURED_EVENTS.clear()
        mock_data.EVENT_LOG.clear()


event_log_service = EventLogService()
