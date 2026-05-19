from PyQt6.QtWidgets import QComboBox, QFormLayout, QGridLayout, QHBoxLayout, QMessageBox, QSpinBox, QWidget

from data.mock_data import LOGISTICS_ORDERS, TRANSPORT_OPTIONS
from services.auth_service import auth_service
from services.event_log_service import event_log_service
from ui.components import group_box, info_card, make_button, make_table, page_shell, title_label


class LogisticsPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        page, layout = page_shell()
        root = QGridLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(page)

        layout.addWidget(title_label("Логистика и транспорт"))

        planning_box, planning_layout = group_box("Заказы для планирования")
        planning_layout.addWidget(
            make_table(["Заказ", "Направление", "Вес", "Приоритет", "Срок"], LOGISTICS_ORDERS, min_height=220)
        )
        layout.addWidget(planning_box)

        priority_box, priority_layout = group_box("Изменение приоритета заказа")
        priority_form = QWidget()
        form = QFormLayout(priority_form)
        self.order_combo = QComboBox()
        self.order_combo.addItems([row[0] for row in LOGISTICS_ORDERS])
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Высокий", "Средний", "Низкий"])
        form.addRow("Заказ", self.order_combo)
        form.addRow("Приоритет", self.priority_combo)
        priority_layout.addWidget(priority_form)
        priority_layout.addWidget(make_button("Применить приоритет", "Приоритет применен в прототипе"))
        layout.addWidget(priority_box)

        transport_box, transport_layout = group_box("Настройка транспорта")
        transport_row = QWidget()
        transport_row_layout = QHBoxLayout(transport_row)
        transport_row_layout.setContentsMargins(0, 0, 0, 0)
        transport_row_layout.setSpacing(12)
        for transport in TRANSPORT_OPTIONS:
            card = info_card(
                {
                    "Тип": transport["name"],
                    "Грузоподъемность": transport["capacity"],
                    "Назначение": transport["note"],
                }
            )
            spin = QSpinBox()
            spin.setRange(0, 99)
            spin.setValue(transport["default"])
            spin.setPrefix("Ед.: ")
            wrapper = QWidget()
            wrapper_layout = QGridLayout(wrapper)
            wrapper_layout.setContentsMargins(0, 0, 0, 0)
            wrapper_layout.addWidget(card, 0, 0)
            wrapper_layout.addWidget(spin, 1, 0)
            transport_row_layout.addWidget(wrapper)
        transport_layout.addWidget(transport_row)
        self.calculate_button = make_button("Рассчитать транспорт", None, secondary=True)
        transport_layout.addWidget(self.calculate_button)
        self.calculate_button.clicked.disconnect()
        self.calculate_button.clicked.connect(self._calculate_transport)
        layout.addWidget(transport_box)

        formation_box, formation_layout = group_box("Формирование отправок")
        formation_layout.addWidget(make_button("Сформировать отправки", "Отправки сформированы."))
        layout.addWidget(formation_box)
        layout.addStretch(1)
        self.apply_role()

    def _calculate_transport(self) -> None:
        if not auth_service.has_permission("logistics:calculate"):
            QMessageBox.warning(self, "Права доступа", "Недостаточно прав для расчёта транспорта.")
            return
        total_kg = sum(self._parse_weight(row[2]) for row in LOGISTICS_ORDERS)
        if total_kg <= 1000:
            recommendation = "Малый транспорт"
        elif total_kg <= 5000:
            recommendation = "Средний транспорт"
        elif total_kg <= 12000:
            recommendation = "Большой транспорт"
        else:
            recommendation = "Фура"

        event_log_service.add_event("SHIPMENT_CREATED", f"Рассчитан транспорт: {recommendation} для {total_kg:.0f} кг")
        QMessageBox.information(
            self,
            "Расчет транспорта",
            f"Суммарный вес заказов: {total_kg:.0f} кг.\nРекомендация: {recommendation}.",
        )

    def _parse_weight(self, value: str) -> float:
        return float(value.replace("кг", "").replace(" ", "").replace(",", ".").strip())

    def apply_role(self) -> None:
        self.calculate_button.setEnabled(auth_service.has_permission("logistics:calculate"))
