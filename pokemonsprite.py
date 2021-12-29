import os
import pygame.image
import xml.etree.ElementTree as ET

class PokemonSprite:
    SPRITE_DIRECTORY = os.path.join(os.getcwd(), "assets", "sprites")

    def __init__(self, poke_id):
        self.poke_id = poke_id
        self.root = self.get_root()
        self.load_all_sprites()

    def get_root(self):
        directory = os.path.join(self.get_directory(), "AnimData.xml")
        tree = ET.parse(directory)
        return tree.getroot()

    def get_directory(self):
        return os.path.join(PokemonSprite.SPRITE_DIRECTORY, self.poke_id)

    def load_all_sprites(self):
        self.root = self.get_root()
        self.sprite_dict = {}
        for anim in self.root.find("Anims").findall("Anim"):
            name = anim.find("Name").text
            file_name = name + "-Anim.png"
            self.sprite_dict[name] = pygame.image.load(os.path.join(self.get_directory(), file_name))

    def get_sprite_frame_size(self, name):
        for anim in self.root.find("Anims").findall("Anim"):
            if anim.find("Name").text == name:
                width = anim.find("FrameWidth")
                height = anim.find("FrameHeight")
                return (width, height)

    def get_sprite_durations(self, name):
        for anim in self.root.find("Anims").findall("Anim"):
            if anim.find("Name").text == name:
                durations = []
                for d in anim.find("Durations").findall("Duration"):
                    durations.append(int(d.text))
                return durations

    def get_sprite(self, name, direction, frame):
        pass
