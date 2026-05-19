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

from data.mock_data import TOP_STATS
from services.auth_service import auth_service
from ui.pages.dashboard_page import DashboardPage
from ui.pages.logistics_page import LogisticsPage
from ui.pages.orders_page import OrdersPage
from ui.pages.receiving_page import ReceivingPage
from ui.pages.reports_page import ReportsPage
from ui.pages.shipping_page import ShippingPage
from ui.pages.users_page import UsersPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Склад комплектующих для вагонов")
        self.resize(1360, 860)

        self.nav_buttons: list[QPushButton] = []
        self.page_permissions: list[str] = []
        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage()

        central = QWidget()
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_workspace(), 1)

        self.setCentralWidget(central)
        self._set_active_page(0)

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
        role = QLabel("Менеджер")
        role.setObjectName("Muted")
        user_layout.addWidget(name)
        user_layout.addWidget(role)
        layout.addWidget(user_card)

        menu_label = QLabel("Разделы")
        menu_label.setObjectName("Muted")
        layout.addWidget(menu_label)

        pages = [
            ("Главное", self.dashboard_page, "dashboard:view"),
            ("Приемка", ReceivingPage(), "receiving:view"),
            ("Отгрузка", ShippingPage(), "shipping:view"),
            ("Заказы", OrdersPage(), "orders:view"),
            ("Логистика", LogisticsPage(), "logistics:view"),
            ("Отчёты", ReportsPage(), "reports:view"),
            ("Пользователи", UsersPage(), "users:view"),
        ]

        for index, (title, page, permission) in enumerate(pages):
            self.stack.addWidget(page)
            self.page_permissions.append(permission)
            button = QPushButton(title)
            button.setObjectName("NavButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda checked=False, page_index=index: self._set_active_page(page_index))
            self.nav_buttons.append(button)
            layout.addWidget(button)

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
        self.role_combo.addItems(["Приёмщик", "Менеджер", "Логист", "Руководитель", "Администратор"])
        self.role_combo.setCurrentText(auth_service.current_role())
        self.role_combo.currentTextChanged.connect(self._change_role)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.role_combo)

        stats = QWidget()
        stats_layout = QHBoxLayout(stats)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        for item in TOP_STATS:
            stats_layout.addWidget(self._header_stat(item["title"], item["value"], item["accent"]))

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch(1)
        layout.addWidget(mode_box)
        layout.addWidget(stats)
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

    def _resource_path(self, relative_path: str) -> Path:
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / relative_path
        return Path(__file__).resolve().parent.parent / relative_path

    def _set_active_page(self, index: int) -> None:
        if not auth_service.has_permission(self.page_permissions[index]):
            QMessageBox.warning(self, "Права доступа", "Недостаточно прав для открытия раздела.")
            return
        self.stack.setCurrentIndex(index)
        if index == 0 and hasattr(self.dashboard_page, "refresh"):
            self.dashboard_page.refresh()
        current_page = self.stack.currentWidget()
        if hasattr(current_page, "refresh"):
            current_page.refresh()
        for button_index, button in enumerate(self.nav_buttons):
            is_active = button_index == index
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)
        print(f"Открыта страница: {self.nav_buttons[index].text()}")

    def _change_role(self, role: str) -> None:
        auth_service.set_role(role)
        self._apply_role_permissions()
        for index in range(self.stack.count()):
            page = self.stack.widget(index)
            if hasattr(page, "apply_role"):
                page.apply_role()
        print(f"Роль: {role}")

    def _apply_role_permissions(self) -> None:
        for button, permission in zip(self.nav_buttons, self.page_permissions):
            button.setEnabled(auth_service.has_permission(permission))
