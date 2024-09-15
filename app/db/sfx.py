import os

import pygame.mixer

from app.common.constants import SOUND_DIRECTORY


base_dir = os.path.join(SOUND_DIRECTORY, "sfx")


def load(sfx_category: str, sfx_id) -> pygame.mixer.Sound:
    file_name = os.path.join(base_dir, sfx_category, f"{sfx_id}.wav")
    return pygame.mixer.Sound(file_name)
