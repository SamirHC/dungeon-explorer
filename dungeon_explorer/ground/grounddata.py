import dataclasses
import os
import xml.etree.ElementTree as ET
import pygame
import pygame.image
from dungeon_explorer.pokemon import pokemon


@dataclasses.dataclass
class GroundTile:
    collision: bool
    interaction_id: int
    next_ground_id: str


@dataclasses.dataclass
class GroundData:
    bg: pygame.Surface
    tiles: dict[tuple[int, int], GroundTile]
    spawns: list[tuple[int, int]]
    npcs: list[pokemon.Pokemon]


def get_ground_data(scene_id: int):
    base_dir = os.path.join("data", "gamedata", "ground")
    directory = os.path.join(base_dir, str(scene_id), f"{scene_id}.xml")

    root = ET.parse(directory).getroot()

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
    tiles = {(x, y): GroundTile(False, 0, 0) for x in range(map_width) for y in range(map_height)}
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
                next_ground_id = tile_node.get("next_ground_id")
                if next_ground_id is not None:
                    tiles[x+i, y+j].next_ground_id = next_ground_id
    
    return GroundData(
        bg,
        tiles,
        [(9*24, 8*24), (10*24, 8*24)],
        [pokemon.Pokemon(pokemon.PokemonBuilder(420).build_level(1))]
    )