from enum import Enum


class DarknessLevel(Enum):
    NO_DARKNESS = "NO_DARKNESS"
    LIGHT_DARKNESS = "LIGHT_DARKNESS"
    HEAVY_DARKNESS = "HEAVY_DARKNESS"

    def get_visibility_radius(self) -> int:
        match self:
            case DarknessLevel.LIGHT_DARKNESS:
                return 2
            case DarknessLevel.HEAVY_DARKNESS:
                return 1
            case _:
                return 1000
