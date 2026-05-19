from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QWidget

from data.mock_data import USERS
from ui.components import group_box, make_button, make_table, page_shell, title_label


class UsersPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        page, layout = page_shell()
        root = QGridLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(page)

        layout.addWidget(title_label("Пользователи"))
        layout.addWidget(make_table(["ФИО", "Роль", "Email", "Статус"], USERS, min_height=280))

        actions_box, actions_layout = group_box("Действия с пользователями")
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(make_button("Добавить пользователя", "Открытие формы добавления пользователя"))
        row_layout.addWidget(make_button("Изменить роль", "Открытие формы изменения роли"))
        row_layout.addWidget(make_button("Заблокировать", "Пользователь заблокирован в прототипе"))
        row_layout.addStretch(1)
        actions_layout.addWidget(row)
        layout.addWidget(actions_box)
        layout.addStretch(1)
