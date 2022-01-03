import animation
import direction
import os
import pygame
import pygame.image
import xml.etree.ElementTree as ET

class PokemonSprite:
    SPRITE_DIRECTORY = os.path.join(os.getcwd(), "assets", "sprites")

    def __init__(self, poke_id):
        self.poke_id = poke_id
        self.root = self.get_root()
        self.load_all_sprites()
        self.animations = self.load_animations()

    def get_root(self):
        directory = os.path.join(self.get_directory(), "AnimData.xml")
        tree = ET.parse(directory)
        return tree.getroot()

    def get_directory(self):
        return os.path.join(PokemonSprite.SPRITE_DIRECTORY, self.poke_id)

    def load_all_sprites(self):
        self.root = self.get_root()
        self.sprite_dict: dict[str, pygame.Surface] = {}
        for anim in self.root.find("Anims").findall("Anim"):
            name = anim.find("Name").text
            file_name = name + "-Anim.png"
            self.sprite_dict[name] = pygame.image.load(os.path.join(self.get_directory(), file_name))

    def get_sprite_frame_size(self, name):
        for anim in self.root.find("Anims").findall("Anim"):
            if anim.find("Name").text == name:
                width = int(anim.find("FrameWidth").text)
                height = int(anim.find("FrameHeight").text)
                return (width, height)

    def get_sprite_durations(self, name):
        for anim in self.root.find("Anims").findall("Anim"):
            if anim.find("Name").text == name:
                durations = []
                for d in anim.find("Durations").findall("Duration"):
                    durations.append(int(d.text))
                return durations

    def get_direction_row(self, dir):
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

    def load_specific_animation(self, name, dir) -> animation.Animation:
        a = animation.Animation()
        frames = []
        frame_width, frame_height = self.get_sprite_frame_size(name)
        row = self.get_direction_row(dir)
        sprites_per_animation = self.sprite_dict[name].get_width() // frame_width
        for i in range(sprites_per_animation):
            if self.sprite_dict[name].get_height() == frame_height * 8:
                individual_sprite = self.sprite_dict[name].subsurface(i*frame_width, row*frame_height, frame_width, frame_height)
                frames.append(individual_sprite)
        a.set_frames(frames)
        a.set_durations(self.get_sprite_durations(name))
        return a
        
    def load_animations(self) -> dict[str, dict[direction.Direction, animation.Animation]]:
        animations = {}

        for animation_type in self.sprite_dict:  # ["Physical","Special","Walk","Hurt"]
            directional_animations = {}
            for d in direction.Direction:
                directional_animations[d] = self.load_specific_animation(animation_type, d)
            animations[animation_type] = directional_animations
        return animations

    def get_animation(self, name: str, dir: direction.Direction) -> animation.Animation:
        return self.animations[name][dir]