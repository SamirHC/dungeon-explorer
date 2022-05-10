import dataclasses
import os
import xml.etree.ElementTree as ET

import pygame
import pygame.image
from dungeon_explorer.common import direction
from dungeon_explorer.pokemon import portrait, shadow


@dataclasses.dataclass(frozen=True)
class SpriteSheet:
    name: str
    sprites: dict[direction.Direction, tuple[pygame.Surface, ...]]
    size: tuple[int, int]
    durations: tuple[int]

    @property
    def num_rows(self) -> int:
        return len(self.sprites)

    def __len__(self):
        return len(self.durations)

    def get_sprite(self, d: direction.Direction, index: int) -> pygame.Surface:
        if d not in self.sprites:
            d = direction.Direction.SOUTH
        return self.sprites[d][index]


@dataclasses.dataclass(frozen=True)
class SpriteCollection:
    sprite_sheets: dict[int, SpriteSheet]
    portraits: portrait.Portrait
    shadow_size: shadow.ShadowSize

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
        return self.sprite_collection.sprite_sheets[self.animation_id]

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
            frame_size = frame_w, frame_h = int(anim.find("FrameWidth").text), int(anim.find("FrameHeight").text)
            durations = tuple([int(d.text) for d in anim.find("Durations").findall("Duration")])
            
            anim_sheet = pygame.image.load(_get_file(f"{anim_name}-Anim.png"))
            if frame_h == anim_sheet.get_height():
                num_rows = 1
            else:
                num_rows = len(direction.Direction)
            sprites: dict[direction.Direction, tuple[pygame.Surface, ...]] = {}
            d = direction.Direction.SOUTH
            for row in range(num_rows):
                direction_sprites = []
                for i in range(len(durations)):
                    direction_sprite = anim_sheet.subsurface((frame_w*i, frame_h*row), frame_size)
                    direction_sprites.append(direction_sprite)
                sprites[d] = tuple(direction_sprites)
                d = d.anticlockwise()

            return SpriteSheet(anim_name, sprites, frame_size, durations)
        
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

        portraits = portrait.Portrait(dex)

        sprite_collection = SpriteCollection(
            sprite_sheets,
            portraits,
            shadow_size
        )
        self.loaded[dex] = sprite_collection


db = PokemonImageDatabase()
