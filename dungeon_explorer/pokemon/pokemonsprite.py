import dataclasses
import enum
import os
import xml.etree.ElementTree as ET

import pygame
import pygame.image
from dungeon_explorer.common import constants, direction
from dungeon_explorer.pokemon import portrait


class ShadowSize(enum.Enum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2

    def color(self) -> pygame.Color:
        if self is ShadowSize.SMALL: return pygame.Color(0, 255, 0)
        if self is ShadowSize.MEDIUM: return pygame.Color(255, 0, 0)
        if self is ShadowSize.LARGE: return pygame.Color(0, 0, 255)


@dataclasses.dataclass(frozen=True)
class SpriteSheet:
    name: str
    surface: pygame.Surface
    size: tuple[int, int]
    durations: tuple[int]
    shadow_surface: pygame.Surface

    @property
    def num_rows(self) -> int:
        return self.surface.get_height() // self.size[1]

    def __len__(self):
        return len(self.durations)

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        x, y = position
        w, h = self.size
        return self.surface.subsurface((x*w, y*h), self.size)

    def get_sprite(self, direction: direction.Direction, index: int) -> pygame.Surface:
        x = index
        y = self.get_row(direction)
        surface = pygame.Surface(self.size, pygame.SRCALPHA)
        sprite = self[x, y]
        shadow = self.get_shadow((x, y))
        surface.blit(shadow, (0, 0))
        surface.blit(sprite, (0, 0))
        return surface

    def get_shadow(self, position: tuple[int, int]) -> pygame.Surface:
        x, y = position
        w, h = self.size
        return self.shadow_surface.subsurface((x*w, y*h), self.size)
    
    def get_row(self, d: direction.Direction) -> int:
        if self.num_rows == 1:
            return 0
        if d is direction.Direction.SOUTH: return 0
        if d is direction.Direction.SOUTH_EAST: return 1
        if d is direction.Direction.EAST: return 2
        if d is direction.Direction.NORTH_EAST: return 3
        if d is direction.Direction.NORTH: return 4
        if d is direction.Direction.NORTH_WEST: return 5
        if d is direction.Direction.WEST: return 6
        if d is direction.Direction.SOUTH_WEST: return 7


@dataclasses.dataclass(frozen=True)
class SpriteCollection:
    sprite_sheets: dict[int, SpriteSheet]
    portraits: portrait.Portrait

    def get_sprite(self, anim_id: int, direction: direction.Direction, index: int) -> pygame.Surface:
        sheet = self.sprite_sheets[anim_id]
        return sheet.get_sprite(direction, index)


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
        self.sprite_surface = self.update_current_sprite()

    @property
    def direction(self) -> direction.Direction:
        return self._direction
    @direction.setter
    def direction(self, new_direction):
        if self.direction is new_direction:
            return
        self._direction = new_direction
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
        return self.sprite_collection.sprite_sheets[self.animation_id]

    def update_current_sprite(self) -> pygame.Surface:
        return self.current_sheet.get_sprite(self.direction, self.index)

    def update(self):
        self.timer += 1
        if self.timer < self.current_sheet.durations[self.index]:
            return
        self.timer = 0
        self.index += 1
        if self.index == len(self.current_sheet):
            self.animation_id = self.IDLE_ANIMATION_ID
            self.index = 0
        self.sprite_surface = self.update_current_sprite()

    def render(self):
        return self.sprite_surface


class PokemonImageDatabase:
    def __init__(self):
        self.base_dir = os.path.join("assets", "images", "sprites")
        self.loaded: dict[int, SpriteCollection] = {}

    def __getitem__(self, dex: int) -> SpriteCollection:
        if dex in self.loaded:
            return self.loaded[dex]
        self.load(dex)
        return self.loaded[dex]

    def load(self, dex: int):
        sprite_dir = os.path.join(self.base_dir, str(dex))

        def _get_file(filename):
            return os.path.join(sprite_dir, filename)

        def _load_shadow_sheet(path: str, shadow_size: ShadowSize) -> pygame.Surface:
            colors = pygame.PixelArray(pygame.image.load(path))
            colors.replace(constants.WHITE, constants.BLACK)
            colors.replace(ShadowSize.SMALL.color(), constants.BLACK)
            if shadow_size is ShadowSize.SMALL:
                colors.replace(ShadowSize.MEDIUM.color(), constants.TRANSPARENT)
                colors.replace(ShadowSize.LARGE.color(), constants.TRANSPARENT)
            elif shadow_size is ShadowSize.MEDIUM:
                colors.replace(ShadowSize.MEDIUM.color(), constants.BLACK)
                colors.replace(ShadowSize.LARGE.color(), constants.TRANSPARENT)
            elif shadow_size is ShadowSize.LARGE:
                colors.replace(ShadowSize.MEDIUM.color(), constants.BLACK)
                colors.replace(ShadowSize.LARGE.color(), constants.BLACK)
            return colors.make_surface()

        def _load_sprite_sheet(anim: ET.Element, shadow_size: ShadowSize) -> SpriteSheet:
            anim_name = anim.find("Name").text
            anim_sheet = pygame.image.load(_get_file(f"{anim_name}-Anim.png"))
            shadow_sheet = _load_shadow_sheet(_get_file(f"{anim_name}-Shadow.png"), shadow_size)
            frame_size = (int(anim.find("FrameWidth").text), int(anim.find("FrameHeight").text))
            durations = tuple([int(d.text) for d in anim.find("Durations").findall("Duration")])
            return SpriteSheet(anim_name, anim_sheet, frame_size, durations, shadow_sheet)
        
        anim_data_file = _get_file("AnimData.xml")
        anim_root = ET.parse(anim_data_file).getroot()

        shadow_size = ShadowSize(int(anim_root.find("ShadowSize").text))

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
            sprite_sheets[index] = _load_sprite_sheet(anim, shadow_size)

        portraits = portrait.Portrait(dex)

        sprite_collection = SpriteCollection(
            sprite_sheets,
            portraits
        )
        self.loaded[dex] = sprite_collection


db = PokemonImageDatabase()
