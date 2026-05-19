# Wagon WMS/MES

Desktop WMS/MES-система на Python + PyQt6 для склада комплектующих производства железнодорожных вагонов. Проект демонстрационный: backend, 1С, весы и сканер подготовлены архитектурно, но работают на данных из `data/mock_data.py`.

## Tech Stack

- Python 3.10+
- PyQt6
- ReportLab
- PyInstaller

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Build EXE

```powershell
.\build_exe.ps1
```

Result:

```text
dist\WagonWMS.exe
```

## Project Structure

```text
main.py
ui/                 # main window, styles, components, pages
services/           # business logic and integrations
data/               # demonstration data
models/             # enums / model placeholders
reports/            # generated PDF reports
docs/               # engineering docs
```

## Main Features

- Приёмка комплектующих.
- Сканирование штрих-кода.
- Симуляция умных весов.
- Контроль расхождений веса.
- Заказы и жизненный цикл заказа.
- Отгрузки и жизненный цикл партии.
- Интеграция с 1С в демонстрационном режиме.
- Очередь обмена с 1С.
- PDF-отчёты.
- Журнал событий.
- Журнал аудита пользователей.
- Цифровой паспорт партии.
- Справочник номенклатуры.
- Роли и скрытие вкладок по роли.

## Roles

- `Администратор` — полный доступ.
- `Менеджер` — заказы, отгрузка, интеграции, отчёты.
- `Кладовщик` / `Приёмщик` — главная и приёмка.
- `Логист` — логистика, отгрузка, интеграции.
- `Руководитель` — обзор, заказы, отгрузка, логистика, интеграции, пользователи, отчёты.

## PDF Reports

PDF генерируются через `services/pdf_report_service.py`. Папка отчётов выбирается на странице `Отчёты` и хранится в `%APPDATA%\WagonWMS\settings.json`.

## 1C Integration

Демонстрационная интеграция находится в `services/onec_service.py`. Страница `Интеграции` показывает подключение, очередь обмена, ошибки и действия повторной отправки.

## Event Log

Все значимые действия должны писать событие через `services/event_log_service.py`. Пользовательские действия дополнительно пишутся через `services/audit_service.py`.

## Mock Functionality

Сейчас демонстрационными являются:

- backend/data storage;
- 1С;
- весы;
- сканер;
- уведомления;
- аналитика;
- роли без реальной авторизации.

## Roadmap

См. `TODO.md`.

## Documentation

- `PROJECT_CONTEXT.md` — короткий контекст для новых сессий.
- `PROJECT_OVERVIEW.md` — подробное описание реализованного MVP.
- `docs/architecture.md` — архитектура и зависимости.
- `docs/roles.md` — роли и права.
- `docs/event_flow.md` — события и аудит.
- `docs/integration.md` — интеграции и точки подключения.

## Как работать с проектом

1. Сначала читать `PROJECT_CONTEXT.md`.
2. Перед изменениями анализировать существующую структуру.
3. Не переписывать существующие страницы.
4. Не создавать дубликаты сервисов.
5. Сначала искать существующий компонент в `ui/components.py`.
6. Все изменения делать минимально.
7. Новую бизнес-логику выносить в `services/`.
8. Проверять проект командой:

```powershell
.\.venv\Scripts\python.exe -m compileall main.py ui data services models
```
