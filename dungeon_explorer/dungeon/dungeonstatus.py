import dataclasses
import enum

from dungeon_explorer.dungeon import colormap
from dungeon_explorer.common.statistic import Statistic


class Structure(enum.Enum):
    SMALL = "SMALL"
    ONE_ROOM_MH = "ONE_ROOM_MH"
    RING = "RING"
    CROSSROADS = "CROSSROADS"
    TWO_ROOMS_MH = "TWO_ROOMS_MH"
    LINE = "LINE"
    CROSS = "CROSS"
    BEETLE = "BETTLE"
    OUTER_ROOMS = "OUTER_ROOMS"
    MEDIUM = "MEDIUM"
    SMALL_MEDIUM = "SMALL_MEDIUM"
    MEDIUM_LARGE = "MEDIUM_LARGE"
    MEDIUM_LARGE_12 = "MEDIUM_LARGE_12"
    MEDIUM_LARGE_13 = "MEDIUM_LARGE_13"
    MEDIUM_LARGE_14 = "MEDIUM_LARGE_14"
    MEDIUM_LARGE_15 = "MEDIUM_LARGE_15"


class Weather(enum.Enum):
    CLEAR = "CLEAR"
    FOG = "FOG"
    SUNNY = "SUNNY"
    CLOUDY = "CLOUDY"
    RAINY = "RAINY"
    SNOW = "SNOW"
    HAIL = "HAIL"
    SANDSTORM = "SANDSTORM"
    RANDOM = "RANDOM"

    def colormap(self):
        if self is Weather.CLEAR:
            return colormap.CLEAR_COLOR_MAP
        elif self is Weather.SUNNY:
            return colormap.SUNNY_COLOR_MAP
        elif self is Weather.SANDSTORM:
            return colormap.SANDSTORM_COLOR_MAP
        elif self is Weather.CLOUDY:
            return colormap.CLOUDY_COLOR_MAP
        elif self is Weather.RAINY:
            return colormap.RAINY_COLOR_MAP
        elif self is Weather.HAIL:
            return colormap.HAIL_COLOR_MAP
        elif self is Weather.FOG:
            return colormap.FOG_COLOR_MAP
        elif self is Weather.SNOW:
            return colormap.SNOW_COLOR_MAP
        else:
            return colormap.CLEAR_COLOR_MAP


class DarknessLevel(enum.Enum):
    NO_DARKNESS = "NO_DARKNESS"
    LIGHT_DARKNESS = "LIGHT_DARKNESS"
    HEAVY_DARKNESS = "HEAVY_DARKNESS"


@dataclasses.dataclass
class DungeonStatus:
    darkness_level: DarknessLevel
    weather: Weather
    turns: Statistic
