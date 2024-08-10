import os

import pygame.mixer

from app.common.constants import SOUND_DIRECTORY


class SfxDatabase:
    def __init__(self):
        self.base_dir = os.path.join(SOUND_DIRECTORY, "sfx")
        self.loaded = {}

    def __getitem__(self, sfx_id: tuple[str, int]) -> pygame.mixer.Sound:
        if sfx_id not in self.loaded:
            self.load(sfx_id)
        return self.loaded[sfx_id]

    def load(self, sfx_id: tuple[str, int]):
        file_name = os.path.join(self.base_dir, sfx_id[0], f"{sfx_id[1]}.wav")
        self.loaded[sfx_id] = pygame.mixer.Sound(file_name)
