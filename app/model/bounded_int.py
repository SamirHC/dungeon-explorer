import dataclasses

from app.common import utils


@dataclasses.dataclass
class BoundedInt:
    value: int
    min_value: int
    max_value: int

    def increase(self, amount: int):
        self.value = min(self.value + amount, self.max_value)

    def reduce(self, amount: int):
        self.value = max(self.min_value, self.value - amount)

    def set_value(self, result: int):
        self.value = utils.clamp(self.min_value, result, self.max_value)
