import dataclasses
import os
import xml.etree.ElementTree as ET
import pygame
import pygame.image
from app.pokemon import pokemon
from app.ground import groundmap
from app.db import groundmap_db

"""
The story is a sequence of scenes. Each scene is made up of a collection of
ground locations, each making use of different events and npcs.

We need to know what the current scene is, as well as the location in order to
fetch the information from storage.
"""
class EventTrigger:
    def __init__(self, node: ET.Element):
        self.data = {k:node.get(k) for k in node.keys()}
        self.event_class = node.get("class")
        self.id = int(node.get("id"))
        self.rect = pygame.Rect(
            int(node.get("x")),
            int(node.get("y")),
            int(node.get("w")),
            int(node.get("h"))
        )

@dataclasses.dataclass
class GroundData:
    ground_map: groundmap.GroundMap
    event_triggers: list[EventTrigger]
    npcs: list[pokemon.Pokemon]


class GroundSceneData:
    def __init__(self, scene_id: int, location: int=0):
        self.scene_id = scene_id
        self.location = location
        self.directory = os.path.join("data", "gamedata", "ground", str(self.scene_id))

        file = os.path.join(self.directory, f"ground_data{location}.xml")
        self.root = ET.parse(file).getroot()

        self.ground_data = get_ground_location_data(self.root)

    def reload(self):
        self.ground_data = get_ground_location_data(self.root)


def get_ground_location_data(root: ET.Element) -> GroundData:
    bg_id = root.find("Background").get("id")
    triggers = list(map(
        EventTrigger,
        root.find("EventTriggers").findall("Trigger")
    ))
    return GroundData(
        groundmap_db.load(bg_id),
        triggers,
        []  # [pokemon.Pokemon(pokemon.PokemonBuilder(325).build_level(1))]
    )
