from PyQt6.QtWidgets import QComboBox, QFormLayout, QGridLayout, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QWidget

from data import mock_data
from services.audit_service import audit_service
from services.event_log_service import event_log_service
from services.onec_service import OneCIntegrationService
from ui.components import group_box, info_card, make_table, page_shell, refill_table, title_label


class IntegrationsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.onec_service = OneCIntegrationService()
        page, layout = page_shell()
        root = QGridLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(page)

        layout.addWidget(title_label("Интеграции и справочники"))

        status_box, status_layout = group_box("Состояние интеграций")
        self.status_host = QWidget()
        self.status_layout = QGridLayout(self.status_host)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.addWidget(self.status_host)

        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        check_button = QPushButton("Проверить подключение 1С")
        retry_button = QPushButton("Повторить обмен")
        check_button.clicked.connect(self._check_onec)
        retry_button.clicked.connect(self._retry_exchange)
        actions_layout.addWidget(check_button)
        actions_layout.addWidget(retry_button)
        actions_layout.addStretch(1)
        status_layout.addWidget(actions)
        layout.addWidget(status_box)

        queue_box, queue_layout = group_box("Очередь обмена с 1С")
        queue_layout.addWidget(self._filters_row("Поиск", "Статус", self._apply_queue_filters, ["Все", "Ожидает выгрузки", "Выгружено", "Ошибка", "Повторная попытка"], "queue"))
        self.exchange_table = make_table(
            ["ID документа", "Тип документа", "Статус", "Попыток", "Последняя ошибка", "Дата последней попытки"],
            mock_data.ONEC_EXCHANGE_QUEUE,
            min_height=220,
        )
        queue_layout.addWidget(self.exchange_table)
        layout.addWidget(queue_box)

        audit_box, audit_layout = group_box("Журнал аудита пользователей")
        audit_layout.addWidget(self._filters_row("Поиск", "Роль", self._apply_audit_filters, ["Все", "Администратор", "Менеджер", "Кладовщик", "Приёмщик", "Логист", "Руководитель"], "audit"))
        self.audit_table = make_table(["Время", "Пользователь", "Роль", "Действие", "Объект", "Результат"], mock_data.USER_AUDIT_LOG, min_height=220)
        audit_layout.addWidget(self.audit_table)
        layout.addWidget(audit_box)

        passport_box, passport_layout = group_box("Цифровой паспорт партии")
        self.batch_combo = QComboBox()
        self.batch_combo.addItems(mock_data.SHIPMENT_ITEMS.keys())
        self.batch_combo.currentTextChanged.connect(self._refresh_batch_passport)
        passport_layout.addWidget(self.batch_combo)
        self.passport_host = QWidget()
        self.passport_layout = QGridLayout(self.passport_host)
        self.passport_layout.setContentsMargins(0, 0, 0, 0)
        passport_layout.addWidget(self.passport_host)
        self.passport_history_table = make_table(["Время", "Операция", "Пользователь", "Комментарий"], [], min_height=160)
        passport_layout.addWidget(self.passport_history_table)
        layout.addWidget(passport_box)

        nomenclature_box, nomenclature_layout = group_box("Справочник номенклатуры")
        nomenclature_layout.addWidget(self._filters_row("Поиск", "Категория", self._apply_nomenclature_filters, ["Все", "Окна и двери", "Металлопрокат", "Крепёж", "Уплотнители"], "nomenclature"))
        self.nomenclature_table = make_table(
            ["Артикул", "Наименование", "Категория", "Единица учёта", "Нормативный вес", "Зона хранения", "Допуск веса, %"],
            mock_data.NOMENCLATURE,
            min_height=260,
        )
        nomenclature_layout.addWidget(self.nomenclature_table)
        layout.addWidget(nomenclature_box)

        tolerance_box, tolerance_layout = group_box("Настраиваемые допуски")
        self.tolerance_table = make_table(
            ["Категория товара", "Допустимое отклонение веса, %", "Требуется ручная проверка", "Ответственный"],
            mock_data.WEIGHT_TOLERANCES,
            min_height=170,
        )
        tolerance_layout.addWidget(self.tolerance_table)
        save_tolerance_button = QPushButton("Сохранить настройки допусков")
        save_tolerance_button.clicked.connect(self._save_tolerances)
        tolerance_layout.addWidget(save_tolerance_button)
        layout.addWidget(tolerance_box)
        layout.addStretch(1)

        self.refresh()

    def _filters_row(self, search_label: str, combo_label: str, handler, combo_values: list[str], prefix: str) -> QWidget:
        row = QWidget()
        form = QFormLayout(row)
        form.setContentsMargins(0, 0, 0, 0)
        search = QLineEdit()
        combo = QComboBox()
        combo.addItems(combo_values)
        search.textChanged.connect(handler)
        combo.currentTextChanged.connect(handler)
        setattr(self, f"{prefix}_search", search)
        setattr(self, f"{prefix}_combo", combo)
        form.addRow(search_label, search)
        form.addRow(combo_label, combo)
        return row

    def refresh(self) -> None:
        self._refresh_status_card()
        self._refresh_batch_passport()
        refill_table(self.exchange_table, mock_data.ONEC_EXCHANGE_QUEUE)
        refill_table(self.audit_table, mock_data.USER_AUDIT_LOG)
        refill_table(self.nomenclature_table, mock_data.NOMENCLATURE)
        refill_table(self.tolerance_table, mock_data.WEIGHT_TOLERANCES)

    def _refresh_status_card(self) -> None:
        while self.status_layout.count():
            item = self.status_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        sync = self.onec_service.get_last_sync_status()
        card = info_card(
            {
                "Статус подключения к 1С": str(sync["connection"]),
                "Последняя синхронизация": str(sync["last_sync"]),
                "Очередь документов": str(len([row for row in mock_data.ONEC_EXCHANGE_QUEUE if row[2] != "Выгружено"])),
                "Ошибки синхронизации": str(len([row for row in mock_data.ONEC_EXCHANGE_QUEUE if row[2] == "Ошибка"])),
                "Настройки весов": "COM3, 9600 бод, контроль стабильности веса",
                "Настройки сканера": "USB HID, завершение ввода Enter",
            }
        )
        self.status_layout.addWidget(card, 0, 0)

    def _refresh_batch_passport(self) -> None:
        if not hasattr(self, "passport_layout"):
            return
        batch_id = self.batch_combo.currentText()
        while self.passport_layout.count():
            item = self.passport_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        items = mock_data.SHIPMENT_ITEMS.get(batch_id, [])
        related_reports = ", ".join(row[0] for row in mock_data.REPORTS if batch_id in row[-1]) or "Нет связанных PDF"
        passport = {
            "ID партии": batch_id,
            "Поставщик": "АО «Трансмашхолдинг»",
            "Состав": f"{len(items)} позиций",
            "Общий вес": "8 600 кг",
            "Количество упаковок": str(len(items)),
            "Количество сканов": "12",
            "Количество расхождений": str(len(mock_data.PROBLEM_POSITIONS)),
            "Статус отгрузки": mock_data.SHIPMENT_STATUSES.get(batch_id, "-"),
            "Статус 1С": mock_data.ONEC_SYNC_STATUS.get(batch_id, "-"),
            "Связанные PDF-документы": related_reports,
        }
        self.passport_layout.addWidget(info_card(passport), 0, 0)
        refill_table(self.passport_history_table, mock_data.SHIPMENT_HISTORY.get(batch_id, []))

    def _apply_queue_filters(self) -> None:
        text = self.queue_search.text().lower()
        status = self.queue_combo.currentText()
        rows = [
            row for row in mock_data.ONEC_EXCHANGE_QUEUE
            if (not text or text in " ".join(row).lower()) and (status == "Все" or row[2] == status)
        ]
        refill_table(self.exchange_table, rows)

    def _apply_audit_filters(self) -> None:
        text = self.audit_search.text().lower()
        role = self.audit_combo.currentText()
        rows = [
            row for row in mock_data.USER_AUDIT_LOG
            if (not text or text in " ".join(row).lower()) and (role == "Все" or row[2] == role)
        ]
        refill_table(self.audit_table, rows)

    def _apply_nomenclature_filters(self) -> None:
        text = self.nomenclature_search.text().lower()
        category = self.nomenclature_combo.currentText()
        rows = [
            row for row in mock_data.NOMENCLATURE
            if (not text or text in " ".join(row).lower()) and (category == "Все" or row[2] == category)
        ]
        refill_table(self.nomenclature_table, rows)

    def _check_onec(self) -> None:
        ok = self.onec_service.check_connection()
        result = "Подключение активно" if ok else "Ошибка подключения"
        event_log_service.add_event("INTEGRATION_CHECK", f"Проверка подключения к 1С: {result}")
        audit_service.add_record("Проверка подключения к 1С", "1C", result)
        QMessageBox.information(self, "1С", result)
        self.refresh()

    def _retry_exchange(self) -> None:
        for row in mock_data.ONEC_EXCHANGE_QUEUE:
            if row[2] in ("Ошибка", "Повторная попытка"):
                row[2] = "Повторная попытка"
                row[3] = str(int(row[3]) + 1)
                row[4] = "Ожидает повторной отправки"
                break
        event_log_service.add_event("EXPORT_1C", "Документ поставлен в очередь повторного обмена с 1С")
        audit_service.add_record("Повтор обмена с 1С", "Очередь обмена", "Повторная попытка")
        QMessageBox.information(self, "1С", "Документ поставлен в очередь повторного обмена.")
        self.refresh()

    def _save_tolerances(self) -> None:
        event_log_service.add_event("SETTINGS_CHANGED", "Настройки допусков веса сохранены")
        audit_service.add_record("Сохранение допусков веса", "Справочник допусков", "Успешно")
        QMessageBox.information(self, "Допуски", "Настройки допусков сохранены.")
        self.refresh()
