from enum import Enum


class OrderStatus(str, Enum):
    CREATED = "Создан"
    PICKING = "В комплектации"
    PICKED = "Скомплектован"
    SHIPPING = "На отгрузке"
    SHIPPED = "Отгружен"
    CLOSED = "Закрыт"


class ShipmentStatus(str, Enum):
    DRAFT = "Черновик"
    FORMING = "Формируется"
    READY = "Готова к отгрузке"
    SHIPPED = "Отгружена"
    CLOSED = "Закрыта"
    EXPORTED = "Выгружена в 1С"
