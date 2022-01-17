import animation
import direction
import os
import pygame
import pygame.image
import xml.etree.ElementTree as ET


class PokemonSprite:
    SPRITE_DIRECTORY = os.path.join(os.getcwd(), "assets", "sprites")

    def __init__(self, poke_id: str):
        self.poke_id = poke_id
        self.root = self.get_root()
        self.load_all_sprites()
        self.animations = self.load_animations()

    def get_root(self) -> ET.Element:
        directory = os.path.join(self.get_directory(), "AnimData.xml")
        tree = ET.parse(directory)
        return tree.getroot()

    def get_directory(self) -> str:
        return os.path.join(PokemonSprite.SPRITE_DIRECTORY, self.poke_id)

    def load_all_sprites(self):
        self.root = self.get_root()
        self.sprite_dict: dict[str, pygame.Surface] = {}
        for anim in self.root.find("Anims").findall("Anim"):
            name = anim.find("Name").text
            if anim.find("CopyOf") is None:
                file_name = f"{name}-Anim.png"
            else:
                copy_name = anim.find("CopyOf").text
                file_name = f"{copy_name}-Anim.png"
            self.sprite_dict[name] = pygame.image.load(
                os.path.join(self.get_directory(), file_name))

    def get_sprite_frame_size(self, name: str) -> tuple[int, int]:
        for anim in self.root.find("Anims").findall("Anim"):
            if anim.find("Name").text != name:
                continue
            if anim.find("CopyOf") is not None:
                return self.get_sprite_frame_size(anim.find("CopyOf").text)
            width = int(anim.find("FrameWidth").text)
            height = int(anim.find("FrameHeight").text)
            return (width, height)

    def get_sprite_durations(self, name: str) -> list[int]:
        for anim in self.root.find("Anims").findall("Anim"):
            if anim.find("Name").text != name:
                continue
            if anim.find("CopyOf") is not None:
                return self.get_sprite_durations(anim.find("CopyOf").text)
            durations = []
            for d in anim.find("Durations").findall("Duration"):
                durations.append(int(d.text))
            return durations

    def get_direction_row(self, dir: direction.Direction) -> int:
        direction_dict = {
            direction.Direction.SOUTH: 0,
            direction.Direction.SOUTH_EAST: 1,
            direction.Direction.EAST: 2,
            direction.Direction.NORTH_EAST: 3,
            direction.Direction.NORTH: 4,
            direction.Direction.NORTH_WEST: 5,
            direction.Direction.WEST: 6,
            direction.Direction.SOUTH_WEST: 7
        }
        return direction_dict[dir]

    def load_specific_animation(self, name: str, dir: direction.Direction) -> animation.Animation:
        frames = []
        w, h = self.get_sprite_frame_size(name)
        row = self.get_direction_row(dir)
        sprites_per_animation = self.sprite_dict[name].get_width() // w
        for i in range(sprites_per_animation):
            if self.sprite_dict[name].get_height() == h * 8:
                individual_sprite = self.sprite_dict[name].subsurface(
                    i*w, row*h, w, h)
                frames.append(individual_sprite)
        return animation.Animation(list(zip(frames, self.get_sprite_durations(name))))

    def load_animations(self) -> dict[str, dict[direction.Direction, animation.Animation]]:
        animations = {}

        # ["Physical","Special","Walk","Hurt"]
        for animation_type in self.sprite_dict:
            directional_animations = {}
            for d in direction.Direction:
                directional_animations[d] = self.load_specific_animation(
                    animation_type, d)
            animations[animation_type] = directional_animations
        return animations

    def get_animation(self, name: str, dir: direction.Direction) -> animation.Animation:
        return self.animations[name][dir]
