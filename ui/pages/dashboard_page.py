from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from data import mock_data
from services.analytics_service import analytics_service
from services.event_log_service import event_log_service
from services.pdf_report_service import PDFReportService
from ui.components import cards_row, group_box, make_table, metric_card, page_shell, refill_table, title_label


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.pdf_service = PDFReportService()
        page, layout = page_shell()
        root = QGridLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(page)

        layout.addWidget(title_label("Главная панель"))

        kpi_box, kpi_layout = group_box("Ключевые показатели эффективности")
        self.kpi_layout = kpi_layout
        layout.addWidget(kpi_box)

        analytics_box, analytics_layout = group_box("Аналитика WMS/MES")
        self.analytics_layout = analytics_layout
        layout.addWidget(analytics_box)

        problems_box, problems_layout = group_box("Проблемные позиции")
        self.problem_table = make_table(
            ["Штрих-код", "Товар", "Плановый вес", "Фактический вес", "Отклонение", "Причина", "Статус"],
            mock_data.PROBLEM_POSITIONS,
            min_height=210,
        )
        problems_layout.addWidget(self.problem_table)
        layout.addWidget(problems_box)

        events_box, events_layout = group_box("Журнал событий")
        self.event_table = make_table(["Дата/время", "Тип", "Пользователь", "Сущность", "Описание"], event_log_service.get_recent_events(20), min_height=220)
        events_layout.addWidget(self.event_table)
        layout.addWidget(events_box)

        warehouse_box, warehouse_layout = group_box("Зоны склада")
        self.warehouse_layout = warehouse_layout
        layout.addWidget(warehouse_box)

        notifications_box, notifications_layout = group_box("Последние уведомления руководителю")
        self.notification_table = make_table(
            ["Время", "Тип", "Описание"],
            mock_data.MANAGER_NOTIFICATIONS,
            min_height=170,
        )
        notifications_layout.addWidget(self.notification_table)
        summary_button = QPushButton("PDF суточная сводка")
        summary_button.clicked.connect(self._generate_daily_summary)
        notifications_layout.addWidget(summary_button)
        layout.addWidget(notifications_box)
        layout.addStretch(1)

        self.refresh()

    def refresh(self) -> None:
        while self.kpi_layout.count():
            item = self.kpi_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        cards = [
            {
                "title": "Заказы в работе",
                "value": str(sum(1 for row in mock_data.ALL_ORDERS if row[5] in ("Создан", "В комплектации", "На отгрузке"))),
                "note": "комплектующие для вагонов",
                "accent": "#31506f",
            },
            {
                "title": "Принято упаковок сегодня",
                "value": str(len(mock_data.ACCEPTED_PACKAGES)),
                "note": "после контроля веса",
                "accent": "#4d7a5f",
            },
            {
                "title": "Отгружено партий сегодня",
                "value": "9",
                "note": "оперативный счетчик отгрузок",
                "accent": "#4f7188",
            },
            {
                "title": "Проблемные позиции",
                "value": str(len(mock_data.PROBLEM_POSITIONS)),
                "note": "требуют проверки",
                "accent": "#8a3b3b",
            },
            {
                "title": "Уведомления руководителю",
                "value": str(len(mock_data.MANAGER_NOTIFICATIONS)),
                "note": "журнал контроля",
                "accent": "#705b8b",
            },
        ]
        self.kpi_layout.addWidget(cards_row([metric_card(item["title"], item["value"], item["note"], item["accent"]) for item in cards]))
        self._refresh_analytics()
        self._refresh_warehouse_zones()
        refill_table(self.problem_table, mock_data.PROBLEM_POSITIONS)
        refill_table(self.event_table, event_log_service.get_recent_events(20))
        refill_table(self.notification_table, mock_data.MANAGER_NOTIFICATIONS)

    def _refresh_analytics(self) -> None:
        while self.analytics_layout.count():
            item = self.analytics_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        cards = [
            metric_card("Процент расхождений", f"{analytics_service.calculate_discrepancy_rate()}%", "по принятым упаковкам", "#8a3b3b"),
            metric_card("Среднее время приёмки", "18 мин", "расчёт за смену", "#31506f"),
            metric_card("Выгрузок в 1С", str(analytics_service.calculate_closed_shipments()), "закрытые/выгруженные", "#4d7a5f"),
            metric_card("Ошибок синхронизации", str(analytics_service.calculate_1c_sync_errors()), "интеграция", "#9a6b1f"),
            metric_card("Загрузка склада", f"{analytics_service.calculate_warehouse_load()}%", "по зонам", "#4f7188"),
            metric_card("Загрузка транспорта", "64%", "плановая загрузка", "#705b8b"),
        ]
        self.analytics_layout.addWidget(cards_row(cards))

    def _refresh_warehouse_zones(self) -> None:
        while self.warehouse_layout.count():
            item = self.warehouse_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)
        for zone in mock_data.WAREHOUSE_ZONES:
            color = "#e6f0e8"
            border = "#8dae97"
            if zone["load"] >= 90:
                color = "#f5e3e3"
                border = "#b98585"
            elif zone["load"] >= 80:
                color = "#f3ecd2"
                border = "#bca968"

            card = QFrame()
            card.setObjectName("WarehouseZoneCard")
            card.setStyleSheet(
                f"""
                QFrame#WarehouseZoneCard {{
                    background: {color};
                    border: 1px solid {border};
                    border-radius: 3px;
                }}
                QFrame#WarehouseZoneCard QLabel {{
                    background: transparent;
                    border: none;
                    padding: 0;
                }}
                """
            )
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(8, 6, 8, 6)
            zone_title = QLabel(f"{zone['zone']} — {zone['name']}")
            zone_title.setStyleSheet("background: transparent; border: none; padding: 0; font-weight: 800;")
            load = QLabel(f"Загрузка: {zone['load']}%")
            load.setStyleSheet("background: transparent; border: none; padding: 0;")
            status = QLabel(zone["status"])
            status.setStyleSheet("background: transparent; border: none; padding: 0;")
            card_layout.addWidget(zone_title)
            card_layout.addWidget(load)
            card_layout.addWidget(status)
            row_layout.addWidget(card)
        self.warehouse_layout.addWidget(row)

    def _generate_daily_summary(self) -> None:
        path = self.pdf_service.generate_daily_summary_report()
        QMessageBox.information(self, "PDF", f"Суточная сводка сформирована:\n{path}")
        self.refresh()
