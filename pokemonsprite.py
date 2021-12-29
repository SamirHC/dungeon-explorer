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
        self.image_dict = self.pokemon_image_dict()

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

    def get_sprite_animation(self, name, dir):
        sprite_animation = []
        frame_width, frame_height = self.get_sprite_frame_size(name)
        row = self.get_direction_row(dir)
        sprites_per_animation = self.sprite_dict[name].get_width() // frame_width
        for i in range(sprites_per_animation):
            if self.sprite_dict[name].get_height() == frame_height * 8:
                individual_sprite = self.sprite_dict[name].subsurface(i*frame_width, row*frame_height, frame_width, frame_height)
                sprite_animation.append(individual_sprite)
        return sprite_animation
        
    def pokemon_image_dict(self):
        full_dict = {}

        for image_type in self.sprite_dict:  # ["Physical","Special","Walk","Hurt"]
            Dict = {}
            for d in direction.Direction:
                Dict[d] = self.get_sprite_animation(image_type, d)
            full_dict[image_type] = Dict
        return full_dict