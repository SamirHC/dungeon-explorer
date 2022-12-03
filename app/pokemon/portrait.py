import enum
import os

import pygame
import pygame.image


class PortraitEmotion(enum.Enum):
    NORMAL = 0
    HAPPY = 1
    PAIN = 2
    ANGRY = 3
    WORRIED = 4
    SAD = 5
    CRYING = 6
    SHOUTING = 7
    TEARY_EYED = 8
    DETERMINED = 9
    JOYOUS = 10
    INSPIRED = 11
    SURPRISD = 12
    DIZZY = 13
    SPECIAL_0 = 14
    SPECIAL_1 = 15
    SIGH = 16
    STUNNED = 17
    SPECIAL_2 = 18
    SPECIAL_3 = 19


class PortraitSheet:
    SIZE = 40
    SHEET_WIDTH = 5
    def __init__(self, sheet: pygame.Surface):
        self.sheet = sheet
        
    def get_portrait_position(self, emotion: PortraitEmotion, flipped=False) -> tuple[int, int]:
        y, x = divmod(emotion.value, self.SHEET_WIDTH)
        if flipped:
            y += 4
        x *= self.SIZE
        y *= self.SIZE
        return x, y
    
    def get_portrait(self, emotion: PortraitEmotion, flipped=False) -> pygame.Surface:
        position = self.get_portrait_position(emotion, flipped)
        size = (self.SIZE, self.SIZE)
        return self.sheet.subsurface(position, size)


class PortraitDatabase:
    def __init__(self):
        self.base_dir = os.path.join("assets", "images", "portrait")
        self.loaded: dict[int, PortraitSheet] = {}

    def __getitem__(self, dex: int) -> PortraitSheet:
        if dex not in self.loaded:
            self.load(dex)
        return self.loaded[dex]

    def load(self, dex: int):
        sheet_path = os.path.join(self.base_dir, str(dex), f"portrait_sheet{dex}.png")
        sheet = pygame.image.load(sheet_path)
        self.loaded[dex] = PortraitSheet(sheet)


db = PortraitDatabase()