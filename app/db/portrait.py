import os

import pygame

from app.common.constants import IMAGES_DIRECTORY
from app.pokemon.portrait import PortraitSheet


base_dir = os.path.join(IMAGES_DIRECTORY, "portrait")


def load(dex: int) -> PortraitSheet:
    sheet_path = os.path.join(base_dir, str(dex), f"portrait_sheet{dex}.png")
    sheet = pygame.image.load(sheet_path)
    return PortraitSheet(sheet)
