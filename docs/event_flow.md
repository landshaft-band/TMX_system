# Event Flow

## Event Service

Центральный сервис:

```text
services/event_log_service.py
```

Основной метод:

```python
add_event(event_type, message, user=None, entity_id=None)
```

## Event Fields

- `datetime`
- `time`
- `type`
- `user`
- `entity_id`
- `message`

## Event Types

- `SCAN`
- `WEIGHT_RECEIVED`
- `ACCEPTED`
- `DISCREPANCY`
- `NOTIFICATION`
- `ORDER_CREATED`
- `SHIPMENT_CREATED`
- `SHIPMENT_CLOSED`
- `EXPORT_1C`
- `PDF_GENERATED`
- `ERROR`
- `ROLE_CHANGED`
- `INTEGRATION_CHECK`
- `SETTINGS_CHANGED`

## Where Events Are Created

- `receiving_page` — сканирование, вес, приёмка, расхождения.
- `orders_page` — создание и изменение статуса заказа.
- `shipping_page` — партии, статусы, PDF, 1С.
- `logistics_page` — расчёт транспорта.
- `reports_page` / `pdf_report_service` — PDF.
- `integrations_page` — проверки 1С, очередь обмена, настройки допусков.
- `main_window` — смена роли.

## Audit Log

Аудит действий пользователей находится в:

```text
services/audit_service.py
```

Формат:

- Время
- Пользователь
- Роль
- Действие
- Объект
- Результат

Аудит отображается на странице `Интеграции`.
