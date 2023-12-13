import dataclasses
from app.dungeon.darkness_level import DarknessLevel
from app.dungeon.weather import Weather
from app.model.bounded_int import BoundedInt


@dataclasses.dataclass
class FloorStatus:
    darkness_level: DarknessLevel
    weather: Weather
    mud_sport: BoundedInt = BoundedInt(0, 0, 11)
    water_sport: BoundedInt = BoundedInt(0, 0, 11)
    gravity: bool = False
