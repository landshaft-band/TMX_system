from pathlib import Path
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from data.mock_data import SYSTEM_STATUS, TOP_STATS
from services.audit_service import audit_service
from services.auth_service import auth_service
from services.event_log_service import event_log_service
from ui.pages.dashboard_page import DashboardPage
from ui.pages.integrations_page import IntegrationsPage
from ui.pages.logistics_page import LogisticsPage
from ui.pages.orders_page import OrdersPage
from ui.pages.receiving_page import ReceivingPage
from ui.pages.reports_page import ReportsPage
from ui.pages.shipping_page import ShippingPage
from ui.pages.users_page import UsersPage


ROLE_VISIBLE_PAGES = {
    "Администратор": ["Главное", "Приёмка", "Отгрузка", "Заказы", "Логистика", "Интеграции", "Пользователи", "Отчёты"],
    "Менеджер": ["Главное", "Отгрузка", "Заказы", "Интеграции", "Отчёты"],
    "Кладовщик": ["Главное", "Приёмка"],
    "Приёмщик": ["Главное", "Приёмка"],
    "Логист": ["Главное", "Логистика", "Отгрузка", "Интеграции"],
    "Руководитель": ["Главное", "Заказы", "Отгрузка", "Логистика", "Интеграции", "Пользователи", "Отчёты"],
}


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Склад комплектующих для вагонов")
        self.resize(1360, 860)

        self.nav_buttons: dict[str, QPushButton] = {}
        self.page_indexes: dict[str, int] = {}
        self.current_page_title = "Главное"
        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.pages = {
            "Главное": self.dashboard_page,
            "Приёмка": ReceivingPage(),
            "Отгрузка": ShippingPage(),
            "Заказы": OrdersPage(),
            "Логистика": LogisticsPage(),
            "Интеграции": IntegrationsPage(),
            "Пользователи": UsersPage(),
            "Отчёты": ReportsPage(),
        }
        for title, page in self.pages.items():
            self.page_indexes[title] = self.stack.addWidget(page)

        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_workspace(), 1)

        self.setCentralWidget(central)
        self.apply_role_permissions(auth_service.current_role(), log_event=False)
        self._set_active_page_by_title("Главное")

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(250)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        user_card = QFrame()
        user_card.setObjectName("UserCard")
        user_layout = QVBoxLayout(user_card)
        user_layout.setContentsMargins(12, 10, 12, 10)
        name = QLabel("Смирнов А.Н.")
        name.setStyleSheet("font-size: 13px; font-weight: 800; color: #f4f7fa;")
        self.user_role_label = QLabel(auth_service.current_role())
        self.user_role_label.setObjectName("Muted")
        user_layout.addWidget(name)
        user_layout.addWidget(self.user_role_label)
        layout.addWidget(user_card)

        menu_label = QLabel("Разделы")
        menu_label.setObjectName("Muted")
        layout.addWidget(menu_label)

        self.nav_container = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(8)
        layout.addWidget(self.nav_container)

        layout.addStretch(1)
        return sidebar

    def _build_workspace(self) -> QWidget:
        workspace = QWidget()
        layout = QVBoxLayout(workspace)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())
        layout.addWidget(self.stack, 1)
        return workspace

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("TopHeader")
        header.setStyleSheet("QFrame#TopHeader { background: #f2f5f7; border-bottom: 1px solid #b8c2cc; }")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(14)

        logo = QFrame()
        logo.setFixedSize(256, 116)
        logo_layout = QVBoxLayout(logo)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_label = QLabel("Логотип компании")
        logo_label.setObjectName("LogoText")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_path = self._resource_path("tmh.png")
        pixmap = QPixmap(str(logo_path))
        if not pixmap.isNull():
            logo_label.setText("")
            logo_label.setPixmap(
                pixmap.scaled(
                    240,
                    104,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        logo_layout.addWidget(logo_label)

        title = QLabel("Панель управления складом")
        title.setObjectName("AppTitle")

        mode_box = QFrame()
        mode_layout = QHBoxLayout(mode_box)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(8)
        mode_label = QLabel("Роль")
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Администратор", "Менеджер", "Кладовщик", "Приёмщик", "Логист", "Руководитель"])
        self.role_combo.setCurrentText(auth_service.current_role())
        self.role_combo.currentTextChanged.connect(self._change_role)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.role_combo)

        system_status = QWidget()
        system_status_layout = QHBoxLayout(system_status)
        system_status_layout.setContentsMargins(0, 0, 0, 0)
        system_status_layout.setSpacing(6)
        for status_title, status_value in SYSTEM_STATUS.items():
            system_status_layout.addWidget(self._status_badge(status_title, status_value))

        stats = QWidget()
        stats_layout = QHBoxLayout(stats)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        for item in TOP_STATS:
            stats_layout.addWidget(self._header_stat(item["title"], item["value"], item["accent"]))

        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(6)
        bottom_row = QWidget()
        bottom_row_layout = QHBoxLayout(bottom_row)
        bottom_row_layout.setContentsMargins(0, 0, 0, 0)
        bottom_row_layout.setSpacing(10)
        bottom_row_layout.addWidget(mode_box)
        bottom_row_layout.addWidget(stats)
        right_panel_layout.addWidget(system_status)
        right_panel_layout.addWidget(bottom_row)

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch(1)
        layout.addWidget(right_panel)
        return header

    def _header_stat(self, title: str, value: str, accent: str) -> QWidget:
        card = QFrame()
        card.setObjectName("HeaderStat")
        card.setFixedSize(98, 46)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 5, 8, 5)
        layout.setSpacing(1)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 16px; font-weight: 800; color: {accent};")
        title_label = QLabel(title)
        title_label.setObjectName("Muted")
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        return card

    def _status_badge(self, title: str, value: str) -> QWidget:
        ok_values = {"Подключено", "Подключены", "Активен", "Готово", "Mock"}
        color = "#2f6b3f" if value in ok_values else "#8a3b3b"
        background = "#e6f0e8" if value in ok_values else "#f5e3e3"
        badge = QFrame()
        badge.setStyleSheet(
            f"""
            QFrame {{
                background: {background};
                border: 1px solid #aeb8c3;
                border-radius: 3px;
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: {color};
                font-weight: 700;
            }}
            """
        )
        layout = QHBoxLayout(badge)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(4)
        layout.addWidget(QLabel(f"{title}: {value}"))
        return badge

    def _resource_path(self, relative_path: str) -> Path:
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / relative_path
        return Path(__file__).resolve().parent.parent / relative_path

    def _set_active_page_by_title(self, title: str) -> None:
        visible_pages = self._visible_pages(auth_service.current_role())
        if title not in visible_pages:
            QMessageBox.warning(self, "Права доступа", "Недостаточно прав для открытия раздела.")
            title = "Главное"

        self.current_page_title = title
        self.stack.setCurrentIndex(self.page_indexes[title])

        current_page = self.stack.currentWidget()
        if hasattr(current_page, "refresh"):
            current_page.refresh()

        for page_title, button in self.nav_buttons.items():
            is_active = page_title == title
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)
        print(f"Открыта страница: {title}")

    def _change_role(self, role: str) -> None:
        auth_service.set_role(role)
        self.apply_role_permissions(role)
        for page in self.pages.values():
            if hasattr(page, "apply_role"):
                page.apply_role()
        print(f"Роль: {role}")

    def apply_role_permissions(self, role: str, log_event: bool = True) -> None:
        self._clear_nav_buttons()
        self.user_role_label.setText(role)

        for title in self._visible_pages(role):
            if title not in self.pages:
                continue
            button = QPushButton(title)
            button.setObjectName("NavButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, page_title=title: self._set_active_page_by_title(page_title))
            self.nav_buttons[title] = button
            self.nav_layout.addWidget(button)

        if self.current_page_title not in self._visible_pages(role):
            self._set_active_page_by_title("Главное")
        else:
            self._set_active_page_by_title(self.current_page_title)

        if log_event:
            event_log_service.add_event("ROLE_CHANGED", f"Роль пользователя изменена: {role}", user="Смирнов А.Н.")
            audit_service.add_record("Изменение роли пользователя", "Главное окно", "Успешно", user="Смирнов А.Н.", role=role)

    def _clear_nav_buttons(self) -> None:
        while self.nav_layout.count():
            item = self.nav_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.nav_buttons.clear()

    def _visible_pages(self, role: str) -> list[str]:
        return [title for title in ROLE_VISIBLE_PAGES.get(role, ["Главное"]) if title in self.pages]
