import os

import pygame
import pygame.image

from app.common.constants import IMAGES_DIRECTORY
from app.dungeon.trap import Trap


class TrapDatabase:
    def __init__(self):
        base_dir = os.path.join(IMAGES_DIRECTORY, "traps")
        self.trapset = {
            t: pygame.image.load(os.path.join(base_dir, f"{t.value}.png")) for t in Trap
        }

    def __getitem__(self, trap: Trap) -> pygame.Surface:
        return self.trapset[trap]
