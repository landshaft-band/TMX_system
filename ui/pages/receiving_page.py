from PyQt6.QtWidgets import QComboBox, QFormLayout, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QWidget

from data import mock_data
from data.mock_data import (
    BATCH_ITEMS,
    BATCH_PASSPORTS,
    ACCEPTED_PACKAGES,
    INCOMING_SUPPLIES,
    PROBLEM_POSITIONS,
    RAIL_PRODUCTS,
    RECEIVING_ORDERS,
)
from services import barcode_service, discrepancy_service, notification_service
from services.auth_service import auth_service
from services.event_log_service import event_log_service
from services.pdf_report_service import PDFReportService
from services.scale_service import ScaleService
from ui.components import (
    append_table_row,
    group_box,
    info_card,
    make_button,
    make_table,
    page_shell,
    refill_table,
    title_label,
)


class ReceivingPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.scale_service = ScaleService()
        self.pdf_service = PDFReportService()
        page, layout = page_shell()
        root = QGridLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(page)

        layout.addWidget(title_label("Приёмка товара"))

        supplies_box, supplies_layout = group_box("Поступающие поставки")
        supplies_layout.addWidget(
            make_table(
                ["Поставка", "Поставщик", "Время прибытия", "Объем", "Статус"],
                INCOMING_SUPPLIES,
                min_height=210,
            )
        )
        layout.addWidget(supplies_box)

        passport_box, passport_layout = group_box("Паспорт партии")
        self.supply_combo = QComboBox()
        self.supply_combo.addItems(BATCH_PASSPORTS.keys())
        self.supply_combo.currentTextChanged.connect(self._update_passport)
        passport_layout.addWidget(self.supply_combo)

        self.passport_host = QWidget()
        self.passport_host_layout = QGridLayout(self.passport_host)
        self.passport_host_layout.setContentsMargins(0, 0, 0, 0)
        passport_layout.addWidget(self.passport_host)

        self.batch_table = make_table(["Артикул", "Наименование", "Количество", "Вес"], [], min_height=180)
        passport_layout.addWidget(self.batch_table)
        layout.addWidget(passport_box)

        scan_box, scan_layout = group_box("Сканирование и умные весы")
        form_row = QWidget()
        form_layout = QFormLayout(form_row)
        form_layout.setContentsMargins(0, 0, 0, 0)

        self.product_combo = QComboBox()
        self.product_combo.addItems(RAIL_PRODUCTS)
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Штрихкод упаковки")
        self.scale_status = QLabel("Не подключены")
        self.scale_status.setObjectName("StatusPill")
        self.planned_weight_input = QLineEdit("320.00")
        self.actual_weight_input = QLineEdit()
        self.actual_weight_input.setPlaceholderText("получите вес с весов")
        self.tolerance_input = QLineEdit("3")

        form_layout.addRow("Товар", self.product_combo)
        form_layout.addRow("Штрих-код", self.barcode_input)
        form_layout.addRow("Статус весов", self.scale_status)
        form_layout.addRow("Плановый вес, кг", self.planned_weight_input)
        form_layout.addRow("Фактический вес, кг", self.actual_weight_input)
        form_layout.addRow("Допустимое отклонение, %", self.tolerance_input)
        scan_layout.addWidget(form_row)

        scan_actions = QWidget()
        scan_actions_layout = QHBoxLayout(scan_actions)
        scan_actions_layout.setContentsMargins(0, 0, 0, 0)
        generate_button = make_button("Сгенерировать штрих-код")
        generate_button.clicked.disconnect()
        generate_button.clicked.connect(self._generate_barcode)
        scan_button = make_button("Сканировать")
        scan_button.clicked.disconnect()
        scan_button.clicked.connect(self._scan_barcode)
        connect_button = make_button("Подключить весы")
        connect_button.clicked.disconnect()
        connect_button.clicked.connect(self._connect_scale)
        simulate_button = make_button("Симулировать вес")
        simulate_button.clicked.disconnect()
        simulate_button.clicked.connect(self._simulate_weight)
        self.accept_button = make_button("Проверить и принять")
        self.accept_button.clicked.disconnect()
        self.accept_button.clicked.connect(self._check_and_accept)
        scan_actions_layout.addWidget(generate_button)
        scan_actions_layout.addWidget(scan_button)
        scan_actions_layout.addWidget(connect_button)
        scan_actions_layout.addWidget(simulate_button)
        scan_actions_layout.addWidget(self.accept_button)
        scan_actions_layout.addStretch(1)
        scan_layout.addWidget(scan_actions)

        self.accepted_table = make_table(
            ["Штрих-код", "Товар", "Плановый вес", "Фактический вес", "Отклонение", "Статус"],
            ACCEPTED_PACKAGES,
            min_height=180,
        )
        accepted_box, accepted_layout = group_box("Принятые упаковки")
        accepted_layout.addWidget(self.accepted_table)
        scan_layout.addWidget(accepted_box)

        self.problem_table = make_table(
            ["Штрих-код", "Товар", "Плановый вес", "Фактический вес", "Отклонение", "Причина", "Статус"],
            PROBLEM_POSITIONS,
            min_height=180,
        )
        problem_box, problem_layout = group_box("Проблемные позиции")
        problem_layout.addWidget(self.problem_table)
        discrepancy_pdf_button = make_button("PDF акт расхождения")
        discrepancy_pdf_button.clicked.disconnect()
        discrepancy_pdf_button.clicked.connect(self._generate_discrepancy_pdf)
        problem_layout.addWidget(discrepancy_pdf_button)
        scan_layout.addWidget(problem_box)
        layout.addWidget(scan_box)

        control_box, control_layout = group_box("Управление приёмкой")
        control_layout.addWidget(
            make_table(["Заказ", "Поставка", "Комментарий", "Статус"], RECEIVING_ORDERS, min_height=160)
        )
        selected_order = info_card(
            {
                "Выбранный заказ": "RCV-502",
                "Операция": "Проверка веса и маркировки",
                "Ответственный": "Орлова Н.С.",
            }
        )
        control_layout.addWidget(selected_order)
        batch_pdf_button = make_button("PDF паспорт партии")
        batch_pdf_button.clicked.disconnect()
        batch_pdf_button.clicked.connect(self._generate_batch_pdf)
        control_layout.addWidget(batch_pdf_button)
        control_layout.addWidget(make_button("Начать приёмку", "Приёмка запущена в прототипе"))
        layout.addWidget(control_box)
        layout.addStretch(1)

        self._update_passport(self.supply_combo.currentText())
        self.apply_role()

    def _update_passport(self, supply_id: str) -> None:
        while self.passport_host_layout.count():
            item = self.passport_host_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.passport_host_layout.addWidget(info_card(BATCH_PASSPORTS[supply_id]), 0, 0)
        refill_table(self.batch_table, BATCH_ITEMS[supply_id])

    def _generate_barcode(self) -> None:
        barcode = barcode_service.generate_barcode()
        self.barcode_input.setText(barcode)
        event_log_service.add_event("SCAN", f"Сгенерирован штрих-код {barcode}", entity_id=barcode)

    def _scan_barcode(self) -> None:
        barcode = self.barcode_input.text().strip()
        if not barcode:
            QMessageBox.warning(self, "Сканирование", "Введите или сгенерируйте штрих-код.")
            return
        event_log_service.add_event("SCAN", f"Сканирован штрих-код {barcode}", entity_id=barcode)
        QMessageBox.information(self, "Сканирование", f"Штрих-код {barcode} считан.")

    def _connect_scale(self) -> None:
        self.scale_service.connect()
        self.scale_status.setText("Подключены")
        event_log_service.add_event("WEIGHT_RECEIVED", "Умные весы подключены")
        QMessageBox.information(self, "Весы", "Умные весы подключены в демонстрационном режиме.")

    def _simulate_weight(self) -> None:
        try:
            planned_weight = float(self.planned_weight_input.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Весы", "Плановый вес должен быть числом.")
            return

        if not self.scale_service.connected:
            self._connect_scale()

        actual_weight = self.scale_service.simulate_weight(planned_weight)
        self.actual_weight_input.setText(f"{actual_weight:.2f}")
        event_log_service.add_event("WEIGHT_RECEIVED", f"Получен вес {actual_weight:.2f} кг для {self.product_combo.currentText()}")

    def _check_and_accept(self) -> None:
        if not auth_service.has_permission("receiving:accept"):
            QMessageBox.warning(self, "Права доступа", "Недостаточно прав для приёмки упаковки.")
            return

        barcode = self.barcode_input.text().strip()
        product = self.product_combo.currentText()
        if not barcode:
            QMessageBox.warning(self, "Приёмка", "Сначала укажите штрих-код.")
            return

        try:
            planned_weight = float(self.planned_weight_input.text().replace(",", "."))
            actual_weight = float(self.actual_weight_input.text().replace(",", "."))
            tolerance = float(self.tolerance_input.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Приёмка", "Плановый вес, фактический вес и допуск должны быть числами.")
            return

        result = discrepancy_service.check_package(planned_weight, actual_weight, tolerance)
        deviation = float(result["deviation"])
        status = str(result["status"])
        reason = str(result["reason"])

        if status == "Принято":
            row = [
                barcode,
                product,
                f"{planned_weight:.2f} кг",
                f"{actual_weight:.2f} кг",
                f"{deviation:.2f}%",
                status,
            ]
            mock_data.ACCEPTED_PACKAGES.insert(0, row)
            append_table_row(self.accepted_table, row)
            event_log_service.add_event("ACCEPTED", f"Упаковка {barcode} принята", entity_id=barcode)
            QMessageBox.information(self, "Приёмка", "Упаковка принята. Отклонение в пределах допуска.")
            return

        row = [
            barcode,
            product,
            f"{planned_weight:.2f} кг",
            f"{actual_weight:.2f} кг",
            f"{deviation:.2f}%",
            reason,
            "Требует проверки",
        ]
        mock_data.PROBLEM_POSITIONS.insert(0, row)
        append_table_row(self.problem_table, row)
        event_log_service.add_event("DISCREPANCY", f"Обнаружено расхождение по {product}: {barcode}", entity_id=barcode)
        notification_service.create_manager_notification(barcode, product, deviation)
        QMessageBox.warning(
            self,
            "Расхождение",
            f"Отклонение {deviation:.2f}% больше допустимых {tolerance:.2f}%.\nПозиция отправлена на проверку.",
        )

    def _generate_discrepancy_pdf(self) -> None:
        if not auth_service.has_permission("reports:discrepancy") and not auth_service.has_permission("reports:view"):
            QMessageBox.warning(self, "Права доступа", "Недостаточно прав для формирования акта расхождения.")
            return
        if not mock_data.PROBLEM_POSITIONS:
            QMessageBox.warning(self, "PDF", "Нет проблемных позиций для акта.")
            return
        path = self.pdf_service.generate_discrepancy_report(mock_data.PROBLEM_POSITIONS[0])
        QMessageBox.information(self, "PDF", f"Акт расхождения сформирован:\n{path}")

    def _generate_batch_pdf(self) -> None:
        if not auth_service.has_permission("reports:batch") and not auth_service.has_permission("reports:view"):
            QMessageBox.warning(self, "Права доступа", "Недостаточно прав для формирования паспорта партии.")
            return
        supply_id = self.supply_combo.currentText()
        path = self.pdf_service.generate_batch_passport({"id": supply_id})
        QMessageBox.information(self, "PDF", f"Паспорт партии сформирован:\n{path}")

    def apply_role(self) -> None:
        self.accept_button.setEnabled(auth_service.has_permission("receiving:accept"))
