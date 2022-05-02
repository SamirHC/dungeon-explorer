import dataclasses
import enum
import os
import xml.etree.ElementTree as ET

import pygame
import pygame.image
from dungeon_explorer.common import animation, constants, direction
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

    def __len__(self):
        return len(self.durations)

    def __getitem__(self, position: tuple[int, int]) -> pygame.Surface:
        x, y = position
        w, h = self.size
        return self.surface.subsurface((x*w, y*h), self.size)

    def get_shadow(self, position: tuple[int, int]) -> pygame.Surface:
        x, y = position
        w, h = self.size
        return self.shadow_surface.subsurface((x*w, y*h), self.size)


class OldSpriteCollection:
    SPRITE_DIRECTORY = os.path.join("assets", "images", "sprites")

    def __init__(self, sprite_id: str):
        self.sprite_id = sprite_id
        self._directory = os.path.join(self.SPRITE_DIRECTORY, self.sprite_id)
        anim_data_root = self.get_anim_data()
        self.shadow_size = ShadowSize(int(anim_data_root.find("ShadowSize").text))
        self.anim_data = anim_data_root.find("Anims").findall("Anim")
        self.spritesheets = self.get_spritesheets()
        self.animations = self.load_animations()

    def get_file(self, name) -> str:
        return os.path.join(self._directory, name)

    def get_anim_data(self) -> ET.Element:
        return ET.parse(self.get_file("AnimData.xml")).getroot()

    def get_spritesheets(self) -> dict[int, SpriteSheet]:
        spritesheets = {}
        for anim in self.anim_data:
            index_elem = anim.find("Index")
            if index_elem is not None:
                i = int(index_elem.text)
                spritesheets[i] = self.load_spritesheet(anim)
        return spritesheets

    def load_spritesheet(self, anim: ET.Element) -> SpriteSheet:
        if anim.find("CopyOf") is not None:
            copy_anim = self.find_anim_by_name(anim.find("CopyOf").text)
            return self.load_spritesheet(copy_anim)
        name = anim.find("Name").text
        image = pygame.image.load(self.get_file(f"{name}-Anim.png"))
        size = (int(anim.find("FrameWidth").text), int(anim.find("FrameHeight").text))
        durations = tuple([int(d.text) for d in anim.find("Durations").findall("Duration")])
        shadow_surface = pygame.image.load(self.get_file(f"{name}-Shadow.png"))
        return SpriteSheet(name, image, size, durations, shadow_surface)

    def __getitem__(self, index: int) -> SpriteSheet:
        return self.spritesheets[index]

    def find_anim_by_name(self, name) -> ET.Element:
        for anim in self.anim_data:
            if anim.find("Name").text == name:
                return anim

    def get_direction_row(self, d: direction.Direction) -> int:
        if d is direction.Direction.SOUTH: return 0
        if d is direction.Direction.SOUTH_EAST: return 1
        if d is direction.Direction.EAST: return 2
        if d is direction.Direction.NORTH_EAST: return 3
        if d is direction.Direction.NORTH: return 4
        if d is direction.Direction.NORTH_WEST: return 5
        if d is direction.Direction.WEST: return 6
        if d is direction.Direction.SOUTH_WEST: return 7

    def load_specific_animation(self, sheet: SpriteSheet, d: direction.Direction) -> animation.Animation:
        frames = []
        w, h = sheet.size
        if sheet.surface.get_height() == h * 8:
            row = self.get_direction_row(d)
        else:
            row = 0
        for i in range(len(sheet.durations)):
            individual_sprite = sheet.surface.subsurface(i*w, row*h, w, h)
            frames.append(individual_sprite)
        return animation.Animation(frames, sheet.durations)

    def load_animations(self) -> dict[int, dict[direction.Direction, animation.Animation]]:
        animations = {}
        for i, sheet in self.spritesheets.items():
            directional_animations = {}
            for d in direction.Direction:
                directional_animations[d] = self.load_specific_animation(sheet, d)
            animations[i] = directional_animations
        return animations

    def get_animation(self, index: str, dir: direction.Direction) -> animation.Animation:
        return self.animations[index][dir]


class PokemonSprite:
    def __init__(self, sprite_id: str):
        self.sprite_collection = OldSpriteCollection(sprite_id)
        self.direction = direction.Direction.SOUTH
        self._animation_id = self.idle_animation_id()
        self.timer = 0
        self.index = 0

    def walk_animation_id(self):
        return 0

    def idle_animation_id(self):
        return 7

    def hurt_animation_id(self):
        return 6

    def update(self):
        self.timer += 1
        if self.timer == self.current_sheet.durations[self.index]:
            self.timer = 0
            self.index += 1
            if self.index == len(self.current_sheet):
                if self.animation_id != self.walk_animation_id():
                    self.animation_id = self.idle_animation_id()
                self.index = 0

    def get_position(self):
        is_directional = self.current_sheet.surface.get_height() == self.current_sheet.size[1]*8
        row = 0 if not is_directional else self.sprite_collection.get_direction_row(self.direction)
        return (self.index, row)

    @property
    def animation_id(self) -> int:
        return self._animation_id
    @animation_id.setter
    def animation_id(self, index: int):
        if index == self._animation_id:
            return
        self._animation_id = index
        self.timer = 0
        self.index = 0

    @property
    def size(self):
        return self.current_sheet.size

    @property
    def shadow_size(self) -> ShadowSize:
        return self.sprite_collection.shadow_size

    @property
    def current_sheet(self) -> SpriteSheet:
        return self.sprite_collection[self.animation_id]

    def render(self) -> pygame.Surface:
        return self.current_sheet[self.get_position()]

    def get_shadow(self) -> pygame.Surface:
        colors = pygame.PixelArray(self.current_sheet.get_shadow(self.get_position()))
        colors.replace(constants.WHITE, constants.BLACK)
        colors.replace(ShadowSize.SMALL.color(), constants.BLACK)
        if self.shadow_size is ShadowSize.SMALL:
            colors.replace(ShadowSize.MEDIUM.color(), constants.TRANSPARENT)
            colors.replace(ShadowSize.LARGE.color(), constants.TRANSPARENT)
        elif self.shadow_size is ShadowSize.MEDIUM:
            colors.replace(ShadowSize.MEDIUM.color(), constants.BLACK)
            colors.replace(ShadowSize.LARGE.color(), constants.TRANSPARENT)
        elif self.shadow_size is ShadowSize.LARGE:
            colors.replace(ShadowSize.MEDIUM.color(), constants.BLACK)
            colors.replace(ShadowSize.LARGE.color(), constants.BLACK)
        return colors.make_surface()


@dataclasses.dataclass(frozen=True)
class SpriteCollection:
    sprite_sheets: dict[int, SpriteSheet]
    portraits: portrait.Portrait


class PokemonImageDatabase:
    def __init__(self):
        self.base_dir = os.path.join("assets", "images", "sprites")
        self.loaded: dict[int, OldSpriteCollection] = {}

    def __getitem__(self, dex: int) -> OldSpriteCollection:
        if dex in self.loaded:
            return self.loaded[dex]
        self.load(dex)
        return self.loaded[dex]

    def load(self, dex: int):
        sprite_dir = os.path.join(self.base_dir, str(dex))

        def _get_file(filename):
            return os.path.join(sprite_dir, filename)

        def _load_sprite_sheet(anim: ET.Element) -> SpriteSheet:
            anim_name = anim.find("Name").text
            anim_sheet = pygame.image.load(_get_file(f"{anim_name}-Anim.png"))
            shadow_sheet = pygame.image.load(_get_file(f"{anim_name}-Shadow.png"))
            frame_size = (int(anim.find("FrameWidth").text), int(anim.find("FrameHeight").text))
            durations = tuple([int(d.text) for d in anim.find("Durations").findall("Duration")])
            return SpriteSheet(anim_name, anim_sheet, frame_size, durations, shadow_sheet)
        
        anim_data_file = _get_file("AnimData.xml")
        anim_root = ET.parse(anim_data_file).getroot()
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

        portraits = portrait.Portrait(dex)

        sprite_collection = SpriteCollection(
            sprite_sheets,
            portraits
        )
        self.loaded[dex] = sprite_collection


db = PokemonImageDatabase()
