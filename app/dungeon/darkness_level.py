from enum import Enum


class DarknessLevel(Enum):
    NO_DARKNESS = "NO_DARKNESS"
    LIGHT_DARKNESS = "LIGHT_DARKNESS"
    HEAVY_DARKNESS = "HEAVY_DARKNESS"

    def get_visibility_size(self) -> int:
        match self:
            case DarknessLevel.LIGHT_DARKNESS:
                return 5
            case DarknessLevel.HEAVY_DARKNESS:
                return 3
            case _:
                return 0
