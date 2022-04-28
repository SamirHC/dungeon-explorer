import dataclasses


@dataclasses.dataclass
class Statistic:
    value: int
    min_value: int
    max_value: int

    def increase(self, amount: int):
        self.value = min(self.value + amount, self.max_value)

    def reduce(self, amount: int):    
        self.value = max(self.min_value, self.value - amount)

    def set(self, result: int):
        self.value = max(self.min_value, min(result, self.max_value))
