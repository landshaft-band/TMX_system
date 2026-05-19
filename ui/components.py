from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QScrollArea,
)


STATUS_COLORS = {
    "Принято": ("#e6f0e8", "#2f6b3f"),
    "Расхождение": ("#f5e3e3", "#8a2d2d"),
    "Требует проверки": ("#f3ecd2", "#7a5a18"),
    "В работе": ("#e4ebf3", "#31506f"),
    "Создан": ("#eef1f4", "#5b6773"),
    "В комплектации": ("#e4ebf3", "#31506f"),
    "Скомплектован": ("#e6f0e8", "#2f6b3f"),
    "На отгрузке": ("#e4ebf3", "#31506f"),
    "Отгружен": ("#e6f0e8", "#2f6b3f"),
    "Закрыт": ("#eef1f4", "#5b6773"),
    "Черновик": ("#eef1f4", "#5b6773"),
    "Формируется": ("#e4ebf3", "#31506f"),
    "Готова к отгрузке": ("#e6f0e8", "#2f6b3f"),
    "Отгружена": ("#e6f0e8", "#2f6b3f"),
    "Закрыта": ("#eef1f4", "#5b6773"),
    "Выгружена в 1С": ("#e6f0e8", "#2f6b3f"),
    "Не выгружено": ("#eef1f4", "#5b6773"),
    "Готово к выгрузке": ("#f3ecd2", "#7a5a18"),
    "Выгружено в 1С": ("#e6f0e8", "#2f6b3f"),
    "Ошибка синхронизации": ("#f5e3e3", "#8a2d2d"),
    "Комплектация": ("#e4ebf3", "#31506f"),
    "Готов к комплектации": ("#e4ebf3", "#31506f"),
    "Готовится": ("#e4ebf3", "#31506f"),
    "Готов": ("#e6f0e8", "#2f6b3f"),
    "Готова": ("#e6f0e8", "#2f6b3f"),
    "Ожидает": ("#eef1f4", "#5b6773"),
    "Запланирована": ("#eef1f4", "#5b6773"),
    "Проблема": ("#f5e3e3", "#8a2d2d"),
    "Новый": ("#eef1f4", "#5b6773"),
}


def make_button(text: str, message: str | None = None, secondary: bool = False) -> QPushButton:
    button = QPushButton(text)
    if secondary:
        button.setObjectName("SecondaryButton")
    if message:
        button.clicked.connect(lambda: QMessageBox.information(button, "Действие", message))
    else:
        button.clicked.connect(lambda: print(f"Нажата кнопка: {text}"))
    return button


def make_table(headers: list[str], rows: list[list[str]], min_height: int = 190) -> QTableWidget:
    table = QTableWidget()
    table.setColumnCount(len(headers))
    table.setRowCount(len(rows))
    table.setHorizontalHeaderLabels(headers)
    table.verticalHeader().setVisible(False)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    table.setMinimumHeight(min_height)
    table.verticalHeader().setDefaultSectionSize(25)
    table.horizontalHeader().setMinimumHeight(28)
    table.horizontalHeader().setStretchLastSection(True)

    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            _apply_status_style(item)
            table.setItem(row_index, col_index, item)

    table.resizeColumnsToContents()
    return table


def refill_table(table: QTableWidget, rows: list[list[str]]) -> None:
    table.setRowCount(len(rows))
    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            _apply_status_style(item)
            table.setItem(row_index, col_index, item)
    table.resizeColumnsToContents()


def append_table_row(table: QTableWidget, row: list[str]) -> None:
    row_index = table.rowCount()
    table.insertRow(row_index)
    for col_index, value in enumerate(row):
        item = QTableWidgetItem(str(value))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        _apply_status_style(item)
        table.setItem(row_index, col_index, item)
    table.resizeColumnsToContents()


def _apply_status_style(item: QTableWidgetItem) -> None:
    value = item.text()
    if value not in STATUS_COLORS:
        return

    background, foreground = STATUS_COLORS[value]
    item.setBackground(QBrush(QColor(background)))
    item.setForeground(QBrush(QColor(foreground)))


def page_shell() -> tuple[QWidget, QVBoxLayout]:
    page = QWidget()
    root = QVBoxLayout(page)
    root.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    root.addWidget(scroll)

    content = QWidget()
    layout = QVBoxLayout(content)
    layout.setContentsMargins(18, 14, 18, 18)
    layout.setSpacing(10)
    scroll.setWidget(content)
    return page, layout


def title_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("PageTitle")
    return label


def group_box(title: str) -> tuple[QGroupBox, QVBoxLayout]:
    box = QGroupBox(title)
    layout = QVBoxLayout(box)
    layout.setSpacing(8)
    return box, layout


def metric_card(title: str, value: str, note: str, accent: str) -> QFrame:
    card = QFrame()
    card.setObjectName("MetricCard")
    card.setMinimumHeight(88)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(10, 8, 10, 8)
    layout.setSpacing(3)

    marker = QFrame()
    marker.setFixedSize(28, 3)
    marker.setStyleSheet(f"background: {accent}; border-radius: 1px;")

    title_widget = QLabel(title)
    title_widget.setObjectName("MetricTitle")
    value_widget = QLabel(value)
    value_widget.setObjectName("MetricValue")
    note_widget = QLabel(note)
    note_widget.setObjectName("Muted")

    layout.addWidget(marker)
    layout.addWidget(title_widget)
    layout.addWidget(value_widget)
    layout.addWidget(note_widget)
    return card


def info_card(items: dict[str, str]) -> QFrame:
    card = QFrame()
    card.setObjectName("InfoCard")
    layout = QGridLayout(card)
    layout.setContentsMargins(10, 8, 10, 8)
    layout.setHorizontalSpacing(12)
    layout.setVerticalSpacing(5)

    for row, (key, value) in enumerate(items.items()):
        key_label = QLabel(key)
        key_label.setObjectName("Muted")
        value_label = QLabel(value)
        value_label.setWordWrap(True)
        value_label.setStyleSheet("font-weight: 700;")
        layout.addWidget(key_label, row, 0)
        layout.addWidget(value_label, row, 1)

    return card


def cards_row(cards: list[QWidget]) -> QWidget:
    wrapper = QWidget()
    layout = QHBoxLayout(wrapper)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    for card in cards:
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(card)
    return wrapper


def order_card(number: str, client: str, route: str, status: str, button_text: str) -> QFrame:
    card = QFrame()
    card.setObjectName("OrderCard")
    layout = QHBoxLayout(card)
    layout.setContentsMargins(10, 8, 10, 8)
    layout.setSpacing(10)

    info = QVBoxLayout()
    number_label = QLabel(number)
    number_label.setStyleSheet("font-size: 13px; font-weight: 800;")
    client_label = QLabel(client)
    client_label.setObjectName("Muted")
    route_label = QLabel(f"Маршрут: {route}")
    route_label.setObjectName("Muted")
    info.addWidget(number_label)
    info.addWidget(client_label)
    info.addWidget(route_label)

    status_label = QLabel(status)
    status_label.setFixedWidth(150)
    status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    status_label.setStyleSheet("color: #334155; font-weight: 700; padding-left: 8px;")

    action = make_button(button_text, f"{button_text}: {number}")

    layout.addLayout(info, 1)
    layout.addWidget(status_label)
    layout.addWidget(action)
    return card


def list_widget(items: list[str]) -> QListWidget:
    widget = QListWidget()
    widget.addItems(items)
    widget.setMinimumHeight(104)
    return widget
