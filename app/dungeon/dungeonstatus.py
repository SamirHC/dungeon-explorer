import dataclasses
import enum

from app.model.statistic import Statistic


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
