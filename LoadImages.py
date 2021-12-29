import constants
import os
import pygame.image
import utils

def stats_dict():
    Dict = {}
    directory = os.path.join(os.getcwd(), "images", "MoveAnimations", "Stat Change")
    stats = [stat for stat in os.listdir(directory) if stat != "Thumbs.db"]
    for stat in stats:
        Dict[stat] = {
            "+": [pygame.image.load(os.path.join(directory, stat, "001", image)) for image in
                  os.listdir(os.path.join(directory, stat, "001")) if image != "Thumbs.db"][::-1],
            "-": [pygame.image.load(os.path.join(directory, stat, "000", image)) for image in
                  os.listdir(os.path.join(directory, stat, "000")) if image != "Thumbs.db"][::-1]
            }
    return Dict

stats_animation_dict = stats_dict()
