import os
import pygame

from app.common.constants import IMAGES_DIRECTORY
from app.pokemon.portrait import PortraitSheet


class PortraitDatabase:
    def __init__(self):
        self.base_dir = os.path.join(IMAGES_DIRECTORY, "portrait")
        self.loaded: dict[int, PortraitSheet] = {}

    def __getitem__(self, dex: int) -> PortraitSheet:
        if dex not in self.loaded:
            self.load(dex)
        return self.loaded[dex]

    def load(self, dex: int):
        sheet_path = os.path.join(self.base_dir, str(dex), f"portrait_sheet{dex}.png")
        sheet = pygame.image.load(sheet_path)
        self.loaded[dex] = PortraitSheet(sheet)
