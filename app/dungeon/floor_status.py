import dataclasses
from app.dungeon.darkness_level import DarknessLevel
from app.dungeon.weather import Weather
from app.model.statistic import Statistic


@dataclasses.dataclass
class FloorStatus:
    darkness_level: DarknessLevel
    weather: Weather
    mud_sport: Statistic = Statistic(0, 0, 11)
    water_sport: Statistic = Statistic(0, 0, 11)
    gravity: bool = False
