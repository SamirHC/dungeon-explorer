from ..common import animation, direction
import dataclasses
import enum
import os
import pygame
import pygame.image
import xml.etree.ElementTree as ET


class ShadowSize(enum.Enum):
    SMALL = 0
    MEDIUM = 1
    LARGE = 2

    def color(self) -> pygame.Color:
        if self is ShadowSize.SMALL: return pygame.Color(0, 255, 0)
        if self is ShadowSize.MEDIUM: return pygame.Color(255, 0, 0)
        if self is ShadowSize.LARGE: return pygame.Color(0, 0, 255)


@dataclasses.dataclass
class SpriteSheet:
    name: str
    surface: pygame.Surface
    size: tuple[int, int]
    durations: list[int]
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


class SpriteCollection:
    SPRITE_DIRECTORY = os.path.join(os.getcwd(), "assets", "images", "sprites")

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

    def get_spritesheets(self) -> dict[str, SpriteSheet]:
        spritesheets = {}
        for anim in self.anim_data:
            spritesheets[anim.find("Name").text] = self.load_spritesheet(anim)
        return spritesheets

    def load_spritesheet(self, anim: ET.Element) -> SpriteSheet:
        if anim.find("CopyOf") is not None:
            copy_anim = self.find_anim_by_name(anim.find("CopyOf").text)
            return self.load_spritesheet(copy_anim)
        name = anim.find("Name").text
        image = pygame.image.load(self.get_file(f"{name}-Anim.png"))
        size = (int(anim.find("FrameWidth").text), int(anim.find("FrameHeight").text))
        durations = [int(d.text) for d in anim.find("Durations").findall("Duration")]
        shadow_surface = pygame.image.load(self.get_file(f"{name}-Shadow.png"))
        return SpriteSheet(name, image, size, durations, shadow_surface)

    def __getitem__(self, name: str) -> SpriteSheet:
        return self.spritesheets[name]

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

    def load_specific_animation(self, name: str, d: direction.Direction) -> animation.Animation:
        frames = []
        sheet = self.spritesheets[name]
        w, h = sheet.size
        if sheet.surface.get_height() == h * 8:
            row = self.get_direction_row(d)
        else:
            row = 0
        for i in range(len(sheet.durations)):
            individual_sprite = sheet.surface.subsurface(i*w, row*h, w, h)
            frames.append(individual_sprite)
        return animation.Animation(list(zip(frames, sheet.durations)))

    def load_animations(self) -> dict[str, dict[direction.Direction, animation.Animation]]:
        animations = {}
        for animation_type in self.spritesheets:
            directional_animations = {}
            for d in direction.Direction:
                directional_animations[d] = self.load_specific_animation(
                    animation_type, d)
            animations[animation_type] = directional_animations
        return animations

    def get_animation(self, name: str, dir: direction.Direction) -> animation.Animation:
        return self.animations[name][dir]


class PokemonSprite:
    def __init__(self, sprite_id: str):
        self.sprite_collection = SpriteCollection(sprite_id)
        self.direction = direction.Direction.SOUTH
        self._animation_name = "Idle"
        self.timer = 0
        self.index = 0

    def update(self):
        self.timer += 1
        if self.timer == self.current_sheet.durations[self.index]:
            self.timer = 0
            self.index += 1
            if self.index == len(self.current_sheet):
                self.animation_name = "Idle"
                self.index = 0

    def get_position(self):
        is_directional = self.current_sheet.surface.get_height() == self.current_sheet.size[1]*8
        row = 0 if not is_directional else self.sprite_collection.get_direction_row(self.direction)
        return (self.index, row)

    @property
    def animation_name(self) -> str:
        return self._animation_name
    @animation_name.setter
    def animation_name(self, name: str):
        if name == self._animation_name:
            return
        self._animation_name = name
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
        return self.sprite_collection[self.animation_name]

    def render(self) -> pygame.Surface:
        return self.current_sheet[self.get_position()]

    def get_shadow(self) -> pygame.Surface:
        return self.current_sheet.get_shadow(self.get_position())