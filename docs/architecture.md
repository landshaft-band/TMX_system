# Architecture

## Structure

```text
main.py
ui/
  main_window.py
  styles.py
  components.py
  pages/
services/
data/
models/
reports/
docs/
```

## Layers

```text
UI pages
↓
services
↓
mock data
↓
reports / integrations
```

## UI

`ui/main_window.py` создаёт `QMainWindow`, sidebar, top header и `QStackedWidget`. Страницы создаются один раз и переключаются по названию. Общие стили лежат в `ui/styles.py`, переиспользуемые виджеты — в `ui/components.py`.

## Services

Сервисы содержат бизнес-логику, интеграционные заглушки и расчёты. UI не должен напрямую реализовывать новую бизнес-логику, если её можно вынести в `services/`.

## Data Flow

1. Page получает ввод пользователя.
2. Page вызывает сервис.
3. Сервис читает/изменяет `data/mock_data.py`.
4. Page обновляет таблицу через `refill_table`/`append_table_row`.

## Event Flow

1. UI-действие вызывает сервис.
2. Сервис или page вызывает `event_log_service.add_event`.
3. Для пользовательских действий вызывается `audit_service.add_record`.
4. Dashboard и Integrations отображают журналы из `mock_data`.

## Page Dependencies

- `dashboard_page`: analytics, event log, PDF, mock data.
- `receiving_page`: barcode, scale, discrepancy, notification, event log, PDF.
- `shipping_page`: 1С, PDF, event log, auth, mock data.
- `orders_page`: auth, event log, mock data.
- `logistics_page`: auth, event log, mock data.
- `integrations_page`: 1С, audit, event log, mock data.
- `reports_page`: PDF, settings, mock data.

## PDF Dependencies

- `dashboard_page`
- `receiving_page`
- `shipping_page`
- `reports_page`

## 1C Dependencies

- `shipping_page`
- `integrations_page`
- `services/onec_service.py`
