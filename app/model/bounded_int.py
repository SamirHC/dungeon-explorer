import dataclasses

from app.common import utils


@dataclasses.dataclass
class BoundedInt:
    value: int
    min_value: int
    max_value: int

    def set(self, result: int):
        self.value = utils.clamp(self.min_value, result, self.max_value)

    def add(self, delta: int):
        self.set(self.value + delta)

    def __eq__(self, __value: object) -> bool:
        return self.value == __value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.min_value} <= {self.value} <= {self.max_value}"
