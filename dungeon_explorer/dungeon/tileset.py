import os
import xml.etree.ElementTree as ET

import pygame
import pygame.image
from dungeon_explorer.common import animation
from dungeon_explorer.dungeon import tile, dungeonstatus, trap

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


class Tileset:
    TILE_SET_DIR = os.path.join("assets", "images", "tilesets")
    tile_masks = get_tile_mask_to_position()

    def __init__(self, tileset_id: str):
        self.tileset_id = tileset_id
        base_dir = os.path.join(Tileset.TILE_SET_DIR, tileset_id)
        self._weather = None
        self.get_metadata(base_dir)
        self.load_tileset_surfaces(base_dir)
        self.set_tileset_weather(dungeonstatus.Weather.CLEAR)
        self.invalid_tile_position = ((5, 2), 0)

    def get_metadata(self, base_dir: str):
        self.metadata = ET.parse(os.path.join(base_dir, "tileset.dtef.xml")).getroot()
        self.tile_size = int(self.metadata.get("dimensions"))

        animation_10_node, animation_11_node = self.metadata.findall("Animation")

        self.is_animated_10 = bool(list(animation_10_node))
        if self.is_animated_10:
            frames = animation_10_node.findall("Frame")
            self.animation_10_original_colors = [[pygame.Color(f"#{color.text}") for color in palette] for palette in frames]
            colors = [[pygame.Color(f"#{color.text}") for color in palette] for palette in frames]
            durations = [int(el.get("duration")) for el in frames[0].findall("Color")]
            self.animation_10 = animation.PaletteAnimation(colors, durations)

        self.is_animated_11 = bool(list(animation_11_node))
        if self.is_animated_11:
            frames = animation_11_node.findall("Frame")
            self.animation_11_original_colors = [[pygame.Color(f"#{color.text}") for color in palette] for palette in frames]
            colors = [[pygame.Color(f"#{color.text}") for color in palette] for palette in frames]
            durations = [int(el.get("duration")) for el in frames[0].findall("Color")]
            self.animation_11 = animation.PaletteAnimation(colors, durations)

        self.gamedata = ET.parse(os.path.join(base_dir, "tileset_data.xml")).getroot()
        self.primary_type = tile.Terrain(self.gamedata.find("PrimaryType").text)
        self.secondary_type = tile.Terrain(self.gamedata.find("SecondaryType").text)
        self.tertiary_type = tile.Terrain.GROUND
        self.minimap_color = self.get_minimap_color()
        self.underwater = bool(int(self.gamedata.find("Underwater").text))

    def load_tileset_surfaces(self, base_dir):
        self.tileset_surfaces: list[pygame.Surface] = []
        for i in range(3):
            self.tileset_surfaces.append(pygame.image.load(os.path.join(base_dir, f"tileset_{i}.png")))
        self.trapset = trap.TrapTileset()

    @property
    def weather(self) -> dungeonstatus.Weather:
        return self._weather
    @weather.setter
    def weather(self, new_weather: dungeonstatus.Weather):
        if self._weather != new_weather:
            self._weather = new_weather
            self.set_tileset_weather(new_weather)
    
    def set_tileset_weather(self, weather: dungeonstatus.Weather):
        self.tileset = [weather.colormap().transform_surface(s) for s in self.tileset_surfaces]
        if self.is_animated_10:
            self.animation_10.frames = [[weather.colormap().transform_color(c) for c in palette] for palette in self.animation_10_original_colors]
        if self.is_animated_11:
            self.animation_11.frames = [[weather.colormap().transform_color(c) for c in palette] for palette in self.animation_11_original_colors]
        self.stairs_up_tile = weather.colormap().transform_surface(STAIRS_UP_IMAGE)
        self.stairs_down_tile = weather.colormap().transform_surface(STAIRS_DOWN_IMAGE)
        self.shop_tile = weather.colormap().transform_surface(SHOP_IMAGE)

    def get_terrain(self, tile_type: tile.TileType) -> tile.Terrain:
        if tile_type is tile.TileType.PRIMARY:
            return self.primary_type
        if tile_type is tile.TileType.SECONDARY:
            return self.secondary_type
        if tile_type is tile.TileType.TERTIARY:
            return self.tertiary_type

    def get_minimap_color(self) -> pygame.Color:
        hex = self.gamedata.find("MinimapColor").text
        return pygame.Color(f"#{hex}")

    def __getitem__(self, position: tuple[tuple[int, int], int]) -> pygame.Surface:
        (x, y), v = position
        if self.is_valid(position):
            tile = self.tileset[v].subsurface((x*self.tile_size, y*self.tile_size), (self.tile_size, self.tile_size))
            return tile
        default_tile = self.tileset[0].subsurface((x*self.tile_size, y*self.tile_size), (self.tile_size, self.tile_size))
        return default_tile

    def get_tile_position(self, tile_type: tile.TileType, pattern: tile.TileMask, variation: int=0) -> tuple[tuple[int, int], int]:
        return (self.get_position(tile_type, pattern), variation)

    def get_position(self, tile_type: tile.TileType, mask: tile.TileMask) -> tuple[int, int]:
        x, y = self.tile_masks[mask.value()]
        return (x + 6 * tile_type.value, y)

    def get_border_tile(self) -> pygame.Surface:
        return self[(1, 1), 0]

    def is_valid(self, position: tuple[tuple[int, int], int]) -> bool:
        (x, y), v = position
        if v == 0:
            return True
        topleft = (x*self.tile_size, y*self.tile_size)
        return self.tileset[v].get_at(topleft) != self[self.invalid_tile_position].get_at((0, 0))

    def update(self):
        if not (self.is_animated_10 or self.is_animated_11):
            return

        updated = False
        if self.is_animated_10:
            updated = self.animation_10.update()
        if self.is_animated_11:
            updated = self.animation_11.update() or updated
        if not updated:
            return

        for surf in self.tileset:
            if self.is_animated_10:
                palette = self.animation_10.current_palette()
                for i in range(16):
                    surf.set_palette_at(10*16+i, palette[i])
            if self.is_animated_11:
                palette = self.animation_11.current_palette()
                for i in range(16):
                    surf.set_palette_at(11*16+i, palette[i])
