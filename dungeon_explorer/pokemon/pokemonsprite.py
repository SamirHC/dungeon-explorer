from ..common import animation, direction
import dataclasses
import os
import pygame
import pygame.image
import xml.etree.ElementTree as ET


@dataclasses.dataclass
class SpriteSheet:
    name: str
    surface: pygame.Surface
    size: tuple[int, int]
    durations: list[int]


class SpriteCollection:
    SPRITE_DIRECTORY = os.path.join(os.getcwd(), "assets", "images", "sprites")

    def __init__(self, sprite_id: str):
        self.sprite_id = sprite_id
        self._directory = os.path.join(self.SPRITE_DIRECTORY, self.sprite_id)
        anim_data_root = self.get_anim_data()
        self.shadow_size = int(anim_data_root.find("ShadowSize").text)
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
            spritesheets[anim.find("Name").text] = self.get_spritesheet(anim)
        return spritesheets

    def get_spritesheet(self, anim: ET.Element) -> SpriteSheet:
        if anim.find("CopyOf") is not None:
            copy_anim = self.find_anim_by_name(anim.find("CopyOf").text)
            return self.get_spritesheet(copy_anim)
        name = anim.find("Name").text
        image = pygame.image.load(self.get_file(f"{name}-Anim.png"))
        size = (int(anim.find("FrameWidth").text), int(anim.find("FrameHeight").text))
        durations = [int(d.text) for d in anim.find("Durations").findall("Duration")]
        return SpriteSheet(name, image, size, durations)

    def find_anim_by_name(self, name) -> ET.Element:
        for anim in self.anim_data:
            if anim.find("Name").text == name:
                return anim

    def get_direction_row(self, d: direction.Direction) -> int:
        if d == direction.Direction.SOUTH: return 0
        if d == direction.Direction.SOUTH_EAST: return 1
        if d == direction.Direction.EAST: return 2
        if d == direction.Direction.NORTH_EAST: return 3
        if d == direction.Direction.NORTH: return 4
        if d == direction.Direction.NORTH_WEST: return 5
        if d == direction.Direction.WEST: return 6
        if d == direction.Direction.SOUTH_WEST: return 7

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
