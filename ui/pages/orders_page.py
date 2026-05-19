from PyQt6.QtWidgets import QComboBox, QDoubleSpinBox, QFormLayout, QGridLayout, QHBoxLayout, QLineEdit, QMessageBox, QPushButton, QSpinBox, QWidget

from data import mock_data
from data.mock_data import ALL_ORDERS, ORDER_DETAILS, RAIL_PRODUCTS
from services.auth_service import auth_service
from services.event_log_service import event_log_service
from ui.components import append_table_row, group_box, info_card, make_table, page_shell, title_label


class OrdersPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        page, layout = page_shell()
        root = QGridLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(page)

        layout.addWidget(title_label("Реестр заказов"))
        self.orders_table = make_table(
            ["Заказ", "Получатель", "Товар", "Количество", "Плановый вес", "Статус", "Приоритет"],
            ALL_ORDERS,
            min_height=280,
        )
        layout.addWidget(self.orders_table)

        create_box, create_layout = group_box("Создание заказа")
        form_host = QWidget()
        form = QFormLayout(form_host)
        self.receiver_input = QLineEdit("Цех сборки кузовов")
        self.product_combo = QComboBox()
        self.product_combo.addItems(RAIL_PRODUCTS)
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 100000)
        self.quantity_input.setValue(10)
        self.planned_weight_input = QDoubleSpinBox()
        self.planned_weight_input.setRange(1, 100000)
        self.planned_weight_input.setDecimals(2)
        self.planned_weight_input.setSuffix(" кг")
        self.planned_weight_input.setValue(500.00)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Высокий", "Средний", "Низкий"])
        form.addRow("Получатель", self.receiver_input)
        form.addRow("Товар", self.product_combo)
        form.addRow("Количество", self.quantity_input)
        form.addRow("Плановый вес", self.planned_weight_input)
        form.addRow("Приоритет", self.priority_combo)
        create_layout.addWidget(form_host)

        action_row = QWidget()
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(0, 0, 0, 0)
        create_button = QPushButton("Создать заказ")
        create_button.clicked.connect(self._create_order)
        self.create_button = create_button
        action_layout.addWidget(create_button)
        next_status_button = QPushButton("Перевести заказ в следующий статус")
        next_status_button.clicked.connect(self._move_order_next_status)
        self.next_status_button = next_status_button
        action_layout.addWidget(next_status_button)
        action_layout.addStretch(1)
        create_layout.addWidget(action_row)
        layout.addWidget(create_box)

        details_box, details_layout = group_box("Детальная информация по заказам")
        for detail in ORDER_DETAILS:
            item_box, item_layout = group_box(detail["title"])
            item_layout.addWidget(info_card({"Описание": detail["text"]}))
            details_layout.addWidget(item_box)
        layout.addWidget(details_box)
        layout.addStretch(1)
        self.apply_role()

    def _create_order(self) -> None:
        receiver = self.receiver_input.text().strip()
        if not receiver:
            QMessageBox.warning(self, "Заказы", "Укажите получателя.")
            return

        order_number = f"ORD-{3100 + len(mock_data.ALL_ORDERS) + 1}"
        row = [
            order_number,
            receiver,
            self.product_combo.currentText(),
            f"{self.quantity_input.value()} шт.",
            f"{self.planned_weight_input.value():.2f} кг",
            "Создан",
            self.priority_combo.currentText(),
        ]
        mock_data.ALL_ORDERS.append(row)
        append_table_row(self.orders_table, row)
        event_log_service.add_event("ORDER_CREATED", f"Создан заказ {order_number}", entity_id=order_number)
        QMessageBox.information(self, "Заказы", f"Заказ {order_number} создан в памяти прототипа.")

    def _move_order_next_status(self) -> None:
        if not auth_service.has_permission("orders:create"):
            QMessageBox.warning(self, "Права доступа", "Недостаточно прав для изменения заказа.")
            return
        row_index = self.orders_table.currentRow()
        if row_index < 0:
            row_index = 0
        status_flow = ["Создан", "В комплектации", "Скомплектован", "На отгрузке", "Отгружен", "Закрыт"]
        current = mock_data.ALL_ORDERS[row_index][5]
        if current == status_flow[-1]:
            QMessageBox.information(self, "Заказы", "Заказ уже закрыт.")
            return
        next_status = status_flow[status_flow.index(current) + 1] if current in status_flow else "Создан"
        mock_data.ALL_ORDERS[row_index][5] = next_status
        self.orders_table.item(row_index, 5).setText(next_status)
        event_log_service.add_event("ORDER_CREATED", f"Заказ {mock_data.ALL_ORDERS[row_index][0]} переведён в статус {next_status}", entity_id=mock_data.ALL_ORDERS[row_index][0])
        QMessageBox.information(self, "Заказы", f"Новый статус заказа: {next_status}")

    def apply_role(self) -> None:
        allowed = auth_service.has_permission("orders:create")
        self.create_button.setEnabled(allowed)
        self.next_status_button.setEnabled(allowed)
