import dataclasses
import os
import xml.etree.ElementTree as ET
import pygame
import pygame.image
from app.pokemon import pokemon
from app.ground import groundmap


@dataclasses.dataclass
class GroundData:
    ground_map: groundmap.GroundMap
    event_triggers: list[tuple[str, pygame.Rect, int]]
    spawns: list[tuple[int, int]]
    npcs: list[pokemon.Pokemon]


class GroundSceneData:
    def __init__(self, scene_id: int, location: int=0):
        self.scene_id = scene_id
        self.location = location
        self.directory = os.path.join("data", "gamedata", "ground", str(self.scene_id))

        file = os.path.join(self.directory, f"ground_data{location}.xml")
        root = ET.parse(file).getroot()

        self.ground_data = get_ground_location_data(root)


def get_ground_location_data(root: ET.Element) -> GroundData:
    bg_id = root.find("Background").get("id")
    trigger_nodes = root.find("EventTriggers").findall("Trigger")
    triggers = []
    for n in trigger_nodes:
        trigger_type = n.get("class")
        rect = pygame.Rect(int(n.get("x")), int(n.get("y")), int(n.get("width")), int(n.get("height")))
        trigger_id = int(n.get("id"))
        triggers.append((trigger_type, rect, trigger_id))
    
    return GroundData(
        groundmap.db[bg_id],
        triggers,
        [(9*24, 8*24), (10*24, 8*24)],
        [pokemon.Pokemon(pokemon.PokemonBuilder(325).build_level(1))]
    )