import os
import xml.etree.ElementTree as ET

import pygame
import pygame.image
from dungeon_explorer.common import animation
from dungeon_explorer.dungeon import tile, dungeonstatus

WONDER_TILE_IMAGE = pygame.image.load(os.path.join("assets", "images", "traps", "WonderTile.png"))
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
    for i in res.items():
        print(i)
    return res


class Tileset:
    TILE_SET_DIR = os.path.join("assets", "images", "tilesets")
    tile_masks = get_tile_mask_to_position()

    def __init__(self, tileset_id: str):
        self.tileset_id = tileset_id
        base_dir = os.path.join(Tileset.TILE_SET_DIR, tileset_id)
        self.weather = dungeonstatus.Weather.CLEAR
        self.get_metadata(base_dir)
        self.get_tileset(base_dir)
        self.invalid_color = self[(5, 2), 0].get_at((0, 0))

    def get_metadata(self, base_dir: str):
        self.metadata = ET.parse(os.path.join(base_dir, "tileset.dtef.xml")).getroot()
        self.tile_size = int(self.metadata.get("dimensions"))
        animation_10_node, animation_11_node = self.metadata.findall("Animation")
        self.is_animated_10 = bool(list(animation_10_node))
        self.is_animated_11 = bool(list(animation_11_node))
        if self.is_animated_10:
            self.animation_10 = animation.PaletteAnimation(animation_10_node)
        if self.is_animated_11:
            self.animation_11 = animation.PaletteAnimation(animation_11_node)

        self.gamedata = ET.parse(os.path.join(base_dir, "tileset_data.xml")).getroot()
        self.primary_type = tile.Terrain(self.gamedata.find("PrimaryType").text)
        self.secondary_type = tile.Terrain(self.gamedata.find("SecondaryType").text)
        self.tertiary_type = tile.Terrain.GROUND
        self.minimap_color = self.get_minimap_color()
        self.underwater = bool(int(self.gamedata.find("Underwater").text))

    def get_tileset(self, base_dir):
        self._tileset: list[pygame.Surface] = []
        for i in range(3):
            self._tileset.append(pygame.image.load(os.path.join(base_dir, f"tileset_{i}.png")))

        self.weather_tileset = {}
        for w in dungeonstatus.Weather:
            self.weather_tileset[w] = [w.colormap().transform_surface(s) for s in self._tileset]
        
    @property
    def tileset(self) -> list[pygame.Surface]:
        return self.weather_tileset[self.weather]

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
        return self.tileset[v].subsurface((x*self.tile_size, y*self.tile_size), (self.tile_size, self.tile_size))

    def get_tile_position(self, tile_type: tile.TileType, pattern: tile.TileMask, variation: int=0) -> tuple[tuple[int, int], int]:
        return (self.get_position(tile_type, pattern), variation)

    def get_position(self, tile_type: tile.TileType, mask: tile.TileMask) -> tuple[int, int]:
        x, y = self.tile_masks[mask.value()]
        return (x + 6 * tile_type.value, y)

    def get_border_tile(self) -> pygame.Surface:
        return self[(1, 1), 0]

    def is_valid(self, tile_surface: pygame.Surface) -> bool:
        return tile_surface.get_at((0, 0)) != self.invalid_color

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
