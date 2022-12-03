import dataclasses
import enum

from app.model.statistic import Statistic


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


class DarknessLevel(enum.Enum):
    NO_DARKNESS = "NO_DARKNESS"
    LIGHT_DARKNESS = "LIGHT_DARKNESS"
    HEAVY_DARKNESS = "HEAVY_DARKNESS"


@dataclasses.dataclass
class DungeonStatus:
    darkness_level: DarknessLevel
    weather: Weather
    turns: Statistic
    mud_sport: Statistic = Statistic(0, 0, 11)
    water_sport: Statistic = Statistic(0, 0, 11)
    gravity: bool = False
