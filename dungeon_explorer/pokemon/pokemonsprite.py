import dataclasses
import os
import xml.etree.ElementTree as ET
from PIL import Image

import pygame
import pygame.image
from dungeon_explorer.common import constants, direction
from dungeon_explorer.pokemon import shadow
from dungeon_explorer.dungeon import colormap


@dataclasses.dataclass
class SpriteSheet:
    name: str
    sheet: pygame.Surface
    sprite_size: tuple[int, int]
    durations: tuple[int]
    colors: list[pygame.Color]
    is_singular: bool = dataclasses.field(init=False)
    row_directions: list[direction.Direction] = dataclasses.field(init=False)

    def __post_init__(self):
        self.is_singular = self.sheet.get_height() == self.sprite_size[1]
        self.row_directions = []
        d = direction.Direction.SOUTH
        num_rows = 1 if self.is_singular else 8
        for i in range(num_rows):
            self.row_directions.append(d)
            d = d.anticlockwise()

    def __len__(self):
        return len(self.durations)

    def get_row(self, d: direction.Direction):
        return self.row_directions.index(d)
    
    def get_position(self, d: direction.Direction, index: int) -> tuple[int, int]:
        w, h = self.sprite_size
        x = index * w
        y = self.get_row(d) * h
        return x, y

    def get_sprite(self, d: direction.Direction, index: int) -> pygame.Surface:
        if self.is_singular:
            d = direction.Direction.SOUTH
        pos = self.get_position(d, index)
        return self.sheet.subsurface(pos, self.sprite_size)

    def with_colormap(self, col_map: colormap.ColorMap):
        return SpriteSheet(
            self.name,
            col_map.transform_surface_colors(self.sheet, self.colors),
            self.sprite_size,
            self.durations,
            self.colors
        )


@dataclasses.dataclass(frozen=True)
class SpriteCollection:
    sprite_sheets: dict[int, SpriteSheet]
    shadow_size: shadow.ShadowSize

    def get_sprite(self, anim_id: int, direction: direction.Direction, index: int) -> pygame.Surface:
        sheet = self.sprite_sheets[anim_id]
        return sheet.get_sprite(direction, index)

    def with_colormap(self, col_map: colormap.ColorMap):
        return SpriteCollection(
            {i: sheet.with_colormap(col_map) for i, sheet in self.sprite_sheets.items()},
            self.shadow_size
        )


class PokemonSprite:
    WALK_ANIMATION_ID = 0
    HURT_ANIMATION_ID = 6
    IDLE_ANIMATION_ID = 7
    def __init__(self, sprite_collection: SpriteCollection):
        self.sprite_collection = sprite_collection
        self._direction = direction.Direction.SOUTH
        self._animation_id = self.IDLE_ANIMATION_ID
        self.timer = 0
        self.index = 0
        self.update_current_sprite()

    @property
    def direction(self) -> direction.Direction:
        return self._direction
    @direction.setter
    def direction(self, new_direction):
        if self.direction is new_direction:
            return
        self._direction = new_direction
        self.animation_id = self.IDLE_ANIMATION_ID
        self.timer = 0
        self.index = 0
        self.update_current_sprite()

    @property
    def animation_id(self) -> int:
        return self._animation_id
    @animation_id.setter
    def animation_id(self, new_anim_id: int):
        if new_anim_id == self._animation_id:
            return
        self._animation_id = new_anim_id
        self.timer = 0
        self.index = 0
        self.update_current_sprite()

    @property
    def current_sheet(self) -> SpriteSheet:
        return self.sprite_collection.sprite_sheets.get(self.animation_id, self.sprite_collection.sprite_sheets[0])

    def update_current_sprite(self):
        self.sprite_surface = self.current_sheet.get_sprite(self.direction, self.index)

    def update(self):
        self.timer += 1
        if self.timer < self.current_sheet.durations[self.index]:
            return
        self.timer = 0
        self.index += 1
        if self.index == len(self.current_sheet):
            self.animation_id = self.IDLE_ANIMATION_ID
            self.index = 0
        self.update_current_sprite()

    def render(self) -> pygame.Surface:
        return self.sprite_surface


class PokemonImageDatabase:
    def __init__(self):
        self.base_dir = os.path.join("assets", "images", "sprites")
        self.loaded: dict[int, SpriteCollection] = {}

    def __getitem__(self, dex: int) -> SpriteCollection:
        if dex not in self.loaded:
            self.load(dex)
        return self.loaded[dex]

    def load(self, dex: int):
        sprite_dir = os.path.join(self.base_dir, str(dex))

        def _get_file(filename):
            return os.path.join(sprite_dir, filename)            

        def _load_sprite_sheet(anim: ET.Element) -> SpriteSheet:
            anim_name = anim.find("Name").text
            filename = _get_file(f"{anim_name}-Anim.png")
            sheet = pygame.image.load(filename).convert_alpha()
            frame_size = int(anim.find("FrameWidth").text), int(anim.find("FrameHeight").text)
            durations = tuple([int(d.text) for d in anim.find("Durations").findall("Duration")])
            colors = [pygame.Color(c[1]) for c in Image.open(filename).convert("RGBA").getcolors() if c[1] != constants.TRANSPARENT]
            return SpriteSheet(anim_name, sheet, frame_size, durations, colors)
        
        anim_data_file = _get_file("AnimData.xml")
        anim_root = ET.parse(anim_data_file).getroot()

        shadow_size = shadow.ShadowSize(int(anim_root.find("ShadowSize").text))

        anims = anim_root.find("Anims").findall("Anim")
        sprite_sheets = {}
        for anim in anims:
            index_elem = anim.find("Index")
            if index_elem is None:
                continue
            index = int(index_elem.text)
            if anim.find("CopyOf") is not None:
                copy_anim_name = anim.find("CopyOf").text
                for anim_ in anims:
                    if anim_.find("Name").text == copy_anim_name:
                        anim = anim_
            sprite_sheets[index] = _load_sprite_sheet(anim)

        sprite_collection = SpriteCollection(
            sprite_sheets,
            shadow_size
        )
        self.loaded[dex] = sprite_collection


db = PokemonImageDatabase()
