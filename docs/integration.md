# Integration

## 1C

Сервис:

```text
services/onec_service.py
```

Реализовано:

- проверка подключения;
- статус последней синхронизации;
- выгрузка закрытой отгрузки;
- имитация ошибки синхронизации;
- очередь обмена на странице `Интеграции`.

Точки реального подключения:

- HTTP-сервис 1С;
- COMConnector;
- файловый обмен XML/JSON;
- обработка ошибок и retry policy.

TODO находится в `OneCIntegrationService`.

## Scales

Сервис:

```text
services/scale_service.py
```

Сейчас вес симулируется рядом с плановым значением. Реальное подключение можно делать через COM, TCP/IP или SDK производителя.

## Barcode Scanner

Сервис:

```text
services/barcode_service.py
```

UI-точка:

```text
ui/pages/receiving_page.py
```

USB-сканер обычно работает как клавиатура, поэтому текущий `QLineEdit` подходит для первого реального подключения.

## Backend/API

Сейчас backend заменён `data/mock_data.py`. Для реального backend:

1. Создать API-клиент в `services/`.
2. Заменить чтение `mock_data` на репозиторий/API.
3. Сохранить UI-слой максимально тонким.
4. События и аудит хранить в БД.
