from __future__ import annotations

import dataclasses
import os
import xml.etree.ElementTree as ET

import pygame
import pygame.image
from dungeon_explorer.common import animation
from dungeon_explorer.dungeon import tile, trap, colormap

STAIRS_DOWN_IMAGE = pygame.image.load(os.path.join("assets", "images", "stairs", "StairsDown.png"))
STAIRS_UP_IMAGE = pygame.image.load(os.path.join("assets", "images", "stairs", "StairsUp.png"))
SHOP_IMAGE = pygame.image.load(os.path.join("assets", "images", "traps", "KecleonCarpet.png"))

def get_tile_mask_to_position() -> dict[int, tuple[int, int]]:
    pattern_dir = os.path.join("assets", "images", "tilesets", "patterns.txt")
    res = {}
    with open(pattern_dir) as f:
        masks = f.read().splitlines()
    
    for i, mask in enumerate(masks):
        ns = [0]
        for j in range(8):
            if mask[j] == "1":
                ns = [(n << 1) + 1 for n in ns]
            elif mask[j] == "0":
                ns = [n << 1 for n in ns]
            elif mask[j] == "X":
                ns = [n << 1 for n in ns]
                ns += [n + 1 for n in ns]
            else:
                ns = []
                break
        for n in ns:
            res[n] = (i % 6, i // 6)
    return res

tile_masks = get_tile_mask_to_position()


@dataclasses.dataclass(frozen=True)
class Tileset:
    tileset_surfaces: tuple[pygame.Surface]
    tile_size: tuple[int, int]
    invalid_color: pygame.Color
    animation_10: animation.PaletteAnimation
    animation_11: animation.PaletteAnimation
    terrains: dict[tile.TileType, tile.Terrain]
    minimap_color: tile.TileType
    underwater: bool

    def get_terrain(self, tile_type: tile.TileType) -> tile.Terrain:
        return self.terrains[tile_type]

    def __getitem__(self, position: tuple[tuple[int, int], int]) -> pygame.Surface:
        (x, y), v = position
        if self.is_valid(position):
            return self.tileset_surfaces[v].subsurface((x*self.tile_size, y*self.tile_size), (self.tile_size, self.tile_size))
        return self.tileset_surfaces[0].subsurface((x*self.tile_size, y*self.tile_size), (self.tile_size, self.tile_size))

    def get_tile_position(self, tile_type: tile.TileType, pattern: tile.TileMask, variation: int=0) -> tuple[tuple[int, int], int]:
        return (self.get_position(tile_type, pattern), variation)

    def get_position(self, tile_type: tile.TileType, mask: tile.TileMask) -> tuple[int, int]:
        x, y = tile_masks[mask.value()]
        return (x + 6 * tile_type.value, y)

    def get_border_tile(self) -> pygame.Surface:
        return self[(1, 1), 0]

    def is_valid(self, position: tuple[tuple[int, int], int]) -> bool:
        (x, y), v = position
        if v == 0:
            return True
        topleft = (x*self.tile_size, y*self.tile_size)
        return self.tileset_surfaces[v].get_at(topleft) != self.invalid_color

    def update(self):
        if self.animation_10 is None and self.animation_11 is None:
            return
        updated = False
        if self.animation_10 is not None:
            updated = self.animation_10.update()
        if self.animation_11 is not None:
            updated |= self.animation_11.update()
        if not updated:
            return

        for surf in self.tileset_surfaces:
            if self.animation_10 is not None:
                palette = self.animation_10.current_palette()
                for i in range(16):
                    surf.set_palette_at(10*16+i, palette[i])
            if self.animation_11 is not None:
                palette = self.animation_11.current_palette()
                for i in range(16):
                    surf.set_palette_at(11*16+i, palette[i])

    def with_colormap(self, col_map: colormap.ColorMap) -> Tileset:
        tileset_surfaces = tuple([col_map.transform_surface(t) for t in self.tileset_surfaces])
        invalid_color = col_map.transform_color(self.invalid_color)
        animation_10 = col_map.transform_palette_animation(self.animation_10)
        animation_11 = col_map.transform_palette_animation(self.animation_11)
        return Tileset(
            tileset_surfaces,
            self.tile_size,
            invalid_color,
            animation_10,
            animation_11,
            self.terrains,
            self.minimap_color,
            self.underwater
        )


class TilesetDatabase:
    def __init__(self):
        self.base_dir = os.path.join("assets", "images", "tilesets")
        self.loaded: dict[int, Tileset] = {}

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
            colors = [[pygame.Color(f"#{color.text}") for color in palette] for palette in frames]
            durations = [int(el.get("duration")) for el in frames[0].findall("Color")]
            animation_10 = animation.PaletteAnimation(colors, durations)
        else:
            animation_10 = None

        is_animated_11 = bool(list(animation_11_node))
        if is_animated_11:
            frames = animation_11_node.findall("Frame")
            colors = [[pygame.Color(f"#{color.text}") for color in palette] for palette in frames]
            durations = [int(el.get("duration")) for el in frames[0].findall("Color")]
            animation_11 = animation.PaletteAnimation(colors, durations)
        else:
            animation_11 = None

        data_root = ET.parse(os.path.join(tileset_dir, "tileset_data.xml")).getroot()
        primary_type = tile.Terrain(data_root.find("PrimaryType").text)
        secondary_type = tile.Terrain(data_root.find("SecondaryType").text)
        tertiary_type = tile.Terrain.GROUND
        terrains = {
            tile.TileType.PRIMARY: primary_type,
            tile.TileType.SECONDARY: secondary_type,
            tile.TileType.TERTIARY: tertiary_type
        }
        minimap_color = pygame.Color("#"+data_root.find("MinimapColor").text)
        underwater = bool(int(data_root.find("Underwater").text))

        self.loaded[tileset_id] = Tileset(
            tileset_surfaces,
            tile_size,
            invalid_color,
            animation_10,
            animation_11,
            terrains,
            minimap_color,
            underwater
        )


db = TilesetDatabase()
