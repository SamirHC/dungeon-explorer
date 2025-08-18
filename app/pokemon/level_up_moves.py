import bisect
import dataclasses


@dataclasses.dataclass(frozen=True)
class LevelUpMoves:
    levels: tuple[int]
    move_ids: tuple[int]

    def __post_init__(self):
        if len(self.levels) != len(self.move_ids):
            raise ValueError("levels and move_ids must have the same length")
        if any(
            self.levels[i] > self.levels[i + 1]
            for i in range(len(self.levels) - 1)
        ):
            raise ValueError("levels must be sorted ascending")

    def moves_for_level(self, level: int) -> tuple[int]:
        idx = bisect.bisect_right(self.levels, level)
        return self.move_ids[:idx]
