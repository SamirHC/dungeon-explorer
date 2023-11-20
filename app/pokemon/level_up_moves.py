import dataclasses


@dataclasses.dataclass
class LevelUpMoves:
    levels: tuple[int]
    move_ids: tuple[int]

    def get_level_up_move_ids(self, level: int) -> list[int]:
        return [move_id for lv, move_id in zip(self.levels, self.move_ids) 
                        if lv <= level]