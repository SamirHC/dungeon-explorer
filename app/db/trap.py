import os

import pygame
import pygame.image

from app.common.constants import IMAGES_DIRECTORY
from app.dungeon.trap import Trap


base_dir = os.path.join(IMAGES_DIRECTORY, "traps")
trapset = {t: pygame.image.load(os.path.join(base_dir, f"{t.value}.png")) for t in Trap}


def load(trap: Trap) -> pygame.Surface:
    return trapset[trap]
