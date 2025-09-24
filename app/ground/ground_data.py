from dataclasses import dataclass

import pygame

from app.pokemon.pokemon import Pokemon
from app.ground.ground_map import MapBackground


@dataclass
class EventTrigger:
    id: int
    event_class: str
    rect: pygame.Rect
    data: dict


@dataclass
class GroundData:
    ground_map: MapBackground
    event_triggers: list[EventTrigger]
    npcs: list[Pokemon]


@dataclass
class GroundSceneData:
    scene_id: int
    ground_data: GroundData
    location: int = 0
