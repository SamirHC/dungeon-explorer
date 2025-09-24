import os
import xml.etree.ElementTree as ET

import pygame

from app.common import constants


# Quiz Scene
def quiz_scene_background_animation():
    quiz_path = os.path.join(constants.IMAGES_DIRECTORY, "bg", "quiz")
    lower_bg_path = os.path.join(quiz_path, "lower.png")
    higher_bg_path = os.path.join(quiz_path, "higher.png")
    palette_data_path = os.path.join(quiz_path, "palette_data.xml")

    lower_bg = pygame.image.load(lower_bg_path)
    higher_bg = pygame.image.load(higher_bg_path)
    anim_root = ET.parse(palette_data_path).getroot()

    frames = [
        [pygame.Color(f"#{color.text}") for color in frame.findall("Color")]
        for frame in anim_root.findall("Frame")
    ]

    bg_t = 0
    frame_index = 0
    lower_x = 0
    higher_x = 0

    while True:
        # Update
        bg_t += 1
        if bg_t % 8 == 0:
            frame_index += 1
            frame_index %= len(frames)
            lower_bg.set_palette(frames[frame_index])
            higher_bg.set_palette(frames[frame_index])
        if bg_t % 2 == 0:
            lower_x += 1
            if lower_x == lower_bg.get_width():
                lower_x = 0
            higher_x -= 1
            if higher_x == -higher_bg.get_width():
                higher_x = 0

        # Render
        surface = pygame.Surface(constants.DISPLAY_SIZE)
        lower_layer = surface.copy()
        lower_layer.blit(lower_bg, (lower_x, 0))
        lower_layer.blit(lower_bg, (lower_x - lower_bg.get_width(), 0))
        upper_layer = surface.copy()
        upper_layer.blit(higher_bg, (higher_x, 0))
        upper_layer.blit(
            higher_bg, (higher_x + higher_bg.get_width(), 0)
        )
        surface.blit(
            pygame.transform.average_surfaces((lower_layer, upper_layer)),
            (0, 0),
        )
        yield surface
