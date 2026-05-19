from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QGridLayout, QHBoxLayout, QMessageBox, QProgressBar, QPushButton, QVBoxLayout, QWidget

from data import mock_data
from data.mock_data import SHIPMENT_BATCHES, SHIPMENT_INFO, SHIPMENT_ITEMS, SHIPPING_ORDERS
from services.auth_service import auth_service
from services.event_log_service import event_log_service
from services.onec_service import OneCIntegrationService
from services.pdf_report_service import PDFReportService
from ui.components import group_box, info_card, make_table, order_card, page_shell, refill_table, title_label


class ShippingPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.onec_service = OneCIntegrationService()
        self.pdf_service = PDFReportService()
        page, layout = page_shell()
        root = QGridLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(page)

        layout.addWidget(title_label("Отгрузка товаров"))

        batches_box, batches_layout = group_box("Партии для отгрузки")
        self.batches_table = make_table(
            ["Партия", "Маршрут", "Заказов", "Готовность", "Статус", "Статус 1С"],
            SHIPMENT_BATCHES,
            min_height=210,
        )
        batches_layout.addWidget(self.batches_table)
        layout.addWidget(batches_box)

        details_box, details_layout = group_box("Детали отправки")
        self.batch_combo = QComboBox()
        self.batch_combo.addItems(SHIPMENT_INFO.keys())
        self.batch_combo.currentTextChanged.connect(self._update_shipment)
        details_layout.addWidget(self.batch_combo)

        details_grid = QWidget()
        details_grid_layout = QGridLayout(details_grid)
        details_grid_layout.setContentsMargins(0, 0, 0, 0)
        details_grid_layout.setColumnStretch(0, 2)
        details_grid_layout.setColumnStretch(1, 1)

        self.shipment_table = make_table(["Заказ", "Товар", "Количество", "Зона"], [], min_height=190)
        self.shipment_info_host = QWidget()
        self.shipment_info_layout = QVBoxLayout(self.shipment_info_host)
        self.shipment_info_layout.setContentsMargins(0, 0, 0, 0)
        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress.setMinimumHeight(28)

        details_grid_layout.addWidget(self.shipment_table, 0, 0, 2, 1)
        details_grid_layout.addWidget(self.shipment_info_host, 0, 1)
        details_grid_layout.addWidget(self.progress, 1, 1)
        details_layout.addWidget(details_grid)

        shipment_actions = QWidget()
        shipment_actions_layout = QHBoxLayout(shipment_actions)
        shipment_actions_layout.setContentsMargins(0, 0, 0, 0)
        form_batch_button = QPushButton("Сформировать партию")
        print_labels_button = QPushButton("Напечатать этикетки")
        ship_button = QPushButton("Отгрузить")
        self.pdf_button = QPushButton("PDF отчёт по отгрузке")
        self.next_status_button = QPushButton("Перевести в следующий статус")
        form_batch_button.clicked.connect(self._form_batch)
        print_labels_button.clicked.connect(self._print_labels)
        ship_button.clicked.connect(self._ship_batch)
        self.pdf_button.clicked.connect(self._generate_shipment_pdf)
        self.next_status_button.clicked.connect(self._move_next_status)
        self.form_batch_button = form_batch_button
        self.ship_button = ship_button
        shipment_actions_layout.addWidget(form_batch_button)
        shipment_actions_layout.addWidget(print_labels_button)
        shipment_actions_layout.addWidget(ship_button)
        shipment_actions_layout.addWidget(self.pdf_button)
        shipment_actions_layout.addWidget(self.next_status_button)
        shipment_actions_layout.addStretch(1)
        details_layout.addWidget(shipment_actions)
        layout.addWidget(details_box)

        lifecycle_box, lifecycle_layout = group_box("Жизненный цикл")
        self.lifecycle_host = QWidget()
        self.lifecycle_layout = QVBoxLayout(self.lifecycle_host)
        self.lifecycle_layout.setContentsMargins(0, 0, 0, 0)
        lifecycle_layout.addWidget(self.lifecycle_host)
        layout.addWidget(lifecycle_box)

        history_box, history_layout = group_box("История партии")
        self.history_table = make_table(["Время", "Операция", "Пользователь", "Комментарий"], [], min_height=180)
        history_layout.addWidget(self.history_table)
        layout.addWidget(history_box)

        onec_box, onec_layout = group_box("Интеграция с 1С")
        self.onec_host = QWidget()
        self.onec_layout = QVBoxLayout(self.onec_host)
        self.onec_layout.setContentsMargins(0, 0, 0, 0)
        self.export_onec_button = QPushButton("Выгрузить закрытые отгрузки в 1С")
        self.export_onec_button.clicked.connect(self._export_closed_shipments_to_onec)
        onec_layout.addWidget(self.onec_host)
        onec_layout.addWidget(self.export_onec_button)
        layout.addWidget(onec_box)

        orders_box, orders_layout = group_box("Список заказов к отгрузке")
        for item in SHIPPING_ORDERS:
            orders_layout.addWidget(
                order_card(item["number"], item["client"], item["route"], item["status"], item["button"])
            )
        layout.addWidget(orders_box)
        layout.addStretch(1)

        self._update_shipment(self.batch_combo.currentText())
        self.apply_role()

    def _update_shipment(self, batch_id: str) -> None:
        refill_table(self.shipment_table, SHIPMENT_ITEMS[batch_id])

        while self.shipment_info_layout.count():
            item = self.shipment_info_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        info = SHIPMENT_INFO[batch_id] | {
            "Статус": mock_data.SHIPMENT_STATUSES[batch_id],
            "Статус 1С": mock_data.ONEC_SYNC_STATUS[batch_id],
        }
        self.shipment_info_layout.addWidget(info_card(info))
        self.progress.setValue(int(info["Готовность"].replace("%", "")))
        self._refresh_lifecycle(batch_id)
        refill_table(self.history_table, mock_data.SHIPMENT_HISTORY[batch_id])
        self._refresh_onec_card()

    def _form_batch(self) -> None:
        if not auth_service.has_permission("shipping:form"):
            QMessageBox.warning(self, "Права доступа", "Недостаточно прав для формирования партии.")
            return
        batch_id = self.batch_combo.currentText()
        event_log_service.add_event("SHIPMENT_CREATED", f"Сформирована партия {batch_id}", entity_id=batch_id)
        mock_data.SHIPMENT_HISTORY[batch_id].insert(0, ["--:--", "Создана партия", mock_data.CURRENT_USER, "Формирование партии"])
        QMessageBox.information(self, "Отгрузка", f"Партия {batch_id} сформирована.")
        self._update_shipment(batch_id)

    def _print_labels(self) -> None:
        batch_id = self.batch_combo.currentText()
        event_log_service.add_event("SHIPMENT_CREATED", f"Напечатаны этикетки для партии {batch_id}", entity_id=batch_id)
        mock_data.SHIPMENT_HISTORY[batch_id].insert(0, ["--:--", "Упаковка промаркирована", mock_data.CURRENT_USER, "Этикетки напечатаны"])
        QMessageBox.information(self, "Отгрузка", f"Этикетки для {batch_id} отправлены на печать.")
        self._update_shipment(batch_id)

    def _ship_batch(self) -> None:
        batch_id = self.batch_combo.currentText()
        event_log_service.add_event("SHIPMENT_CLOSED", f"Заказ отгружен в составе партии {batch_id}", entity_id=batch_id)
        mock_data.SHIPMENT_STATUSES[batch_id] = "Отгружена"
        self._sync_batch_row(batch_id)
        mock_data.SHIPMENT_HISTORY[batch_id].insert(0, ["--:--", "Партия отгружена", mock_data.CURRENT_USER, "Отгрузка выполнена"])
        QMessageBox.information(self, "Отгрузка", f"Партия {batch_id} отгружена в прототипе.")
        self._update_shipment(batch_id)

    def _move_next_status(self) -> None:
        if not auth_service.has_permission("shipping:close"):
            QMessageBox.warning(self, "Права доступа", "Недостаточно прав для закрытия отгрузок.")
            return
        batch_id = self.batch_combo.currentText()
        current = mock_data.SHIPMENT_STATUSES[batch_id]
        flow = mock_data.SHIPMENT_STATUS_FLOW
        if current == flow[-1]:
            QMessageBox.information(self, "Жизненный цикл", "Отгрузка уже находится в финальном статусе.")
            return
        next_status = flow[flow.index(current) + 1]
        mock_data.SHIPMENT_STATUSES[batch_id] = next_status
        if next_status == "Закрыта":
            mock_data.ONEC_SYNC_STATUS[batch_id] = "Готово к выгрузке"
            event_type = "SHIPMENT_CLOSED"
        else:
            event_type = "SHIPMENT_CREATED"
        mock_data.SHIPMENT_HISTORY[batch_id].insert(0, ["--:--", next_status, mock_data.CURRENT_USER, "Перевод статуса"])
        event_log_service.add_event(event_type, f"Отгрузка {batch_id} переведена в статус {next_status}", entity_id=batch_id)
        self._sync_batch_row(batch_id)
        self._update_shipment(batch_id)

    def _generate_shipment_pdf(self) -> None:
        shipment = self._current_shipment()
        path = self.pdf_service.generate_shipment_report(shipment)
        mock_data.SHIPMENT_HISTORY[shipment["id"]].insert(0, ["--:--", "Сформирован PDF", mock_data.CURRENT_USER, str(path)])
        self._update_shipment(shipment["id"])
        QMessageBox.information(self, "PDF", f"Отчёт по отгрузке сформирован:\n{path}")

    def _export_closed_shipments_to_onec(self) -> None:
        if not auth_service.has_permission("shipping:close"):
            QMessageBox.warning(self, "Права доступа", "Недостаточно прав для выгрузки в 1С.")
            return
        exported = 0
        errors = 0
        for shipment_id, status in list(mock_data.SHIPMENT_STATUSES.items()):
            if status == "Закрыта":
                if self.onec_service.export_closed_shipment(self._shipment_by_id(shipment_id)):
                    exported += 1
                else:
                    errors += 1
                self._sync_batch_row(shipment_id)
        refill_table(self.batches_table, SHIPMENT_BATCHES)
        self._update_shipment(self.batch_combo.currentText())
        QMessageBox.information(self, "1С", f"Выгружено: {exported}\nОшибок: {errors}")

    def _refresh_lifecycle(self, batch_id: str) -> None:
        while self.lifecycle_layout.count():
            item = self.lifecycle_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        current = mock_data.SHIPMENT_STATUSES[batch_id]
        flow = mock_data.SHIPMENT_STATUS_FLOW
        next_status = "Финальный статус" if current == flow[-1] else flow[flow.index(current) + 1]
        self.lifecycle_layout.addWidget(info_card({"Текущий статус": current, "Следующий статус": next_status}))

    def _refresh_onec_card(self) -> None:
        while self.onec_layout.count():
            item = self.onec_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        status = self.onec_service.get_last_sync_status()
        self.onec_layout.addWidget(
            info_card(
                {
                    "Статус подключения": str(status["connection"]),
                    "Последняя синхронизация": str(status["last_sync"]),
                    "Закрытых отгрузок": str(status["closed_shipments"]),
                    "Ошибок синхронизации": str(status["sync_errors"]),
                }
            )
        )

    def _sync_batch_row(self, batch_id: str) -> None:
        for row in SHIPMENT_BATCHES:
            if row[0] == batch_id:
                row[4] = mock_data.SHIPMENT_STATUSES[batch_id]
                row[5] = mock_data.ONEC_SYNC_STATUS[batch_id]
                break
        refill_table(self.batches_table, SHIPMENT_BATCHES)

    def _current_shipment(self) -> dict[str, str]:
        return self._shipment_by_id(self.batch_combo.currentText())

    def _shipment_by_id(self, shipment_id: str) -> dict[str, str]:
        info = SHIPMENT_INFO[shipment_id]
        return {
            "id": shipment_id,
            "status": mock_data.SHIPMENT_STATUSES[shipment_id],
            "recipient": info["Маршрут"],
            "weight": "8 600 кг",
            "packages": str(len(SHIPMENT_ITEMS[shipment_id])),
            "onec_status": mock_data.ONEC_SYNC_STATUS[shipment_id],
        }

    def apply_role(self) -> None:
        can_form = auth_service.has_permission("shipping:form")
        can_close = auth_service.has_permission("shipping:close")
        self.form_batch_button.setEnabled(can_form)
        self.ship_button.setEnabled(can_close)
        self.next_status_button.setEnabled(can_close)
        self.export_onec_button.setEnabled(can_close)
