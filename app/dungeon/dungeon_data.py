from dataclasses import dataclass

from app.dungeon.floor_data import FloorData


@dataclass
class DungeonData:
    dungeon_id: int
    name: str
    banner: str
    is_below: bool
    exp_enabled: bool
    recruiting_enabled: bool
    level_reset: bool
    money_reset: bool
    iq_enabled: bool
    reveal_traps: bool
    enemies_drop_boxes: bool
    max_rescue: int
    max_items: int
    max_party: int
    turn_limit: int
    floor_list: list[FloorData]

    @property
    def number_of_floors(self) -> int:
        return len(self.floor_list)
