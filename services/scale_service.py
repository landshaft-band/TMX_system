import random


class ScaleService:
    def __init__(self) -> None:
        self.connected = False

    def connect(self) -> bool:
        self.connected = True
        return self.connected

    def simulate_weight(self, planned_weight: float) -> float:
        if planned_weight <= 0:
            planned_weight = 100.0

        if random.random() < 0.25:
            deviation_factor = random.choice([-1, 1]) * random.uniform(0.07, 0.14)
        else:
            deviation_factor = random.uniform(-0.025, 0.025)

        return round(planned_weight * (1 + deviation_factor), 2)
