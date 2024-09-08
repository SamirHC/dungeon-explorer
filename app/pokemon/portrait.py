import enum
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
    SURPRISED = 12
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
    FLIPPED_X_Y = (0, 160)

    def __init__(self, sheet: pygame.Surface):
        self.sheet = sheet
        self.is_symmetric = sheet.get_at(PortraitSheet.FLIPPED_X_Y).a == 0

    def get_portrait(self, emotion: PortraitEmotion, flipped=False) -> pygame.Surface:
        y, x = divmod(emotion.value, self.SHEET_WIDTH)
        if flipped and not self.is_symmetric:
            y += 4
        x *= self.SIZE
        y *= self.SIZE

        surface = self.sheet.subsurface((x, y), (self.SIZE, self.SIZE))
        if flipped and self.is_symmetric:
            surface = pygame.transform.flip(surface, flip_x=True, flip_y=False)
        return surface
