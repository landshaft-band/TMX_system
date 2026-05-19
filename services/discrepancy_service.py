def calculate_deviation(planned_weight: float, actual_weight: float) -> float:
    if planned_weight <= 0:
        return 0.0
    return round(abs(actual_weight - planned_weight) / planned_weight * 100, 2)


def check_package(planned_weight: float, actual_weight: float, tolerance_percent: float) -> dict[str, str | float]:
    deviation = calculate_deviation(planned_weight, actual_weight)
    if deviation <= tolerance_percent:
        return {
            "status": "Принято",
            "reason": "Отклонение в норме",
            "deviation": deviation,
        }

    direction = "выше" if actual_weight > planned_weight else "ниже"
    return {
        "status": "Расхождение",
        "reason": f"Вес {direction} допуска",
        "deviation": deviation,
    }
