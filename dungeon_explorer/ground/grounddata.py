import dataclasses
import os
import xml.etree.ElementTree as ET
import pygame
import pygame.image
from dungeon_explorer.pokemon import pokemon


@dataclasses.dataclass
class GroundTile:
    collision: bool

@dataclasses.dataclass
class GroundData:
    bg: pygame.Surface
    tiles: dict[tuple[int, int], GroundTile]
    event_triggers: list[tuple[pygame.Rect, int]]
    spawns: list[tuple[int, int]]
    npcs: list[pokemon.Pokemon]


class GroundSceneData:
    def __init__(self, scene_id: int):
        self.scene_id = scene_id
        self.directory = os.path.join("data", "gamedata", "ground", str(self.scene_id))

        file = os.path.join(self.directory, f"ground_data{self.scene_id}.xml")
        root = ET.parse(file).getroot()

        self.ground_location_list = [get_ground_location_data(node) for node in root.findall("Place")]


def get_ground_location_data(root: ET.Element) -> GroundData:
    bg_id = root.find("Background").get("id")
    bg_class = root.find("Background").get("class")
    bg_base_dir = os.path.join("assets", "images", "bg", bg_class, bg_id)
    bg_dir = os.path.join(bg_base_dir, f"{bg_id}_LOWER.png")
    bg = pygame.image.load(bg_dir).convert_alpha()
    bg_width, bg_height = bg.get_size()
    map_width, map_height = bg_width // 8, bg_height // 8

    bg_data_dir = os.path.join(bg_base_dir, "grounddata.xml")
    bg_data_root = ET.parse(bg_data_dir).getroot()
    tile_nodes = bg_data_root.find("Tiles").findall("Tile")
    tiles = {(x, y): GroundTile(False) for x in range(map_width) for y in range(map_height)}
    for tile_node in tile_nodes:
        x = int(tile_node.get("x"))
        y = int(tile_node.get("y"))
        width = int(tile_node.get("width"))
        height = int(tile_node.get("height"))
        for i in range(width):
            for j in range(height):
                collision = tile_node.get("collision")
                if collision is not None:
                    tiles[x+i, y+j].collision = bool(int(collision))

    trigger_nodes = root.find("EventTriggers").findall("Trigger")
    triggers = []
    for n in trigger_nodes:
        rect = pygame.Rect(int(n.get("x")), int(n.get("y")), int(n.get("width")), int(n.get("height")))
        trigger_id = int(n.get("id"))
        triggers.append((rect, trigger_id))
    
    return GroundData(
        bg,
        tiles,
        triggers,
        [(9*24, 8*24), (10*24, 8*24)],
        [pokemon.Pokemon(pokemon.PokemonBuilder(420).build_level(1))]
    )