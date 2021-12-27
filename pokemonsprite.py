import os
import xml.etree.ElementTree as ET

class PokemonSprite:
    SPRITE_DIRECTORY = os.path.join(os.getcwd(), "assets", "sprites")

    def __init__(self, poke_id):
        self.poke_id = poke_id
        self.root = self.get_root()
        self.load_all_sprites()

    def get_root(self):
        directory = os.path.join(PokemonSprite.SPRITE_DIRECTORY, self.poke_id, "AnimData.xml")
        tree = ET.parse(directory)
        return tree.getroot()

    def load_all_sprites(self):
        pass

