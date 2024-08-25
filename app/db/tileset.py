import os
import pygame
import xml.etree.ElementTree as ET

from app.dungeon.tile_type import TileType
from app.gui.tileset import Tileset
from app.common.constants import IMAGES_DIRECTORY
from app.model.palette_animation import PaletteAnimation
from app.dungeon.terrain import Terrain


class TilesetDatabase:
    def __init__(self):
        self.base_dir = os.path.join(IMAGES_DIRECTORY, "tilesets")
        self.loaded: dict[int, Tileset] = {}

        self.STAIRS_DOWN_IMAGE = pygame.image.load(
            os.path.join(IMAGES_DIRECTORY, "stairs", "StairsDown.png")
        )
        self.STAIRS_UP_IMAGE = pygame.image.load(
            os.path.join(IMAGES_DIRECTORY, "stairs", "StairsUp.png")
        )
        self.SHOP_IMAGE = pygame.image.load(
            os.path.join(IMAGES_DIRECTORY, "traps", "KecleonCarpet.png")
        )

    def __getitem__(self, tileset_id: int) -> Tileset:
        if tileset_id not in self.loaded:
            self.load(tileset_id)
        return self.loaded[tileset_id]

    def load(self, tileset_id: int):
        tileset_dir = os.path.join(self.base_dir, str(tileset_id))

        tileset_0 = pygame.image.load(os.path.join(tileset_dir, "tileset_0.png"))
        tileset_1 = pygame.image.load(os.path.join(tileset_dir, "tileset_1.png"))
        tileset_2 = pygame.image.load(os.path.join(tileset_dir, "tileset_2.png"))
        tileset_more = pygame.image.load(os.path.join(tileset_dir, "tileset_more.png"))
        tileset_surfaces = (tileset_0, tileset_1, tileset_2, tileset_more)

        dtef_root = ET.parse(os.path.join(tileset_dir, "tileset.dtef.xml")).getroot()
        tile_size = int(dtef_root.get("dimensions"))
        invalid_color = tileset_0.get_at((5 * tile_size, 2 * tile_size))

        animation_10_node, animation_11_node = dtef_root.findall("Animation")

        is_animated_10 = bool(list(animation_10_node))
        if is_animated_10:
            frames = animation_10_node.findall("Frame")
            colors = [
                [pygame.Color(f"#{color.text}") for color in palette]
                for palette in frames
            ]
            durations = [int(el.get("duration")) for el in frames[0].findall("Color")]
            animation_10 = PaletteAnimation(colors, durations)
        else:
            animation_10 = None

        is_animated_11 = bool(list(animation_11_node))
        if is_animated_11:
            frames = animation_11_node.findall("Frame")
            colors = [
                [pygame.Color(f"#{color.text}") for color in palette]
                for palette in frames
            ]
            durations = [int(el.get("duration")) for el in frames[0].findall("Color")]
            animation_11 = PaletteAnimation(colors, durations)
        else:
            animation_11 = None

        data_root = ET.parse(os.path.join(tileset_dir, "tileset_data.xml")).getroot()
        primary_type = Terrain(data_root.find("PrimaryType").text)
        secondary_type = Terrain(data_root.find("SecondaryType").text)
        tertiary_type = Terrain.GROUND
        terrains = {
            TileType.PRIMARY: primary_type,
            TileType.SECONDARY: secondary_type,
            TileType.TERTIARY: tertiary_type,
        }
        minimap_color = pygame.Color("#" + data_root.find("MinimapColor").text)
        underwater = bool(int(data_root.find("Underwater").text))

        self.loaded[tileset_id] = Tileset(
            tileset_surfaces,
            tile_size,
            invalid_color,
            animation_10,
            animation_11,
            terrains,
            minimap_color,
            underwater,
        )
